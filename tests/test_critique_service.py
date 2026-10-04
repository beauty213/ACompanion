import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.critique_service import critique_service

client = TestClient(app)

def test_critique_service_money_partying_match():
    res = critique_service.evaluate("I lent Maya 2000 dollars and saw her partying on Instagram stories but she won't pay me back")
    assert res["meme_url"].startswith("http")
    assert "SPONSOR" in res["verdict"] or "TRADE OFFER" in res["verdict"]
    assert "source_platform" in res
    assert "source_url" in res

def test_critique_service_delivered_fast_reply():
    res = critique_service.evaluate("He left me on delivered for two days and I replied in 3 seconds with a paragraph")
    assert res["meme_url"].startswith("http")
    assert "CLOWN" in res["verdict"]

def test_critique_service_location_stalking():
    res = critique_service.evaluate("It is 2 AM and I am checking their location and snap score to see who they are with")
    assert res["meme_url"].startswith("http")
    assert "FBI" in res["verdict"] or "INVESTIGATOR" in res["verdict"]

def test_critique_service_doomscrolling():
    res = critique_service.evaluate("I stayed up until 4 AM doomscrolling reels on my phone and now I am completely exhausted")
    assert res["meme_url"].startswith("http")
    assert "CONSEQUENCES" in res["verdict"]

def test_critique_service_texting_ex():
    res = critique_service.evaluate("I am feeling lonely tonight and thinking of texting my toxic ex to unblock them")
    assert res["meme_url"].startswith("http")
    assert "DOWN HORRENDOUS" in res["verdict"] or "EX" in res["verdict"]

def test_critique_service_hard_criticism_tone():
    res = critique_service.evaluate("He left me on delivered for two days and I replied in 3 seconds")
    critique_text = res["critique"].lower()
    # Ensure zero soft therapy jargon
    assert "protect your peace" not in critique_text
    assert "implement your boundary" not in critique_text
    assert "aww you had it rough" not in critique_text

def test_critique_service_diversity():
    # Different situations MUST get different verdicts and memes
    r1 = critique_service.evaluate("He left me on delivered for two days and I replied in 3 seconds")
    r2 = critique_service.evaluate("I lent Maya 2000 dollars and she is partying at a club")
    r3 = critique_service.evaluate("It is 2 AM and I am checking their location and snap score")
    verdicts = {r1["verdict"], r2["verdict"], r3["verdict"]}
    assert len(verdicts) >= 2, "Critique service should not return the same verdict for different situations"

def test_api_critique_persistence():
    # Create journal entry
    post_res = client.post("/api/journal", json={"title": "Money Drama", "content": "She owes me $500 and is partying on Instagram"})
    assert post_res.status_code == 201
    entry = post_res.json()
    entry_id = entry["id"]
    assert entry.get("critique") is not None
    original_verdict = entry["critique"]["verdict"]

    # Shuffle critique with entry_id
    shuf_res = client.post("/api/critique", json={"text": entry["content"], "entry_id": entry_id, "shuffle": True, "current_meme": entry["critique"]["meme_url"]})
    assert shuf_res.status_code == 200
    new_critique = shuf_res.json()

    # Re-fetch entry to ensure it persisted the update
    get_res = client.get(f"/api/journal/{entry_id}")
    assert get_res.status_code == 200
    updated_entry = get_res.json()
    assert updated_entry["critique"]["meme_url"] == new_critique["meme_url"]

def test_critique_service_expanded_situations():
    # Surprised Pikachu test
    pikachu_res = critique_service.evaluate("I touched the stove again and was shocked that they did it again")
    assert "PIKACHU" in pikachu_res["verdict"]

    # Ralph Wiggum danger test
    ralph_res = critique_service.evaluate("I know this is a bad idea and a huge red flag but heading into a mess anyway")
    assert "DANGER" in ralph_res["verdict"]

    # Buff Doge vs Cheems shower fantasy test
    doge_res = critique_service.evaluate("In my head I was going to confront them but in person I just said no worries haha")
    assert "TOUGH GUY" in doge_res["verdict"]

    # Catalog size check
    from backend.services.online_meme_service import online_meme_service
    assert len(online_meme_service.catalog) >= 50, "Meme catalog should have at least 50 situation memes"

