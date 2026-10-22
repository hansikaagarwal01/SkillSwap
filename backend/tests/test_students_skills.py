import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def get_auth_token(roll_no: str, password: str = "Student@JKLU2026", role: str = "STUDENT") -> str:
    if roll_no == "2024BTECH001":
        role = "ADMIN"
    return create_access_token(subject=roll_no, role=role, token_version=1)

def test_list_and_filter_students():
    # 1. Basic pagination
    resp = client.get("/api/v1/students?page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total"] >= 30
    assert len(data["items"]) == 5

    # 2. Filter by program
    resp_btech = client.get("/api/v1/students?program=BTECH&page_size=50")
    assert resp_btech.status_code == 200
    for student in resp_btech.json()["items"]:
        assert student["program"] == "BTECH"

    # 3. Filter by admission year
    resp_2024 = client.get("/api/v1/students?admission_year=2024&page_size=50")
    assert resp_2024.status_code == 200
    for student in resp_2024.json()["items"]:
        assert student["admission_year"] == 2024

    # 4. Search query
    resp_search = client.get("/api/v1/students?q=Aarav")
    assert resp_search.status_code == 200
    items = resp_search.json()["items"]
    assert len(items) >= 1
    assert "Aarav" in items[0]["name"]


def test_get_and_update_student_profile_with_authz():
    # 1. Get student profile
    resp = client.get("/api/v1/students/2024BTECH001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["roll_no"] == "2024BTECH001"
    assert data["name"] == "Aarav Sharma"
    assert len(data["skills"]) >= 1

    # 2. Non-existent student -> 404
    resp_404 = client.get("/api/v1/students/2029BTECH999")
    assert resp_404.status_code == 404

    # 3. Update profile - unauthorized user (Bhavya tries to edit Aarav) -> 403
    bhavya_token = get_auth_token("2024BTECH002")
    resp_unauth = client.patch(
        "/api/v1/students/2024BTECH001",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_unauth.status_code == 403
    assert resp_unauth.json()["error"]["code"] == "FORBIDDEN"

    # 4. Update profile - authorized owner (Aarav edits Aarav) -> 200
    aarav_token = get_auth_token("2024BTECH001", "Admin@JKLU2026")
    resp_owner = client.patch(
        "/api/v1/students/2024BTECH001",
        json={"phone": "9829099999"},
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_owner.status_code == 200
    assert resp_owner.json()["phone"] == "9829099999"


def test_skills_catalog_and_creation():
    # 1. List skills
    resp = client.get("/api/v1/skills")
    assert resp.status_code == 200
    skills = resp.json()
    assert len(skills) >= 15
    skill_names = [s["name"] for s in skills]
    assert "Python Programming" in skill_names
    assert "Machine Learning" in skill_names

    # 2. Create skill with authenticated user
    aarav_token = get_auth_token("2024BTECH001", "Admin@JKLU2026")
    resp_create = client.post(
        "/api/v1/skills",
        json={
            "name": "DevOps & Docker Containers",
            "category": "Cloud & Infrastructure",
            "description": "Containerizing apps with Docker and Kubernetes orchestration."
        },
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_create.status_code in (201, 409)

    # 3. Duplicate skill creation -> 409
    resp_dup = client.post(
        "/api/v1/skills",
        json={
            "name": "Python Programming",
            "category": "Computer Science"
        },
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_dup.status_code == 409
    assert resp_dup.json()["error"]["code"] == "SKILL_EXISTS"


def test_student_skills_management():
    aarav_token = get_auth_token("2024BTECH001", "Admin@JKLU2026")
    bhavya_token = get_auth_token("2024BTECH002")

    # 1. Bhavya tries to add skill to Aarav -> 403
    resp_forbidden = client.post(
        "/api/v1/students/2024BTECH001/skills",
        json={"skill_id": 10, "proficiency_level": "EXPERT", "can_teach": True},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_forbidden.status_code == 403

    # 2. Aarav adds skill to himself -> 201
    resp_add = client.post(
        "/api/v1/students/2024BTECH001/skills",
        json={"skill_id": 10, "proficiency_level": "ADVANCED", "can_teach": False},
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_add.status_code == 201
    assert resp_add.json()["proficiency_level"] == "ADVANCED"

    # 3. Aarav updates the same skill -> 201
    resp_update = client.post(
        "/api/v1/students/2024BTECH001/skills",
        json={"skill_id": 10, "proficiency_level": "EXPERT", "can_teach": True},
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_update.status_code == 201
    assert resp_update.json()["proficiency_level"] == "EXPERT"
    assert resp_update.json()["can_teach"] is True

    # 4. Aarav deletes the skill -> 200
    resp_delete = client.delete(
        "/api/v1/students/2024BTECH001/skills/10",
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_delete.status_code == 200


def test_mentor_discovery():
    # 1. Discover all mentors
    resp = client.get("/api/v1/mentors")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 10
    assert len(data["items"]) >= 1

    # 2. Discover mentors for Python Programming (skill_id = 1)
    resp_py = client.get("/api/v1/mentors?skill_id=1")
    assert resp_py.status_code == 200
    py_mentors = resp_py.json()["items"]
    assert len(py_mentors) >= 2
    for m in py_mentors:
        assert m["skill_id"] == 1

    # 3. Discover mentors with min_proficiency = EXPERT
    resp_expert = client.get("/api/v1/mentors?min_proficiency=EXPERT")
    assert resp_expert.status_code == 200
    for m in resp_expert.json()["items"]:
        assert m["proficiency_level"] == "EXPERT"

    # 4. Discover mentors with min_rating = 4.5
    resp_rated = client.get("/api/v1/mentors?min_rating=4.5")
    assert resp_rated.status_code == 200
    for m in resp_rated.json()["items"]:
        assert m["avg_rating"] is not None
        assert m["avg_rating"] >= 4.5
