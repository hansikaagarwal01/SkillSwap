import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def get_auth_token(roll_no: str, role: str = "STUDENT") -> str:
    return create_access_token(subject=roll_no, role=role, token_version=1)


def test_inquiry_creation_notification_and_lifecycle():
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    bhavya_token = get_auth_token("2024BTECH002")

    headers_aarav = {"Authorization": f"Bearer {aarav_token}"}
    headers_bhavya = {"Authorization": f"Bearer {bhavya_token}"}

    # 1. Aarav creates a listing
    create_payload = {
        "title": "Lab Coat and Safety Goggles (M)",
        "description": "Clean chemistry lab coat, size M, with shatter-resistant goggles.",
        "price": 300.00,
        "category": "Lab Equipment",
        "item_condition": "LIKE_NEW"
    }
    resp = client.post("/api/v1/listings", json=create_payload, headers=headers_aarav)
    assert resp.status_code == 201
    listing_id = resp.json()["listing_id"]

    # 2. Bhavya submits an inquiry to Aarav
    inquiry_msg = "Hello Aarav, I need this lab coat for next week's chemistry lab. Can we meet near the academic block?"
    inq_resp = client.post(
        f"/api/v1/marketplace/listings/{listing_id}/inquiries",
        json={"message": inquiry_msg},
        headers=headers_bhavya
    )
    assert inq_resp.status_code == 201
    inquiry_data = inq_resp.json()
    assert inquiry_data["listing_id"] == listing_id
    assert inquiry_data["buyer_roll_no"] == "2024BTECH002"
    assert inquiry_data["buyer_name"] == "Bhavya Patel"
    assert inquiry_data["buyer_email"] == "bhavya.patel@jklu.edu.in"
    assert inquiry_data["seller_roll_no"] == "2024BTECH001"
    assert inquiry_data["seller_name"] == "Aarav Sharma"
    assert inquiry_data["seller_email"] == "aarav.sharma@jklu.edu.in"
    assert inquiry_data["inquiry_status"] == "PENDING"
    assert inquiry_data["email_delivery_status"] in ["SKIPPED", "SENT"]
    inquiry_id = inquiry_data["inquiry_id"]

    # 3. Aarav receives in-app notification
    notif_resp = client.get("/api/v1/notifications?unread_only=true", headers=headers_aarav)
    assert notif_resp.status_code == 200
    notifs = notif_resp.json()["items"]
    assert len(notifs) >= 1
    target_notif = next((n for n in notifs if n["inquiry_id"] == inquiry_id), None)
    assert target_notif is not None
    assert "New Marketplace Inquiry" in target_notif["title"]
    assert "Bhavya Patel" in target_notif["message"]
    assert target_notif["is_read"] is False
    notification_id = target_notif["notification_id"]

    # 4. Check unread count
    count_resp = client.get("/api/v1/notifications/unread-count", headers=headers_aarav)
    assert count_resp.status_code == 200
    assert count_resp.json()["unread_count"] >= 1

    # 5. Aarav marks notification as read
    read_resp = client.patch(f"/api/v1/notifications/{notification_id}/read", headers=headers_aarav)
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True

    # 6. Aarav views received inquiries
    rec_resp = client.get("/api/v1/marketplace/inquiries/received", headers=headers_aarav)
    assert rec_resp.status_code == 200
    rec_items = rec_resp.json()["items"]
    assert any(i["inquiry_id"] == inquiry_id for i in rec_items)

    # 7. Bhavya views sent inquiries
    sent_resp = client.get("/api/v1/marketplace/inquiries/sent", headers=headers_bhavya)
    assert sent_resp.status_code == 200
    sent_items = sent_resp.json()["items"]
    assert any(i["inquiry_id"] == inquiry_id for i in sent_items)

    # 8. Aarav updates inquiry status to RESPONDED
    status_resp = client.patch(
        f"/api/v1/marketplace/inquiries/{inquiry_id}/status",
        json={"status": "RESPONDED"},
        headers=headers_aarav
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["inquiry_status"] == "RESPONDED"


def test_inquiry_business_rules_and_security():
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    bhavya_token = get_auth_token("2024BTECH002")
    chirag_token = get_auth_token("2024BTECH003")

    headers_aarav = {"Authorization": f"Bearer {aarav_token}"}
    headers_bhavya = {"Authorization": f"Bearer {bhavya_token}"}
    headers_chirag = {"Authorization": f"Bearer {chirag_token}"}

    # 1. Aarav creates a listing
    resp = client.post("/api/v1/listings", json={
        "title": "Scientific Graphing Calculator (Casio)",
        "description": "Programmable, allowed in JKLU engineering examinations.",
        "price": 850.00,
        "category": "Electronics",
        "item_condition": "GOOD"
    }, headers=headers_aarav)
    listing_id = resp.json()["listing_id"]

    # 2. Self-inquiry rejected (400 Bad Request)
    resp_self = client.post(
        f"/api/v1/marketplace/listings/{listing_id}/inquiries",
        json={"message": "Inquiring about my own listing"},
        headers=headers_aarav
    )
    assert resp_self.status_code == 400
    assert "own listing" in resp_self.json()["error"]["message"].lower()

    # 3. Nonexistent listing (404 Not Found)
    resp_404 = client.post(
        "/api/v1/marketplace/listings/999999/inquiries",
        json={"message": "Does this nonexistent listing exist?"},
        headers=headers_bhavya
    )
    assert resp_404.status_code == 404

    # 4. Bhavya creates valid inquiry
    resp_valid = client.post(
        f"/api/v1/marketplace/listings/{listing_id}/inquiries",
        json={"message": "Can you bring this to the lab tomorrow?"},
        headers=headers_bhavya
    )
    assert resp_valid.status_code == 201
    inquiry_id = resp_valid.json()["inquiry_id"]

    # 5. Chirag (unauthorized student) attempts to update inquiry status -> 403 Forbidden
    resp_unauth = client.patch(
        f"/api/v1/marketplace/inquiries/{inquiry_id}/status",
        json={"status": "CLOSED"},
        headers=headers_chirag
    )
    assert resp_unauth.status_code == 403

    # 6. Aarav marks all notifications as read
    resp_readall = client.patch("/api/v1/notifications/read-all", headers=headers_aarav)
    assert resp_readall.status_code == 200

