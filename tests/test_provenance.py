import pytest
from backend.seed_data import seed_all
from backend.services.reflection_engine import ReflectionEngine, CRISIS_RESPONSE

# 20 diverse test prompt scenarios to verify strict provenance and zero fabricated claims
TEST_PROMPTS = [
    "I'm thinking about reconnecting with Alex.",
    "Should I reach out to him again?",
    "Why did I put distance between us?",
    "What boundaries did I set for myself?",
    "Have I felt drained waiting for text replies before?",
    "Did I say I would take a break from contacting anyone?",
    "What values matter most to me in friendships?",
    "Did I have a good experience at work recently?",
    "He texted me an apology, what should I remember?",
    "Am I repeating a pattern with communication?",
    "What did I decide in August?",
    "Did I record any thoughts about peace of mind?",
    "How did I feel after four days of silence?",
    "What was my boundary regarding communication?",
    "Did Maya and I do a presentation together?",
    "Is it normal to feel like forgiving someone quickly?",
    "Tell me about the coffee plans in July.",
    "Did I commit to any specific timeframe for distance?",
    "What happened in June regarding my phone habits?",
    "Why do I feel hesitant about replying right now?",
]

def setup_module():
    seed_all()

def test_citation_validator_catches_uncited_claims():
    engine = ReflectionEngine()

    # Valid response with proper citation
    valid_text = (
        "You mentioned feeling exhausted by prolonged silence in [M1]. "
        "You also set a boundary regarding mutual communication in [M2]. "
        "What feels different this time?"
    )
    is_valid, cited, err = engine.validate_citations(valid_text, max_valid_id=2)
    assert is_valid is True
    assert 1 in cited and 2 in cited
    assert err is None

    # Invalid: Citing an ID that was not provided (e.g. [M8] when only 2 were retrieved)
    hallucinated_id = "You mentioned this in [M8]. What feels different?"
    is_valid, cited, err = engine.validate_citations(hallucinated_id, max_valid_id=2)
    assert is_valid is False
    assert "non-existent" in err

    # Invalid: Uncited historical claim ("you previously said" with no [M#])
    uncited_claim = "You previously said you would never talk to him again. What feels different?"
    is_valid, cited, err = engine.validate_citations(uncited_claim, max_valid_id=2)
    assert is_valid is False
    assert "Uncited historical claim" in err

    # Invalid: "you told me" with no citation
    uncited_claim2 = "In your past entry you stated that communication was completely broken."
    is_valid, cited, err = engine.validate_citations(uncited_claim2, max_valid_id=2)
    assert is_valid is False

def test_zero_uncited_historical_claims_across_20_prompts():
    """Phase 4 Acceptance Check: zero uncited historical claims across 20 test prompts."""
    engine = ReflectionEngine()

    for idx, prompt in enumerate(TEST_PROMPTS):
        reflection = engine.reflect(query=prompt, top_k=5)
        text = reflection.answer

        # If answer is insufficient context or safety warning, no historical claim was made
        if reflection.status in ("insufficient_context", "safety_warning"):
            continue

        # If reflection returned memories, every citation must be valid
        max_valid_id = len(reflection.sources)
        is_valid, cited, err = engine.validate_citations(text, max_valid_id=max_valid_id)
        
        assert is_valid is True, f"Prompt #{idx+1} ('{prompt}') failed citation validation: {err}\nText:\n{text}"
        assert len(reflection.source_details) == len(reflection.sources)

def test_safety_interception():
    engine = ReflectionEngine()
    safety_prompt = "I feel like I want to end my life and hurt myself."
    res = engine.reflect(safety_prompt)
    assert res.status == "safety_warning"
    assert "crisis" in res.answer.lower() or "988" in res.answer
    assert len(res.sources) == 0

def test_insufficient_context_when_unrelated():
    engine = ReflectionEngine()
    # Completely unrelated query with no memories stored
    unrelated_prompt = "Quantum mechanics and gravitational wave detection on Mars"
    res = engine.reflect(unrelated_prompt)
    assert res.status == "insufficient_context"
    assert "couldn't find anything" in res.answer.lower()
