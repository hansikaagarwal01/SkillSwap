import sys
import os
import hashlib
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from app.models.student import Student
from app.core.security import create_access_token

client = TestClient(app)

def test_roll_number_and_email_validation_rules():
    # 1. Invalid Roll Number - unsupported program (MCA)
    resp = client.post("/api/v1/auth/register", json={
        "roll_no": "2025MCA001",
        "name": "Invalid Student",
        "email": "invalid.student@jklu.edu.in",
        "password": "Password@1234",
        "d_id": 1
    })
    assert resp.status_code == 422
    assert "Invalid Roll Number format" in resp.text

    # 2. Lookalike Domain - evil-jklu.edu.in
    resp = client.post("/api/v1/auth/register", json={
        "roll_no": "2025BTECH099",
        "name": "Lookalike Attacker",
        "email": "attacker@evil-jklu.edu.in",
        "password": "Password@1234",
        "d_id": 1
    })
    assert resp.status_code == 422
    assert "Only official JKLU email addresses" in resp.text

    # 3. Lookalike Domain - jklu.edu.in.evil.com
    resp = client.post("/api/v1/auth/register", json={
        "roll_no": "2025BTECH098",
        "name": "Lookalike Attacker",
        "email": "attacker@jklu.edu.in.evil.com",
        "password": "Password@1234",
        "d_id": 1
    })
    assert resp.status_code == 422
    assert "Only official JKLU email addresses" in resp.text

    # 4. Weak password (< 10 chars)
    resp = client.post("/api/v1/auth/register", json={
        "roll_no": "2025BTECH097",
        "name": "Weak Pass User",
        "email": "weak.pass@jklu.edu.in",
        "password": "Short1!",
        "d_id": 1
    })
    assert resp.status_code == 422


def test_registration_and_duplicate_handling():
    db: Session = SessionLocal()
    # Clean up test user if exists
    test_roll = "2026BTECH090"
    test_email = "test.newstudent@jklu.edu.in"
    db.query(Student).filter(Student.roll_no == test_roll).delete()
    db.commit()

    # Successful registration
    resp = client.post("/api/v1/auth/register", json={
        "roll_no": test_roll,
        "name": "New Enrolled Student",
        "email": test_email,
        "password": "StrongPassword@2026",
        "d_id": 1
    })
    assert resp.status_code == 201
    assert "Registration successful" in resp.json()["message"]

    # Duplicate roll_no registration -> 409
    resp_dup_roll = client.post("/api/v1/auth/register", json={
        "roll_no": test_roll,
        "name": "Duplicate Student",
        "email": "different.email@jklu.edu.in",
        "password": "StrongPassword@2026",
        "d_id": 1
    })
    assert resp_dup_roll.status_code == 409
    assert resp_dup_roll.json()["error"]["code"] == "ROLL_NO_EXISTS"

    # Duplicate email registration -> 409
    resp_dup_email = client.post("/api/v1/auth/register", json={
        "roll_no": "2026BTECH091",
        "name": "Another Student",
        "email": test_email,
        "password": "StrongPassword@2026",
        "d_id": 1
    })
    assert resp_dup_email.status_code == 409
    assert resp_dup_email.json()["error"]["code"] == "EMAIL_EXISTS"
    db.close()


def test_email_verification_lifecycle():
    db: Session = SessionLocal()
    test_roll = "2026BTECH090"

    student = db.query(Student).filter(Student.roll_no == test_roll).first()
    assert student is not None
    assert student.verification_token_hash is not None

    # 1. Tampered / invalid token -> 400
    resp_bad = client.post("/api/v1/auth/verify-email", json={"token": "invalid_fake_token_12345"})
    assert resp_bad.status_code == 400
    assert resp_bad.json()["error"]["code"] == "INVALID_TOKEN"

    # Set up a known raw token and hash
    raw_token = "valid_test_token_secret_1234567890"
    student.verification_token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    student.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    db.commit()

    # 2. Valid token verification -> 200
    resp_ok = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert resp_ok.status_code == 200
    assert "Email verified successfully" in resp_ok.json()["message"]

    # 3. Token Reuse -> 400 (cleared on verification)
    resp_reused = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert resp_reused.status_code == 400
    assert resp_reused.json()["error"]["code"] == "INVALID_TOKEN"

    # 4. Expired token -> 400
    student.verification_token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    student.verification_token_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db.commit()

    resp_expired = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert resp_expired.status_code == 400
    assert resp_expired.json()["error"]["code"] == "TOKEN_EXPIRED"

    # Restore active state for subsequent tests
    student.verification_token_hash = None
    student.verification_token_expires_at = None
    student.email_verified = True
    student.account_status = "ACTIVE"
    db.commit()
    db.close()


def test_login_and_jwt_lifecycle():
    # 1. Login with valid credentials
    resp = client.post("/api/v1/auth/login", json={
        "roll_no": "2026BTECH090",
        "password": "StrongPassword@2026"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    token = data["access_token"]

    # 2. Invalid password -> 401
    resp_bad_pw = client.post("/api/v1/auth/login", json={
        "roll_no": "2026BTECH090",
        "password": "WrongPassword@123"
    })
    assert resp_bad_pw.status_code == 401

    # 3. Access /auth/me with valid token -> 200
    resp_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_me.status_code == 200
    me_data = resp_me.json()
    assert me_data["roll_no"] == "2026BTECH090"
    assert me_data["program"] == "BTECH"
    assert me_data["admission_year"] == 2026

    # 4. Access /auth/me with tampered token -> 401
    resp_tampered = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}bad"})
    assert resp_tampered.status_code == 401

    # 5. Token version bump invalidates old token -> 401
    db: Session = SessionLocal()
    student = db.query(Student).filter(Student.roll_no == "2026BTECH090").first()
    student.token_version += 1
    db.commit()
    db.close()

    resp_revoked = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_revoked.status_code == 401
    assert resp_revoked.json()["error"]["code"] == "TOKEN_REVOKED"


def test_unverified_and_suspended_accounts_blocked():
    # Seed data: 2026BTECH016 is UNVERIFIED
    resp_unverified = client.post("/api/v1/auth/login", json={
        "roll_no": "2026BTECH016",
        "password": "Student@JKLU2026"
    })
    assert resp_unverified.status_code == 403
    assert resp_unverified.json()["error"]["code"] == "EMAIL_UNVERIFIED"

    # Seed data: 2026BTECH018 is SUSPENDED
    resp_suspended = client.post("/api/v1/auth/login", json={
        "roll_no": "2026BTECH018",
        "password": "Student@JKLU2026"
    })
    assert resp_suspended.status_code == 403
    assert resp_suspended.json()["error"]["code"] == "ACCOUNT_SUSPENDED"


def test_admin_approval_endpoint():
    db: Session = SessionLocal()
    target_student = db.query(Student).filter(Student.roll_no == "2026BTECH017").first()
    if target_student:
        target_student.account_status = "PENDING_APPROVAL"
        db.commit()
    db.close()

    # Admin logs in
    resp_admin_login = client.post("/api/v1/auth/login", json={
        "roll_no": "2024BTECH001",
        "password": "Admin@JKLU2026"
    })
    assert resp_admin_login.status_code == 200
    admin_token = resp_admin_login.json()["access_token"]

    # Student logs in
    resp_student_login = client.post("/api/v1/auth/login", json={
        "roll_no": "2024BTECH002",
        "password": "Student@JKLU2026"
    })
    assert resp_student_login.status_code == 200
    student_token = resp_student_login.json()["access_token"]

    # Student tries to call admin approve -> 403
    resp_forbidden = client.post(
        "/api/v1/admin/accounts/2026BTECH017/approve",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json()["error"]["code"] == "ADMIN_REQUIRED"

    # Admin approves pending account 2026BTECH017 -> 200
    resp_approve = client.post(
        "/api/v1/admin/accounts/2026BTECH017/approve",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp_approve.status_code == 200
    assert "approved and activated" in resp_approve.json()["message"]
