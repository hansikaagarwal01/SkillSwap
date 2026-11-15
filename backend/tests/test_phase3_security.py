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
from app.models.notification import Notification
from app.models.inquiry import MarketplaceInquiry
from app.models.listing import Listing
from app.core.security import create_access_token, get_password_hash, hash_token, generate_verification_token

client = TestClient(app)


def test_unauthenticated_verification_bypass_removed():
    """Verify that the unauthenticated account verification bypass endpoint has been removed."""
    resp = client.post("/api/v1/auth/verify-account/2026BTECH016")
    assert resp.status_code == 404

    # Verify student remains UNVERIFIED in the database
    db: Session = SessionLocal()
    student = db.query(Student).filter(Student.roll_no == "2026BTECH016").first()
    assert student is not None
    assert student.account_status == "UNVERIFIED"
    assert student.email_verified is False
    db.close()


def test_email_verification_token_lifecycle_and_single_use():
    """Test cryptographic token verification, expiry, single-use enforcement, and activation."""
    db: Session = SessionLocal()
    test_roll = "2026BTECH080"
    test_email = "token.test@jklu.edu.in"
    db.query(Student).filter(Student.roll_no == test_roll).delete()
    db.commit()

    # 1. Register new student -> status UNVERIFIED
    resp_reg = client.post("/api/v1/auth/register", json={
        "roll_no": test_roll,
        "name": "Token Lifecycle Student",
        "email": test_email,
        "password": "StrongPassword@2026",
        "d_id": 1
    })
    assert resp_reg.status_code == 201
    assert "Please verify your email" in resp_reg.json()["message"]

    student = db.query(Student).filter(Student.roll_no == test_roll).first()
    assert student is not None
    assert student.account_status == "UNVERIFIED"
    assert student.email_verified is False
    assert student.verification_token_hash is not None

    # 2. Invalid token rejection -> 400
    resp_invalid = client.post("/api/v1/auth/verify-email", json={"token": "completely_fake_token_12345"})
    assert resp_invalid.status_code == 400
    assert resp_invalid.json()["error"]["code"] == "INVALID_TOKEN"

    # Set known valid token
    raw_token = generate_verification_token()
    student.verification_token_hash = hash_token(raw_token)
    student.verification_token_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db.commit()

    # 3. Expired token rejection -> 400
    resp_expired = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert resp_expired.status_code == 400
    assert resp_expired.json()["error"]["code"] == "TOKEN_EXPIRED"

    # Set unexpired token
    student.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    db.commit()

    # 4. Valid token verification -> 200 & active
    resp_valid = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert resp_valid.status_code == 200
    assert "verified" in resp_valid.json()["message"].lower()

    # 5. Single-use: Reusing the same token -> 400 INVALID_TOKEN
    resp_reused = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert resp_reused.status_code == 400
    assert resp_reused.json()["error"]["code"] == "INVALID_TOKEN"

    # 6. Account is now active and can login
    resp_login = client.post("/api/v1/auth/login", json={
        "roll_no": test_roll,
        "password": "StrongPassword@2026"
    })
    assert resp_login.status_code == 200
    assert "access_token" in resp_login.json()

    # Cleanup
    db.query(Student).filter(Student.roll_no == test_roll).delete()
    db.commit()
    db.close()


def test_resend_verification_and_rate_limiting():
    """Test resending verification emails safely without email enumeration."""
    db: Session = SessionLocal()
    test_roll = "2026BTECH081"
    test_email = "resend.test@jklu.edu.in"
    db.query(Student).filter(Student.roll_no == test_roll).delete()
    db.commit()

    # Register unverified student
    client.post("/api/v1/auth/register", json={
        "roll_no": test_roll,
        "name": "Resend Test Student",
        "email": test_email,
        "password": "StrongPassword@2026",
        "d_id": 1
    })

    # Resend verification
    resp_resend = client.post("/api/v1/auth/resend-verification", json={"email": test_email})
    assert resp_resend.status_code == 200
    assert "verification link has been sent" in resp_resend.json()["message"]

    # Resend to non-existent email returns generic safe message
    resp_nonexistent = client.post("/api/v1/auth/resend-verification", json={"email": "nonexistent@jklu.edu.in"})
    assert resp_nonexistent.status_code == 200
    assert "verification link has been sent" in resp_nonexistent.json()["message"]

    # Cleanup
    db.query(Student).filter(Student.roll_no == test_roll).delete()
    db.commit()
    db.close()


def test_database_backed_rbac_and_admin_protection():
    """Test database-backed role persistence and administrative endpoint authorization."""
    aarav_token = create_access_token(subject="2024BTECH001", role="ADMIN", token_version=1)
    bhavya_token = create_access_token(subject="2024BTECH002", role="STUDENT", token_version=1)

    db: Session = SessionLocal()
    # Confirm roles in database
    aarav = db.query(Student).filter(Student.roll_no == "2024BTECH001").first()
    bhavya = db.query(Student).filter(Student.roll_no == "2024BTECH002").first()
    assert aarav is not None and aarav.role == "ADMIN"
    assert bhavya is not None and bhavya.role == "STUDENT"

    # Set up pending approval student for test
    target_student = db.query(Student).filter(Student.roll_no == "2026BTECH017").first()
    if target_student:
        target_student.account_status = "PENDING_APPROVAL"
        db.commit()
    db.close()

    # 1. Student accessing admin endpoint -> 403 ADMIN_REQUIRED
    resp_forbidden = client.post(
        "/api/v1/admin/accounts/2026BTECH017/approve",
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json()["error"]["code"] == "ADMIN_REQUIRED"

    # 2. Administrator accessing admin endpoint -> 200
    resp_approved = client.post(
        "/api/v1/admin/accounts/2026BTECH017/approve",
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_approved.status_code == 200
    assert "approved and activated" in resp_approved.json()["message"]

    # 3. Student attempting to modify their own role via PATCH /students/{roll} -> 422 extra forbid
    resp_role_tamper = client.patch(
        "/api/v1/students/2024BTECH002",
        json={"role": "ADMIN"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_role_tamper.status_code == 422

    # Verify role was not changed in database
    db = SessionLocal()
    bhavya_db = db.query(Student).filter(Student.roll_no == "2024BTECH002").first()
    assert bhavya_db.role == "STUDENT"
    db.close()


def test_user_profile_and_resource_authorization():
    """Verify ownership checks and forbidden access for cross-user operations."""
    bhavya_token = create_access_token(subject="2024BTECH002", role="STUDENT", token_version=1)

    # 1. Bhavya attempts to edit Aarav's student profile -> 403
    resp_edit_other = client.patch(
        "/api/v1/students/2024BTECH001",
        json={"name": "Hacked Profile"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_edit_other.status_code == 403
    assert resp_edit_other.json()["error"]["code"] == "FORBIDDEN"

    # 2. Bhavya attempts to edit Aarav's experience -> 403
    resp_edit_exp = client.patch(
        "/api/v1/experiences/2024BTECH001/1",
        json={"role_title": "Hacked Title"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_edit_exp.status_code == 403
    assert resp_edit_exp.json()["error"]["code"] == "FORBIDDEN"

    # 3. Bhavya attempts to delete Aarav's experience -> 403
    resp_del_exp = client.delete(
        "/api/v1/experiences/2024BTECH001/1",
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_del_exp.status_code == 403
    assert resp_del_exp.json()["error"]["code"] == "FORBIDDEN"


def test_user_isolation_notifications_and_sessions():
    """Test user isolation: notifications and marketplace inquiries are strictly isolated between accounts."""
    aarav_token = create_access_token(subject="2024BTECH001", role="ADMIN", token_version=1)
    bhavya_token = create_access_token(subject="2024BTECH002", role="STUDENT", token_version=1)

    db: Session = SessionLocal()
    # Find a listing owned by Aarav
    listing = db.query(Listing).filter(Listing.seller_roll_no == "2024BTECH001", Listing.status == "AVAILABLE").first()
    assert listing is not None
    listing_id = listing.listing_id
    db.close()

    # Bhavya sends an inquiry on Aarav's listing
    resp_inq = client.post(
        f"/api/v1/marketplace/listings/{listing_id}/inquiries",
        json={"message": "Is this still available for library exchange?"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_inq.status_code == 201
    inquiry_id = resp_inq.json()["inquiry_id"]

    # 1. Aarav fetches notifications -> inquiry notification is present
    resp_aarav_notifs = client.get(
        "/api/v1/notifications?page_size=20",
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_aarav_notifs.status_code == 200
    aarav_items = resp_aarav_notifs.json()["items"]
    target_notif = next((n for n in aarav_items if n.get("inquiry_id") == inquiry_id), None)
    assert target_notif is not None
    notif_id = target_notif["notification_id"]

    # 2. Bhavya fetches notifications -> Aarav's notification MUST NOT appear
    resp_bhavya_notifs = client.get(
        "/api/v1/notifications?page_size=20",
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_bhavya_notifs.status_code == 200
    bhavya_items = resp_bhavya_notifs.json()["items"]
    assert not any(n["notification_id"] == notif_id for n in bhavya_items)

    # 3. Bhavya attempts to mark Aarav's notification as read -> 404
    resp_tamper_notif = client.patch(
        f"/api/v1/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_tamper_notif.status_code == 404

    # 4. Marketplace inquiries scoping: Bhavya's sent inquiries contains inquiry_id, Aarav's sent does not
    resp_bhavya_sent = client.get(
        "/api/v1/marketplace/inquiries/sent",
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_bhavya_sent.status_code == 200
    assert any(i["inquiry_id"] == inquiry_id for i in resp_bhavya_sent.json()["items"])

    resp_aarav_sent = client.get(
        "/api/v1/marketplace/inquiries/sent",
        headers={"Authorization": f"Bearer {aarav_token}"}
    )
    assert resp_aarav_sent.status_code == 200
    assert not any(i["inquiry_id"] == inquiry_id for i in resp_aarav_sent.json()["items"])

    # 5. Non-seller Bhavya attempts to update inquiry status -> 403
    resp_tamper_status = client.patch(
        f"/api/v1/marketplace/inquiries/{inquiry_id}/status",
        json={"status": "RESPONDED"},
        headers={"Authorization": f"Bearer {bhavya_token}"}
    )
    assert resp_tamper_status.status_code == 403

    # Cleanup inquiry & notification
    db = SessionLocal()
    db.query(Notification).filter(Notification.notification_id == notif_id).delete()
    db.query(MarketplaceInquiry).filter(MarketplaceInquiry.inquiry_id == inquiry_id).delete()
    db.commit()
    db.close()
