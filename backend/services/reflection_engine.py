import re
from typing import Any, Dict, List, Optional, Tuple
from backend.models.ai import ReflectionResponse
from backend.services.ai.ai_service import AIService, get_ai_service
from backend.services.memory_service import MemoryService
from backend.services.retrieval_service import RetrievalResult, RetrievalService

# Harm and crisis keyword patterns for immediate safety interception
SAFETY_PATTERNS = [
    r"\b(kill myself|commit suicide|end my life|want to die|harm myself|cutting myself)\b",
    r"\b(he hit me|she hit me|physically abusive|threatened to kill|fear for my life)\b",
    r"\b(suicidal thoughts|overdose on pills)\b",
]

# Phrases asserting past statements that MUST have an explicit [M#] citation
HISTORICAL_CLAIM_PATTERNS = [
    r"\byou (previously|already|once|then|also)?\s*(said|wrote|noted|felt|stated|mentioned|decided|expressed|shared|described)\b",
    r"\byou told me\b",
    r"\bin (the|your) past (you\b|\bentry|\bjournal|\brecord)",
    r"\b(in your|your) past (entry|record|journal|memory|note)\b",
    r"\b(past|earlier) (entry|journal|memory|note) (shows|states|said|noted|stated)\b",
]

CRISIS_RESPONSE = (
    "Anchor is a local reflection companion, not a therapist, medical provider, or crisis service. "
    "If you are experiencing thoughts of self-harm, are in danger, or need immediate support, "
    "please reach out to a trusted person, medical professional, or local emergency services right away. "
    "In the US and Canada, you can call or text 988 (Suicide & Crisis Lifeline). "
    "In the UK, call 111 or 999. In international regions, contact your local emergency response."
)

INSUFFICIENT_CONTEXT_MSG = "I couldn't find anything in your saved memories that directly answers this."

class ReflectionEngine:
    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        ai_service: Optional[AIService] = None,
    ):
        self.ai_service = ai_service or get_ai_service()
        self.retrieval_service = retrieval_service or RetrievalService(ai_service=self.ai_service)


    def check_safety(self, text: str) -> bool:
        """Returns True if input indicates potential safety emergency or self-harm."""
        t = text.lower()
        for pat in SAFETY_PATTERNS:
            if re.search(pat, t):
                return True
        return False

    def validate_citations(
        self, text: str, max_valid_id: int
    ) -> Tuple[bool, List[int], Optional[str]]:
        """Strict server-side validation:
        1. All cited [M#] tokens must be within 1 <= # <= max_valid_id.
        2. Any historical assertion ("you previously wrote", "you told me", etc.)
           must be in a sentence containing a valid citation token.
        """
        # Find all cited IDs
        cited_matches = re.findall(r"\[M(\d+)\]", text)
        cited_ids = [int(m) for m in cited_matches]

        # 1. Check for hallucinated citation numbers
        for cid in cited_ids:
            if cid < 1 or cid > max_valid_id:
                return False, [], f"Cited non-existent memory [M{cid}]."

        # 2. Check for uncited historical assertions
        sentences = re.split(r"[.!?\n]+", text)
        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            has_citation = bool(re.search(r"\[M\d+\]", s_clean))
            for pat in HISTORICAL_CLAIM_PATTERNS:
                if re.search(pat, s_clean, re.IGNORECASE) and not has_citation:
                    return False, [], f"Uncited historical claim detected: '{s_clean}'"

        return True, cited_ids, None

    def build_deterministic_template(
        self, query: str, retrieved: List[RetrievalResult]
    ) -> str:
        """Deterministic response built strictly from retrieved memory text without LLM drift."""
        if not retrieved:
            return INSUFFICIENT_CONTEXT_MSG

        top_m = retrieved[0].memory
        lines = [
            f"You mentioned something similar before [M1]. You previously recorded ({top_m.type.value}): \"{top_m.content}\""
        ]

        if len(retrieved) > 1:
            second_m = retrieved[1].memory
            lines.append(
                f"You also recorded in [M2] ({second_m.type.value}): \"{second_m.content}\""
            )

        lines.append("I am not assuming the situation is the same now.")
        lines.append("What feels different this time?")
        return "\n\n".join(lines)

    def extract_reflective_question(self, text: str) -> Optional[str]:
        """Extracts the final reflective question from response if present."""
        questions = re.findall(r"([A-Z][^\.!\?]*\?)", text)
        return questions[-1].strip() if questions else "What feels different this time?"

    def reflect(self, query: str, top_k: int = 5, filter_person: Optional[str] = None) -> ReflectionResponse:
        # 1. Safety Check
        if self.check_safety(query):
            return ReflectionResponse(
                answer=CRISIS_RESPONSE,
                sources=[],
                source_details=[],
                status="safety_warning",
            )

        # 2. Semantic Retrieval
        retrieved = self.retrieval_service.search_memories(
            query=query,
            top_k=top_k,
            min_similarity=0.36,
            include_suggested=False,
        )

        if not retrieved:
            return ReflectionResponse(
                answer=INSUFFICIENT_CONTEXT_MSG,
                sources=[],
                source_details=[],
                status="insufficient_context",
            )

        # Build source details mapping
        source_details = []
        for idx, r in enumerate(retrieved):
            m = r.memory
            source_details.append({
                "citation": f"[M{idx + 1}]",
                "memory_id": m.id,
                "type": m.type.value,
                "title": m.title or f"{m.type.value} memory",
                "content": m.content,
                "date": m.created_at[:10],
                "similarity": r.semantic_sim,
                "importance": m.importance.value,
            })

        sources_ids = [r.memory.id for r in retrieved]

        # 3. If AI is offline, immediately return deterministic template fallback
        ai_status = self.ai_service.get_status()
        if not ai_status.ready:
            template_ans = self.build_deterministic_template(query, retrieved)
            return ReflectionResponse(
                answer=template_ans,
                sources=sources_ids,
                source_details=source_details,
                reflective_question=self.extract_reflective_question(template_ans),
                status="fallback_template",
                why_seeing_this="Generated from local verified memory records while AI runtime is offline.",
            )

        # 4. Construct Prompt with Numbered Memories [M1]..[Mn]
        memory_context_blocks = []
        for idx, r in enumerate(retrieved):
            m = r.memory
            block = (
                f"[M{idx + 1}] Date: {m.created_at[:10]} | Type: {m.type.value}\n"
                f"Content: {m.content}"
            )
            memory_context_blocks.append(block)

        context_str = "\n\n".join(memory_context_blocks)
        max_valid_id = len(retrieved)

        system_prompt = (
            "You are Anchor, a local-first memory and reflection companion.\n"
            "Principle: The AI remembers. The human decides.\n"
            "Rules:\n"
            "1. You must ONLY cite provided numbered memories: [M1] to [M" + str(max_valid_id) + "].\n"
            "2. ANY historical statement about what the user wrote, felt, decided, or experienced MUST have an explicit [M#] citation.\n"
            "3. NEVER fabricate or assume past events not explicitly in [M1]-[M" + str(max_valid_id) + "].\n"
            "4. NEVER tell the user what to do, diagnose them or others, or use labels like 'toxic', 'narcissist', or therapy jargon.\n"
            "5. Structure: (1) Relevant past context with [M#] citations, (2) Similarities, (3) Differences or uncertainty, (4) Exactly ONE reflective question.\n"
            "Tone: calm, neutral, mature, concise."
        )

        user_prompt = (
            f"User statement: \"{query}\"\n\n"
            f"Available memories:\n{context_str}\n\n"
            "Provide your reflection following all rules:"
        )

        # 5. Generation with Two-Try Server-Side Anti-Fabrication Validation
        attempts = 0
        final_answer = None
        while attempts < 2:
            attempts += 1
            try:
                raw_response = self.ai_service.generate(
                    prompt=user_prompt,
                    system=system_prompt,
                    temperature=0.2,
                )
                valid, cited_ids, reason = self.validate_citations(raw_response, max_valid_id)
                if valid:
                    final_answer = raw_response
                    break
            except Exception:
                break

        # 6. Fallback if validation failed twice or generation errored
        if not final_answer:
            final_answer = self.build_deterministic_template(query, retrieved)
            resp_status = "fallback_template"
        else:
            resp_status = "ok"

        return ReflectionResponse(
            answer=final_answer,
            sources=sources_ids,
            source_details=source_details,
            reflective_question=self.extract_reflective_question(final_answer),
            status=resp_status,
            why_seeing_this=f"Retrieved {len(retrieved)} confirmed past memories based on semantic relevance and importance.",
        )
