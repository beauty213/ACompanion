import json
import sqlite3
from datetime import datetime, timezone
from backend.database.connection import get_db_connection
from backend.database.schema import init_db
from backend.models.memory import ImportanceLevel, MemoryCreate, MemoryStatus, MemoryType
from backend.models.journal import JournalEntryCreate
from backend.services.journal_service import JournalService
from backend.services.memory_service import MemoryService

def seed_all(conn: sqlite3.Connection = None) -> dict:
    """Seeds fictional data spanning June to October for Anchor demo."""
    init_db(conn)
    mem_svc = MemoryService()
    jrn_svc = JournalService(memory_service=mem_svc)

    # 1. Reset existing data cleanly
    mem_svc.delete_all(conn=conn)

    # 2. Seed People
    if conn is None:
        conn = get_db_connection()
        close_conn = True
    else:
        close_conn = False

    try:
        conn.execute(
            "INSERT OR REPLACE INTO people (id, name, relationship, notes, created_at) VALUES (?, ?, ?, ?, ?)",
            ("p_alex", "Alex", "Friend / Casual acquaintance", "Known for periodic disappearing acts", "2026-06-01T10:00:00Z")
        )
        conn.execute(
            "INSERT OR REPLACE INTO people (id, name, relationship, notes, created_at) VALUES (?, ?, ?, ?, ?)",
            ("p_maya", "Maya", "Close Friend (7 years)", "Friendship where dynamic shifted to repeated borrowing, mockery, and fake rumors", "2026-06-01T10:00:00Z")
        )
        # Seed Modules / Tracks
        conn.execute(
            "INSERT OR REPLACE INTO modules (id, name, alias, relationship, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("mod_maya", "Maya (Friend of 7 Years)", "Ex-Friend (7 Years)", "Close Friend (7 years)", "Long-time friendship where dynamic shifted to repeated borrowing, mockery, and fake rumors.", "2026-09-01T10:00:00Z", "2026-10-03T10:00:00Z")
        )
        conn.execute(
            "INSERT OR REPLACE INTO modules (id, name, alias, relationship, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("mod_alex", "Alex", "Inconsistent Contact", "Friend / Casual acquaintance", "Known for periodic disappearing acts and one-sided communication.", "2026-06-01T10:00:00Z", "2026-10-02T10:00:00Z")
        )
        conn.execute(
            "INSERT OR REPLACE INTO modules (id, name, alias, relationship, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("mod_work", "Work & Career", "Professional Work", "Professional", "Design presentations and workplace workload boundaries.", "2026-09-01T10:00:00Z", "2026-09-10T10:00:00Z")
        )
        conn.commit()
    finally:
        if close_conn:
            conn.close()

    # 3. Seed Journal Entries
    entries_data = [
        {
            "id": "jrn_01",
            "title": "Alex and communication habits",
            "content": "Alex disappeared for four days right before our weekend plans. I spent hours checking my phone waiting for a reply, feeling sick and completely ignored. It drained all my energy for no reason.",
            "created_at": "2026-06-14T19:30:00Z",
            "module_id": "mod_alex"
        },
        {
            "id": "jrn_02",
            "title": "Deciding on communication boundaries",
            "content": "Talked with a close friend today about my limits. Waiting multiple days for a response without any heads-up is not acceptable to me. I need mutual consistency and respect in my relationships.",
            "created_at": "2026-06-28T21:15:00Z",
            "module_id": "mod_alex"
        },
        {
            "id": "jrn_03",
            "title": "The pattern repeating again",
            "content": "Alex popped back up today acting like nothing had happened. We chatted, made tentative coffee plans, and now silence again for five days. I felt the exact same stomach drop as last month. I keep letting this happen.",
            "created_at": "2026-07-19T20:00:00Z",
            "module_id": "mod_alex"
        },
        {
            "id": "jrn_04",
            "title": "Need distance — stepping back",
            "content": "I wrote down my thoughts today because I don't want to repeat this cycle anymore. When someone makes communication a waiting game, I have to step away. I decided to take a full three-month break from contacting Alex.",
            "created_at": "2026-08-03T18:45:00Z",
            "module_id": "mod_alex"
        },
        {
            "id": "jrn_05",
            "title": "Quiet weeks and finding peace",
            "content": "It has been three weeks without waiting for anyone to text back. My mornings feel so much calmer and I have room to focus on creative projects. Peace of mind is worth so much more than holding on to unreliable dynamics.",
            "created_at": "2026-08-22T09:30:00Z",
            "module_id": "mod_alex"
        },
        {
            "id": "jrn_06",
            "title": "Quarterly product presentation",
            "content": "Delivered the Q3 design review with Maya today. The team responded really well to our proposal. Feeling grounded and confident in my work environment.",
            "created_at": "2026-09-10T17:00:00Z",
            "module_id": "mod_work"
        },
        {
            "id": "jrn_07",
            "title": "Thoughts on healthy reciprocation",
            "content": "Realized that healthy relationships never feel like an interrogation or a guessing test. True mutual friends communicate easily without games or lingering anxiety.",
            "created_at": "2026-09-28T22:00:00Z",
            "module_id": None
        },
        {
            "id": "jrn_08",
            "title": "Alex sent an apology message",
            "content": "Alex texted out of the blue today: 'Hey, sorry I vanished, had a rough month, really miss you and want to catch up.' My immediate impulse was to say yes, but I paused. Need to remember why I put distance there in the first place.",
            "created_at": "2026-10-02T16:20:00Z",
            "module_id": "mod_alex"
        },
        # Maya 7-Year Friendship Incidents
        {
            "id": "jrn_m01",
            "title": "Unpaid loans & $2,000 rent ask",
            "content": "I am feeling sick to my stomach about Maya. We've been close friends for 7 years, but lately the dynamic has completely shifted. Yesterday she casually asked if she could borrow $2,000 for her rent, on top of the $400 she still hasn't paid back from last month. When I hesitated, she scoffed and said, 'It's not like you're doing anything important with your savings anyway.' It felt like a slap in the face. I value our long history, but I need to draw a hard line: no more lending money to her, under any circumstances.",
            "created_at": "2026-09-12T19:30:00Z",
            "module_id": "mod_maya"
        },
        {
            "id": "jrn_m02",
            "title": "Discovered fake gossip & trust betrayal",
            "content": "Another painful discovery today. A mutual friend pulled me aside and told me Maya has been spreading fake gossip about me behind my back, claiming I'm selfish and that I 'abandoned' her when she needed help. Hearing that she is talking about me this way after 7 years of friendship hurts more than the money issue. I realize that history together doesn't excuse cruelty or deceit. My boundary: I will no longer share personal updates with Maya or tolerate being spoken about behind my back.",
            "created_at": "2026-09-22T20:15:00Z",
            "module_id": "mod_maya"
        },
        {
            "id": "jrn_m03",
            "title": "Friendly coffee text out of the blue",
            "content": "Maya texted me out of the blue today saying, 'Hey stranger! I miss my best friend of 7 years, let's grab coffee this weekend.' Part of me feels guilty and misses the good old times before things got messy. Am I being too harsh? Should I give her another chance and offer to help her out?",
            "created_at": "2026-10-03T14:00:00Z",
            "module_id": "mod_maya"
        }
    ]

    for ed in entries_data:
        jrn_svc.create_entry(JournalEntryCreate(**ed))

    # 4. Seed Memories (6+ confirmed/edited, 2 boundaries, 1 suggested)
    memories_data = [
        MemoryCreate(
            id="mem_01",
            type=MemoryType.EXPERIENCE,
            title="Exhaustion from waiting for Alex's replies",
            content="Spent hours repeatedly checking my phone waiting for replies from Alex after four days of silence; felt drained, anxious, and disregarded.",
            summary="Waiting for Alex's replies caused severe drain and anxiety.",
            related_people=["Alex"],
            related_topics=["communication", "waiting", "anxiety"],
            emotion="exhausted",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_01",
            module_id="mod_alex"
        ),
        MemoryCreate(
            id="mem_02",
            type=MemoryType.BOUNDARY,
            title="Consistent communication boundary",
            content="I will not accept waiting days for communication without notice. I deserve reliable, mutual respect in friendships.",
            summary="Boundary against prolonged unexplained silence.",
            related_people=["Alex"],
            related_topics=["boundaries", "communication", "respect"],
            emotion="determined",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_02",
            module_id="mod_alex"
        ),
        MemoryCreate(
            id="mem_03",
            type=MemoryType.REFLECTION,
            title="Noticing the cycle of easy forgiveness and letdown",
            content="Observed that I readily brush off unexplained silence when Alex returns, only to end up in the exact same cycle of waiting and disappointment.",
            summary="Recognized repeated cycle of forgiveness leading to identical letdown.",
            related_people=["Alex"],
            related_topics=["patterns", "forgiveness", "disappointment"],
            emotion="frustrated",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_03",
            module_id="mod_alex"
        ),
        MemoryCreate(
            id="mem_04",
            type=MemoryType.BOUNDARY,
            title="Distance from one-sided waiting dynamics",
            content="I step back and preserve space whenever communication becomes an anxious one-sided waiting game.",
            summary="Stepping back when communication becomes one-sided.",
            related_people=["Alex"],
            related_topics=["boundaries", "self-protection", "distance", "reconnecting"],
            emotion="calm",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_04",
            module_id="mod_alex"
        ),
        MemoryCreate(
            id="mem_05",
            type=MemoryType.COMMITMENT,
            title="Three-month pause on contacting Alex",
            content="Committed to taking a three-month pause from reaching out to Alex to clear my head and break the reactive cycle.",
            summary="Three-month intentional pause from reaching out to Alex.",
            related_people=["Alex"],
            related_topics=["pause", "commitment", "healing", "reconnecting"],
            emotion="resolved",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_04",
            module_id="mod_alex"
        ),
        MemoryCreate(
            id="mem_06",
            type=MemoryType.VALUE,
            title="Peace of mind over unreliable ties",
            content="Peace of mind and emotional stability are far more valuable to me than maintaining ties with someone whose communication is erratic.",
            summary="Valuing mental peace over erratic dynamics.",
            related_people=[],
            related_topics=["values", "peace", "well-being"],
            emotion="peaceful",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_05"
        ),
        MemoryCreate(
            id="mem_07",
            type=MemoryType.EVENT,
            title="Quarterly design presentation with Maya",
            content="Presented the design proposals alongside Maya; felt grounded, capable, and received clear positive feedback.",
            summary="Successful presentation with Maya.",
            related_people=["Maya"],
            related_topics=["work", "presentation", "confidence"],
            emotion="confident",
            importance=ImportanceLevel.MED,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_06",
            module_id="mod_work"
        ),
        MemoryCreate(
            id="mem_08",
            type=MemoryType.REFLECTION,
            title="Ease of genuine friendships",
            content="Healthy relationships feel natural, calm, and predictable, not like a test of patience or guesswork.",
            summary="Healthy bonds do not involve anxiety.",
            related_people=[],
            related_topics=["friendship", "reflection", "connection"],
            emotion="content",
            importance=ImportanceLevel.MED,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_07"
        ),
        MemoryCreate(
            id="mem_09",
            type=MemoryType.REFLECTION,
            title="Impulse to reply to Alex's apology",
            content="Noticed the old familiar urge to immediately accept Alex's apology and reconnect without evaluating what changed.",
            summary="Temptation to immediately accept apology.",
            related_people=["Alex"],
            related_topics=["reconnecting", "apology", "second-chance"],
            emotion="uncertain",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.AI_SUGGESTED,
            source_journal_id="jrn_08",
            module_id="mod_alex"
        ),
        # Maya Memories
        MemoryCreate(
            id="mem_m01",
            type=MemoryType.BOUNDARY,
            title="Boundary: No more lending money to Maya",
            content="No more lending money to Maya under any circumstances after the unpaid $400 loan and the $2,000 demand.",
            summary="Hard boundary against lending money to Maya.",
            related_people=["Maya"],
            related_topics=["boundaries", "money", "loans", "Maya"],
            emotion="firm",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_m01",
            module_id="mod_maya"
        ),
        MemoryCreate(
            id="mem_m02",
            type=MemoryType.BOUNDARY,
            title="Boundary: No personal updates or tolerating rumors",
            content="I will no longer share personal updates with Maya or tolerate being spoken about behind my back.",
            summary="Boundary against personal disclosure and fake rumors.",
            related_people=["Maya"],
            related_topics=["boundaries", "gossip", "trust", "Maya"],
            emotion="betrayed",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_m02",
            module_id="mod_maya"
        ),
        MemoryCreate(
            id="mem_m03",
            type=MemoryType.REFLECTION,
            title="Reflection: 7 years does not excuse deceit",
            content="7 years of friendship history does not give someone permission to feel entitled to my money, ridicule my choices, or backstab me to mutual friends.",
            summary="History together does not excuse cruelty or manipulation.",
            related_people=["Maya"],
            related_topics=["friendship", "loyalty", "respect", "Maya"],
            emotion="clear",
            importance=ImportanceLevel.HIGH,
            status=MemoryStatus.USER_CONFIRMED,
            source_journal_id="jrn_m02",
            module_id="mod_maya"
        )
    ]

    for md in memories_data:
        mem_svc.create_memory(md)

    # 5. Seed Future Self Message (Section 7.4 & 12)
    conn_fs = get_db_connection()
    try:
        conn_fs.execute(
            """
            INSERT OR REPLACE INTO future_self_messages (
                id, message, related_person, related_topic, importance,
                trigger_context, expires_at, created_at, triggered_at, dismissed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "fs_01",
                "Remember how heavy it felt waiting by the phone all summer. If you consider reconnecting with Alex or giving a second chance, ask what is actually different before stepping back into the cycle.",
                "Alex",
                "reconnecting",
                "high",
                "reconnecting, Alex, reaching out, second chance, apologized, apology, give another chance",
                None,
                "2026-08-03T19:00:00Z",
                None,
                0
            )
        )
        conn_fs.execute(
            """
            INSERT OR REPLACE INTO future_self_messages (
                id, message, related_person, related_topic, importance,
                trigger_context, expires_at, created_at, triggered_at, dismissed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "fs_02",
                "If Maya reaches out being sweet or asking for another favor, remember: 7 years of friendship doesn't cancel out the unpaid loans, ridicule of your savings, and spreading rumors behind your back. Do not let nostalgia erase how drained and betrayed you felt. Protect your peace first.",
                "Maya",
                "friendship",
                "high",
                "Maya, 7 years, coffee, borrow, money, favor, reconnecting, stranger",
                None,
                "2026-09-23T10:00:00Z",
                None,
                0
            )
        )
        # 6. Seed Patterns (Section 7.5: >=3 supporting memories)
        conn_fs.execute(
            """
            INSERT OR REPLACE INTO patterns (
                id, title, description, memory_ids, dismissed, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "pat_01",
                "Communication waiting cycle and reconnection dilemma",
                "These entries contain similar themes: waiting days for replies with anxiety, setting boundaries to step back, and contemplating second chances when apologies arrive.",
                json.dumps(["mem_01", "mem_02", "mem_03", "mem_04", "mem_05"]),
                0,
                "2026-10-02T17:00:00Z"
            )
        )
        conn_fs.execute(
            """
            INSERT OR REPLACE INTO patterns (
                id, title, description, memory_ids, dismissed, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "pat_02",
                "Escalating entitlement & trust betrayal across 7-year friendship",
                "These entries trace repeated boundaries regarding money demands ($400 unpaid loan, $2,000 rent demand), dismissive remarks about savings, and discovered behind-the-back rumors.",
                json.dumps(["mem_m01", "mem_m02", "mem_m03"]),
                0,
                "2026-10-03T16:00:00Z"
            )
        )
        conn_fs.commit()
    finally:
        conn_fs.close()

    return {
        "status": "success",
        "journal_entries_seeded": len(entries_data),
        "memories_seeded": len(memories_data),
        "future_self_messages": 1,
        "patterns": 2
    }

def reset_all() -> dict:
    mem_svc = MemoryService()
    mem_svc.delete_all()
    return {"status": "success", "message": "All data reset."}

if __name__ == "__main__":
    res = seed_all()
    print("Seed complete:", res)
