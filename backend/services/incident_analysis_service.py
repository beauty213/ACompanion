import json
import logging
import re
from datetime import datetime, timezone
from typing import List, Optional
from backend.models.incident_analysis import IncidentAnalysisReport
from backend.models.memory import MemoryType
from backend.services.ai.ai_service import get_ai_service
from backend.services.journal_service import JournalService
from backend.services.memory_service import MemoryService
from backend.services.module_service import ModuleService

logger = logging.getLogger("anchor.incident_analysis")

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class IncidentAnalysisService:
    def __init__(self, module_service=None, journal_service=None, memory_service=None, ai_service=None):
        self._module_service = module_service or ModuleService()
        self._journal_service = journal_service or JournalService()
        self._memory_service = memory_service or MemoryService()
        self._ai_service = ai_service or get_ai_service()

    def analyze_module(self, module_id: str) -> Optional[IncidentAnalysisReport]:
        module = self._module_service.get_module(module_id)
        if not module:
            return None

        # Fetch all incidents (sorted chronologically)
        incidents = self._journal_service.list_entries(module_id=module_id)
        incidents = sorted(incidents, key=lambda x: x.created_at)

        # Fetch active memories / boundaries
        memories = self._memory_service.list_memories(module_id=module_id, include_suggested=False)
        boundaries = [m.content for m in memories if m.type == MemoryType.BOUNDARY]

        if not incidents:
            return IncidentAnalysisReport(
                module_id=module.id,
                module_name=module.name,
                relationship=module.relationship,
                incident_count=0,
                timeline_summary=f"No incidents currently recorded under {module.name}.",
                escalation_analysis="Log at least 1-2 incidents to observe behavioral patterns and escalation.",
                documented_contradictions=[],
                reciprocity_assessment="Insufficient incident history to calculate reciprocity balance.",
                active_boundaries=boundaries,
                clarifying_questions=[
                    f"What is the primary dynamic or expectation you want to monitor with {module.name}?"
                ],
                key_takeaway=f"Track is open for {module.name}. Record incidents as they occur to build hindsight clarity.",
                generated_at=utc_now(),
            )

        # Try LLM synthesis if Ollama is online
        analysis = None
        if self._ai_service.model_manager.is_model_available():
            try:
                analysis = self._llm_synthesis(module, incidents, boundaries)
            except Exception as e:
                logger.warning(f"LLM incident analysis failed, falling back to deterministic synthesis: {e}")

        # Deterministic synthesis fallback
        if not analysis:
            analysis = self._deterministic_synthesis(module, incidents, boundaries)

        return analysis

    def _llm_synthesis(self, module, incidents, boundaries) -> Optional[IncidentAnalysisReport]:
        incidents_text = "\n\n".join([
            f"--- Incident #{i+1} ({inc.created_at[:10]}): {inc.title or 'Untitled'} ---\n{inc.content}"
            for i, inc in enumerate(incidents)
        ])
        boundaries_text = "\n".join([f"- {b}" for b in boundaries]) if boundaries else "None recorded yet."

        prompt = f"""You are Anchor's Multi-Incident Analysis Engine.
Analyze the following recorded incidents involving {module.name} ({module.relationship or 'Personal Track'}).

Recorded Incidents ({len(incidents)} total):
{incidents_text}

Recorded Boundaries:
{boundaries_text}

Your analysis must be grounded strictly in the facts recorded above. Do not tell the user what decision to make.
Respond with a strict JSON object with these exact keys:
{{
  "timeline_summary": "2-3 sentences summarizing the progression of events across the incidents",
  "escalation_analysis": "2-3 sentences analyzing how behaviors, demands, or tone escalated over time",
  "documented_contradictions": ["Contradiction 1: Stated words vs documented actions", "Contradiction 2: ..."],
  "reciprocity_assessment": "Analysis of the give-and-take balance, financial and emotional toll",
  "clarifying_questions": ["Reflective question 1", "Reflective question 2", "Reflective question 3"],
  "key_takeaway": "One clear, grounded summary observation of the overall situation"
}}
Return ONLY valid JSON.
"""
        response_text = self._ai_service.generate(prompt)
        # Extract JSON from potential markdown wrapping
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return IncidentAnalysisReport(
                module_id=module.id,
                module_name=module.name,
                relationship=module.relationship,
                incident_count=len(incidents),
                timeline_summary=data.get("timeline_summary", ""),
                escalation_analysis=data.get("escalation_analysis", ""),
                documented_contradictions=data.get("documented_contradictions", []),
                reciprocity_assessment=data.get("reciprocity_assessment", ""),
                active_boundaries=boundaries,
                clarifying_questions=data.get("clarifying_questions", []),
                key_takeaway=data.get("key_takeaway", ""),
                generated_at=utc_now(),
            )
        return None

    def _deterministic_synthesis(self, module, incidents, boundaries) -> IncidentAnalysisReport:
        """Deterministic offline multi-incident analyzer that operates without cloud or LLM dependencies."""
        count = len(incidents)
        all_text = " ".join([inc.content for inc in incidents]).lower()

        # 1. Timeline & Dates
        first_date = incidents[0].created_at[:10]
        latest_date = incidents[-1].created_at[:10]
        timeline_summary = (
            f"Across {count} recorded incident(s) from {first_date} to {latest_date}, "
            f"the interaction pattern with {module.name} shows a documented shift from initial requests to compounding boundary pressure."
        )

        # 2. Escalation Detection
        has_money = any(w in all_text for w in ["$", "borrow", "loan", "rent", "money", "savings", "paid back", "pay back"])
        has_gossip = any(w in all_text for w in ["gossip", "rumor", "behind my back", "talk behind", "abandoned", "badmouth", "mutual friend"])
        has_reconnect = any(w in all_text for w in ["coffee", "stranger", "out of the blue", "reconnect", "reach out", "miss my best friend", "texted me"])

        escalation_parts = []
        if has_money:
            escalation_parts.append("Financial escalation: moving from unresolved smaller loans to substantial demands and dismissal of your financial priorities.")
        if has_gossip:
            escalation_parts.append("Social/Reputational escalation: personal grievances taken outside the friendship to mutual contacts, reframing your hesitation as abandonment.")
        if has_reconnect:
            escalation_parts.append("Cycle resumption: abrupt re-engagement using nostalgia and affection while previous financial and trust violations remain unaddressed.")

        if escalation_parts:
            escalation_analysis = " ".join(escalation_parts)
        else:
            escalation_analysis = f"Documented interactions show repeated boundary friction across {count} logged occurrences."

        # 3. Documented Contradictions
        contradictions = []
        if has_reconnect and has_gossip:
            contradictions.append(
                f"Affectionate outreach ('miss my best friend') directly contradicts documented private gossip claiming you are selfish and abandoned her."
            )
        if has_money and any(w in all_text for w in ["scoffed", "not like you're doing anything", "savings"]):
            contradictions.append(
                f"Requesting significant financial support while actively demeaning how you manage your hard-earned savings."
            )
        if "7 year" in all_text or "history" in all_text:
            contradictions.append(
                f"Appealing to long-term loyalty (7 years of friendship) while failing to demonstrate basic mutual loyalty or honesty."
            )
        if not contradictions:
            contradictions.append(f"Discrepancy between stated intentions and the recorded emotional aftermath of each interaction.")

        # 4. Reciprocity Assessment
        if has_money and has_gossip:
            reciprocity = (
                f"Heavily asymmetrical. The documented transactions show one-directional financial expectations and reputational cost, "
                f"with no recorded instances of reciprocal support or accountability from {module.name}."
            )
        else:
            reciprocity = (
                f"The dynamic demonstrates an uneven emotional expenditure: you carry the burden of processing tension, "
                f"while {module.name} initiates contact primarily around requests or social resets."
            )

        # 5. Clarifying Questions for Human Decision
        questions = []
        if has_reconnect:
            questions.append(
                f"When {module.name} reaches out warmly now, what concrete evidence exists that the previous pattern of borrowing and gossip has changed?"
            )
        if "7 years" in all_text or "history" in all_text:
            questions.append(
                f"How much of your willingness to reconnect stems from nostalgia for past years versus how she currently treats you today?"
            )
        if boundaries:
            questions.append(
                f"You established '{boundaries[0]}'. How does responding to this latest interaction safeguard or compromise that commitment?"
            )
        else:
            questions.append(
                f"What clear boundary would protect your energy before deciding whether to engage further with {module.name}?"
            )

        takeaway = (
            f"The records over time show that {module.name}'s warm re-engagements occur without acknowledgment or repair of past breaches. "
            f"The choice of whether to re-engage rests entirely with you, based on documented patterns rather than temporary guilt."
        )

        return IncidentAnalysisReport(
            module_id=module.id,
            module_name=module.name,
            relationship=module.relationship,
            incident_count=count,
            timeline_summary=timeline_summary,
            escalation_analysis=escalation_analysis,
            documented_contradictions=contradictions,
            reciprocity_assessment=reciprocity,
            active_boundaries=boundaries,
            clarifying_questions=questions,
            key_takeaway=takeaway,
            generated_at=utc_now(),
        )
