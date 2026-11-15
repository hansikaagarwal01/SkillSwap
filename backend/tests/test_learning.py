import sys
import os
import concurrent.futures
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from app.models.student import Student
from app.models.session import LearningSession
from app.models.review import Review
from app.models.experience import Experience
from app.core.security import create_access_token

client = TestClient(app)

def get_auth_token(roll_no: str, role: str = "STUDENT") -> str:
    return create_access_token(subject=roll_no, role=role, token_version=1)

def test_session_creation_and_business_rules():
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    bhavya_token = get_auth_token("2024BTECH002")

    # 1. Self-mentoring blocked -> 400
    resp_self = client.post(
        "/api/v1/sessions",
        json={
            "mentor_roll_no": "2024BTECH001",
            "skill_id": 1,
            "topic": "Python Self Talk",
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        },
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_self.status_code == 400
    assert resp_self.json()["error"]["code"] == "SELF_MENTORING_BLOCKED"

    # 2. Mentor without can_teach = TRUE blocked -> 400
    # Eshan Verma (2024BTECH005) only teaches Embedded Systems (16), not React (3)
    resp_cant_teach = client.post(
        "/api/v1/sessions",
        json={
            "mentor_roll_no": "2024BTECH005",
            "skill_id": 3,
            "topic": "Learn React from Hardware Guy",
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        },
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_cant_teach.status_code == 400
    assert resp_cant_teach.json()["error"]["code"] == "SKILL_NOT_TAUGHT"


def test_session_lifecycle_and_state_machine():
    # Bhavya (mentor) & Gauri (learner - regular STUDENT, not ADMIN)
    bhavya_token = get_auth_token("2024BTECH002")
    gauri_token = get_auth_token("2025BTECH007")

    # Past scheduled time for test completion
    past_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()

    # 1. Gauri requests session with Bhavya (Python, skill_id=1)
    resp_req = client.post(
        "/api/v1/sessions",
        json={
            "mentor_roll_no": "2024BTECH002",
            "skill_id": 1,
            "topic": "Python Asyncio and Coroutines",
            "mode": "ONLINE",
            "scheduled_at": past_time,
            "meeting_link": "https://meet.google.com/test-lifecycle"
        },
        headers={"Authorization": f"Bearer {gauri_token}"}
    )
    assert resp_req.status_code == 201
    session_data = resp_req.json()
    session_id = session_data["session_id"]
    assert session_data["status"] == "REQUESTED"
    assert session_data["credit_cost"] == 0

    # 2. Invalid transition: learner (Gauri) tries to accept -> 403
    resp_bad_accept = client.patch(
        f"/api/v1/sessions/{session_id}/status",
        json={"status": "ACCEPTED"},
        headers={"Authorization": f"Bearer {gauri_token}"}
    )
    assert resp_bad_accept.status_code == 403

    # 3. Mentor (Bhavya) accepts session -> 200
    resp_accept = client.patch(
        f"/api/v1/sessions/{session_id}/status",
        json={"status": "ACCEPTED"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_accept.status_code == 200
    assert resp_accept.json()["status"] == "ACCEPTED"

    # 4. Record initial reputation points
    db: Session = SessionLocal()
    initial_mentor_rep = db.query(Student.reputation_points).filter(Student.roll_no == "2024BTECH002").scalar()
    db.close()

    # 5. Mentor completes session -> 200, awards +10 reputation points
    resp_comp = client.patch(
        f"/api/v1/sessions/{session_id}/status",
        json={"status": "COMPLETED"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_comp.status_code == 200
    assert resp_comp.json()["status"] == "COMPLETED"

    # Verify reputation points increased by exactly 10
    db = SessionLocal()
    new_mentor_rep = db.query(Student.reputation_points).filter(Student.roll_no == "2024BTECH002").scalar()
    assert new_mentor_rep == initial_mentor_rep + 10

    # Verify reputation audit on session
    comp_sess = db.query(LearningSession).filter(LearningSession.session_id == session_id).first()
    assert comp_sess is not None
    assert comp_sess.reputation_awarded is True
    assert comp_sess.points_awarded == 10
    assert comp_sess.reputation_awarded_at is not None
    db.close()

    # 6. Idempotency & anti-double-award: completing again -> 409
    resp_double = client.patch(
        f"/api/v1/sessions/{session_id}/status",
        json={"status": "COMPLETED"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_double.status_code == 409
    assert resp_double.json()["error"]["code"] == "ALREADY_COMPLETED"

    # Verify reputation points DID NOT increase again
    db = SessionLocal()
    after_double_rep = db.query(Student.reputation_points).filter(Student.roll_no == "2024BTECH002").scalar()
    assert after_double_rep == new_mentor_rep
    db.close()


def test_concurrent_session_completion():
    # Setup a new session in ACCEPTED status with past scheduled_at
    db: Session = SessionLocal()
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    test_session = LearningSession(
        mentor_roll_no="2024BTECH002",
        learner_roll_no="2024BTECH001",
        skill_id=1,
        topic="Concurrent Completion Test",
        mode="ONLINE",
        scheduled_at=past_time,
        status="ACCEPTED",
        credit_cost=0
    )
    db.add(test_session)
    db.commit()
    db.refresh(test_session)
    s_id = test_session.session_id

    initial_points = db.query(Student.reputation_points).filter(Student.roll_no == "2024BTECH002").scalar()
    db.close()

    bhavya_token = get_auth_token("2024BTECH002")

    def call_complete():
        c = TestClient(app)
        return c.patch(
            f"/api/v1/sessions/{s_id}/status",
            json={"status": "COMPLETED"},
            headers={"Authorization": f"Bearer {bhavya_token}"}
        )

    # Launch 4 concurrent completion requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(call_complete) for _ in range(4)]
        responses = [f.result() for f in futures]

    status_codes = [r.status_code for r in responses]
    # Exactly one request must return 200, others must return 409
    assert status_codes.count(200) == 1
    assert status_codes.count(409) == 3

    # Verify database reputation increased by exactly 10
    db = SessionLocal()
    final_points = db.query(Student.reputation_points).filter(Student.roll_no == "2024BTECH002").scalar()
    assert final_points == initial_points + 10
    db.close()


def test_reviews_lifecycle_and_rules():
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    bhavya_token = get_auth_token("2024BTECH002")
    sneha_token = get_auth_token("2024BBA001")

    # Seed session 1: COMPLETED (Aarav mentor, Gauri learner)
    # 1. Non-participant (Sneha) tries to review -> 403
    resp_non_part = client.post(
        "/api/v1/reviews",
        json={"session_id": 1, "rating": 5, "comment": "Sneha says hello"},
        headers={"Authorization": f"Bearer {sneha_token}"}
    )
    assert resp_non_part.status_code == 403
    assert resp_non_part.json()["error"]["code"] == "NOT_PARTICIPANT"

    # 2. Review on incomplete session (session 31 is ACCEPTED) -> 409
    resp_incomp = client.post(
        "/api/v1/reviews",
        json={"session_id": 31, "rating": 5, "comment": "Reviewing too early"},
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_incomp.status_code == 409
    assert resp_incomp.json()["error"]["code"] == "SESSION_NOT_COMPLETED"

    # 3. Duplicate review on session 1 (Gauri already reviewed Aarav in seed) -> 409
    gauri_token = get_auth_token("2025BTECH007")
    resp_dup = client.post(
        "/api/v1/reviews",
        json={"session_id": 1, "rating": 4, "comment": "Another review"},
        headers={"Authorization": f"Bearer {gauri_token}"}
    )
    assert resp_dup.status_code == 409
    assert resp_dup.json()["error"]["code"] == "DUPLICATE_REVIEW"


def test_experience_portfolio_crud():
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    bhavya_token = get_auth_token("2024BTECH002")

    # 1. Bhavya tries to add experience to Aarav -> 403
    resp_forbidden = client.post(
        "/api/v1/students/2024BTECH001/experiences",
        json={
            "role_title": "Fake Intern",
            "organization": "Scam Corp",
            "exp_type": "INTERNSHIP",
            "start_date": "2025-01-01"
        },
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_forbidden.status_code == 403

    # 2. Aarav adds new experience -> 201 with auto-incremented exp_no
    resp_create = client.post(
        "/api/v1/students/2024BTECH001/experiences",
        json={
            "role_title": "Cloud Architecture Intern",
            "organization": "Amazon Web Services",
            "exp_type": "INTERNSHIP",
            "start_date": "2026-01-10",
            "end_date": "2026-06-30",
            "description": "Designing serverless Lambda workflows."
        },
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_create.status_code == 201
    exp_data = resp_create.json()
    assert exp_data["roll_no"] == "2024BTECH001"
    exp_no = exp_data["exp_no"]

    # 3. Date validation: end_date < start_date -> 422
    resp_bad_dates = client.post(
        "/api/v1/students/2024BTECH001/experiences",
        json={
            "role_title": "Time Traveler",
            "organization": "Future Tech",
            "start_date": "2026-06-01",
            "end_date": "2025-01-01"
        },
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_bad_dates.status_code == 422

    # 4. Aarav updates his experience -> 200
    resp_update = client.patch(
        f"/api/v1/experiences/2024BTECH001/{exp_no}",
        json={"role_title": "Senior Cloud Architecture Intern"},
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["role_title"] == "Senior Cloud Architecture Intern"

    # 5. Aarav deletes his experience -> 200
    resp_del = client.delete(
        f"/api/v1/experiences/2024BTECH001/{exp_no}",
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_del.status_code == 200


def test_mentorship_requires_can_teach():
    from datetime import datetime, timedelta, timezone
    from app.core.security import create_access_token

    aarav_token = create_access_token(subject="2024BTECH001", role="ADMIN", token_version=1)
    bhavya_token = create_access_token(subject="2024BTECH002", role="STUDENT", token_version=1)

    # Give Bhavya skill_id=10 with can_teach=False (learning-only skill)
    resp_skill = client.post(
        "/api/v1/students/2024BTECH002/skills",
        json={"skill_id": 10, "proficiency_level": "INTERMEDIATE", "can_teach": False},
        headers={"Authorization": f"Bearer {bhavya_token}"},
    )
    assert resp_skill.status_code == 201

    try:
        future_iso = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        resp_req = client.post(
            "/api/v1/sessions",
            json={
                "mentor_roll_no": "2024BTECH002",
                "skill_id": 10,
                "topic": "Requesting skill where mentor has can_teach=False",
                "mode": "ONLINE",
                "scheduled_at": future_iso,
            },
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert resp_req.status_code == 400
        assert resp_req.json()["error"]["code"] == "SKILL_NOT_TAUGHT"
    finally:
        client.delete(
            "/api/v1/students/2024BTECH002/skills/10",
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )


def test_dual_participant_peer_reviews_and_has_review_scope():
    from datetime import datetime, timedelta, timezone
    from app.db.session import SessionLocal
    from app.models.skill import StudentSkill
    from app.models.session import LearningSession
    from app.models.review import Review
    from app.core.security import create_access_token

    aarav_token = create_access_token(subject="2024BTECH001", role="ADMIN", token_version=1)
    bhavya_token = create_access_token(subject="2024BTECH002", role="STUDENT", token_version=1)

    db = SessionLocal()
    teach_row = db.query(StudentSkill).filter(
        StudentSkill.roll_no == "2024BTECH001",
        StudentSkill.can_teach.is_(True),
    ).first()
    assert teach_row is not None
    skill_id = teach_row.skill_id
    db.close()

    session_id = None
    try:
        # 1. Bhavya requests session with Aarav -> 201
        resp_create = client.post(
            "/api/v1/sessions",
            json={
                "mentor_roll_no": "2024BTECH001",
                "skill_id": skill_id,
                "topic": "Dual participant review scoping verification",
                "mode": "ONLINE",
                "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
            },
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )
        assert resp_create.status_code == 201
        session_id = resp_create.json()["session_id"]

        # 2. Aarav accepts the session, then scheduled time elapses before completion
        resp_accept = client.patch(
            f"/api/v1/sessions/{session_id}/status",
            json={"status": "ACCEPTED"},
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert resp_accept.status_code == 200

        db = SessionLocal()
        sess_row = db.query(LearningSession).filter(LearningSession.session_id == session_id).first()
        sess_row.scheduled_at = datetime.now(timezone.utc) - timedelta(hours=2)
        db.commit()
        db.close()

        resp_complete = client.patch(
            f"/api/v1/sessions/{session_id}/status",
            json={"status": "COMPLETED"},
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert resp_complete.status_code == 200, resp_complete.text

        # 3. Bhavya leaves peer review -> 201
        resp_r1 = client.post(
            "/api/v1/reviews",
            json={
                "session_id": session_id,
                "rating": 5,
                "comment": "Clear explanation and structured examples.",
            },
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )
        assert resp_r1.status_code == 201
        assert resp_r1.json()["roll_no"] == "2024BTECH002"

        # 4. Bhavya duplicate review blocked -> 409
        resp_dup = client.post(
            "/api/v1/reviews",
            json={"session_id": session_id, "rating": 4, "comment": "Duplicate attempt"},
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )
        assert resp_dup.status_code == 409

        # 5. has_review must be True for Bhavya and still False for Aarav
        bhavya_list = client.get(
            "/api/v1/sessions?page_size=50",
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )
        assert bhavya_list.status_code == 200
        bhavya_sess = next(s for s in bhavya_list.json()["items"] if s["session_id"] == session_id)
        assert bhavya_sess["has_review"] is True

        aarav_list = client.get(
            "/api/v1/sessions?page_size=50",
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert aarav_list.status_code == 200
        aarav_sess = next(s for s in aarav_list.json()["items"] if s["session_id"] == session_id)
        assert aarav_sess["has_review"] is False

        # 6. Aarav submits his peer review -> 201
        resp_r2 = client.post(
            "/api/v1/reviews",
            json={
                "session_id": session_id,
                "rating": 5,
                "comment": "Well-prepared learner with thoughtful questions.",
            },
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert resp_r2.status_code == 201
        assert resp_r2.json()["roll_no"] == "2024BTECH001"

        # 7. Aarav's has_review now True and GET /sessions/{id}/reviews returns both
        aarav_list_after = client.get(
            "/api/v1/sessions?page_size=50",
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        aarav_sess_after = next(s for s in aarav_list_after.json()["items"] if s["session_id"] == session_id)
        assert aarav_sess_after["has_review"] is True

        resp_reviews = client.get(
            f"/api/v1/sessions/{session_id}/reviews",
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )
        assert resp_reviews.status_code == 200
        reviews = resp_reviews.json()
        assert len(reviews) == 2
        assert {r["roll_no"] for r in reviews} == {"2024BTECH001", "2024BTECH002"}
    finally:
        if session_id is not None:
            db = SessionLocal()
            db.query(Review).filter(Review.session_id == session_id).delete()
            db.query(LearningSession).filter(LearningSession.session_id == session_id).delete()
            db.commit()
            db.close()


def test_experience_update_clear_end_date_authz_and_delete():
    from app.core.security import create_access_token

    aarav_token = create_access_token(subject="2024BTECH001", role="ADMIN", token_version=1)
    bhavya_token = create_access_token(subject="2024BTECH002", role="STUDENT", token_version=1)

    resp_create = client.post(
        "/api/v1/students/2024BTECH001/experiences",
        json={
            "role_title": "Peer Mentorship Lead",
            "organization": "JKLU Academic Council",
            "exp_type": "PROJECT",
            "start_date": "2026-01-15",
            "end_date": "2026-05-15",
            "description": "Coordinating peer labs.",
        },
        headers={"Authorization": f"Bearer {aarav_token}"},
    )
    assert resp_create.status_code == 201
    exp_no = resp_create.json()["exp_no"]

    try:
        # Cross-user forbidden checks
        resp_forbid_patch = client.patch(
            f"/api/v1/experiences/2024BTECH001/{exp_no}",
            json={"role_title": "Unauthorized Edit"},
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )
        assert resp_forbid_patch.status_code == 403

        resp_forbid_del = client.delete(
            f"/api/v1/experiences/2024BTECH001/{exp_no}",
            headers={"Authorization": f"Bearer {bhavya_token}"},
        )
        assert resp_forbid_del.status_code == 403

        # Invalid date order on PATCH -> 400 INVALID_DATES
        resp_bad_date = client.patch(
            f"/api/v1/experiences/2024BTECH001/{exp_no}",
            json={"end_date": "2020-01-01"},
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert resp_bad_date.status_code == 400
        assert resp_bad_date.json()["error"]["code"] == "INVALID_DATES"

        # Clear end_date (mark ongoing) + update description -> 200
        resp_clear = client.patch(
            f"/api/v1/experiences/2024BTECH001/{exp_no}",
            json={"end_date": None, "description": "Updated ongoing leadership role."},
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert resp_clear.status_code == 200
        cleared = resp_clear.json()
        assert cleared["end_date"] is None
        assert cleared["description"] == "Updated ongoing leadership role."

        # Verify persisted via GET
        resp_list = client.get("/api/v1/students/2024BTECH001/experiences")
        assert resp_list.status_code == 200
        match = next(e for e in resp_list.json() if e["exp_no"] == exp_no)
        assert match["end_date"] is None
        assert match["description"] == "Updated ongoing leadership role."
    finally:
        resp_del = client.delete(
            f"/api/v1/experiences/2024BTECH001/{exp_no}",
            headers={"Authorization": f"Bearer {aarav_token}"},
        )
        assert resp_del.status_code == 200

    resp_after_del = client.get("/api/v1/students/2024BTECH001/experiences")
    assert all(e["exp_no"] != exp_no for e in resp_after_del.json())
