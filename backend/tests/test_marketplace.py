import sys
import os
import concurrent.futures
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from app.models.listing import Listing
from app.core.security import create_access_token

client = TestClient(app)

def get_auth_token(roll_no: str, role: str = "STUDENT") -> str:
    return create_access_token(subject=roll_no, role=role, token_version=1)


def test_listings_listing_filtering_and_pagination():
    # 1. Fetch seed listings
    resp = client.get("/api/v1/listings?page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total"] >= 10
    assert len(data["items"]) == 5

    # 2. Filter by category
    resp_cats = client.get("/api/v1/listings/categories")
    assert resp_cats.status_code == 200
    cats = resp_cats.json()
    assert "Textbooks" in cats

    resp_books = client.get("/api/v1/listings?category=Textbooks")
    assert resp_books.status_code == 200
    items = resp_books.json()["items"]
    assert len(items) > 0
    assert all(i["category"] == "Textbooks" for i in items)

    # 3. Filter by status AVAILABLE
    resp_avail = client.get("/api/v1/listings?status=AVAILABLE")
    assert resp_avail.status_code == 200
    for item in resp_avail.json()["items"]:
        assert item["status"] == "AVAILABLE"

    # 4. Search keyword
    resp_search = client.get("/api/v1/listings?search=Calculator")
    assert resp_search.status_code == 200
    calc_items = resp_search.json()["items"]
    assert len(calc_items) >= 1
    assert "Calculator" in calc_items[0]["title"] or "calculator" in calc_items[0]["description"].lower()


def test_listing_crud_and_permissions():
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    bhavya_token = get_auth_token("2024BTECH002")

    headers_aarav = {"Authorization": f"Bearer {aarav_token}"}
    headers_bhavya = {"Authorization": f"Bearer {bhavya_token}"}

    # 1. Aarav creates a listing
    create_payload = {
        "title": "Raspberry Pi 4 Model B (4GB)",
        "description": "Like-new condition, with power supply and acrylic case.",
        "price": 3500.00,
        "category": "Electronics",
        "item_condition": "LIKE_NEW"
    }
    resp = client.post("/api/v1/listings", json=create_payload, headers=headers_aarav)
    assert resp.status_code == 201
    listing = resp.json()
    listing_id = listing["listing_id"]
    assert listing["seller_roll_no"] == "2024BTECH001"
    assert listing["status"] == "AVAILABLE"
    assert float(listing["price"]) == 3500.00

    # 2. Bhavya attempts to update Aarav's listing -> 403 Forbidden
    update_payload = {"price": 3200.00}
    resp_unauth = client.patch(f"/api/v1/listings/{listing_id}", json=update_payload, headers=headers_bhavya)
    assert resp_unauth.status_code == 403

    # 3. Aarav updates his own listing -> 200 OK
    resp_update = client.patch(f"/api/v1/listings/{listing_id}", json=update_payload, headers=headers_aarav)
    assert resp_update.status_code == 200
    assert float(resp_update.json()["price"]) == 3200.00

    # 4. Verify in /mine
    resp_mine = client.get("/api/v1/listings/mine", headers=headers_aarav)
    assert resp_mine.status_code == 200
    my_ids = [item["listing_id"] for item in resp_mine.json()["items"]]
    assert listing_id in my_ids


def test_purchase_lifecycle_and_business_rules():
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    bhavya_token = get_auth_token("2024BTECH002")
    chirag_token = get_auth_token("2024BTECH003")

    headers_aarav = {"Authorization": f"Bearer {aarav_token}"}
    headers_bhavya = {"Authorization": f"Bearer {bhavya_token}"}
    headers_chirag = {"Authorization": f"Bearer {chirag_token}"}

    # Create listing by Aarav
    create_payload = {
        "title": "Mechanical Engineering Drawing Board",
        "description": "Standard university drawing board with T-square and clips.",
        "price": 450.00,
        "category": "Stationery",
        "item_condition": "GOOD"
    }
    resp = client.post("/api/v1/listings", json=create_payload, headers=headers_aarav)
    assert resp.status_code == 201
    listing_id = resp.json()["listing_id"]

    # 1. Self-purchase rejected (400 Bad Request)
    resp_self = client.post(f"/api/v1/listings/{listing_id}/purchase", headers=headers_aarav)
    assert resp_self.status_code == 400
    assert "cannot purchase your own listing" in resp_self.json()["error"]["message"].lower()

    # 2. Bhavya requests to purchase the listing -> 200 OK, status IN_PROGRESS
    resp_buy = client.post(f"/api/v1/listings/{listing_id}/purchase", headers=headers_bhavya)
    assert resp_buy.status_code == 200
    bought = resp_buy.json()
    assert bought["status"] == "IN_PROGRESS"
    assert bought["buyer_roll_no"] == "2024BTECH002"
    assert bought["sold_at"] is None

    # 3. Chirag tries to purchase the IN_PROGRESS listing -> 409 Conflict
    resp_second_buy = client.post(f"/api/v1/listings/{listing_id}/purchase", headers=headers_chirag)
    assert resp_second_buy.status_code == 409
    assert "in progress" in resp_second_buy.json()["error"]["message"].lower()

    # 4. Cancel and re-purchase test
    # Chirag cannot cancel Bhavya's deal -> 403 Forbidden
    resp_cancel_chirag = client.post(f"/api/v1/listings/{listing_id}/cancel-sale", headers=headers_chirag)
    assert resp_cancel_chirag.status_code == 403

    # Bhavya cancels the purchase request -> 200 OK, status AVAILABLE
    resp_cancel = client.post(f"/api/v1/listings/{listing_id}/cancel-sale", headers=headers_bhavya)
    assert resp_cancel.status_code == 200
    assert resp_cancel.json()["status"] == "AVAILABLE"
    assert resp_cancel.json()["buyer_roll_no"] is None

    # Bhavya re-requests purchase -> status IN_PROGRESS
    resp_re_buy = client.post(f"/api/v1/listings/{listing_id}/purchase", headers=headers_bhavya)
    assert resp_re_buy.status_code == 200
    assert resp_re_buy.json()["status"] == "IN_PROGRESS"

    # 5. Seller (Aarav) confirms payment and hands over item -> 200 OK, status SOLD
    resp_confirm = client.post(f"/api/v1/listings/{listing_id}/confirm-sale", headers=headers_aarav)
    assert resp_confirm.status_code == 200
    sold_data = resp_confirm.json()
    assert sold_data["status"] == "SOLD"
    assert sold_data["buyer_roll_no"] == "2024BTECH002"
    assert sold_data["sold_at"] is not None

    # 6. Chirag tries to purchase the now SOLD listing -> 409 Conflict
    resp_third_buy = client.post(f"/api/v1/listings/{listing_id}/purchase", headers=headers_chirag)
    assert resp_third_buy.status_code == 409
    assert "already been sold" in resp_third_buy.json()["error"]["message"].lower()

    # 7. Modifying or deleting a SOLD listing is rejected (400 Bad Request)
    resp_edit_sold = client.patch(f"/api/v1/listings/{listing_id}", json={"price": 400.00}, headers=headers_aarav)
    assert resp_edit_sold.status_code == 400

    resp_del_sold = client.delete(f"/api/v1/listings/{listing_id}", headers=headers_aarav)
    assert resp_del_sold.status_code == 400

    # 8. Check Bhavya's purchases endpoint
    resp_purchases = client.get("/api/v1/listings/purchases", headers=headers_bhavya)
    assert resp_purchases.status_code == 200
    bought_ids = [item["listing_id"] for item in resp_purchases.json()["items"]]
    assert listing_id in bought_ids


def test_concurrent_marketplace_purchases():
    """
    CONCURRENCY TEST:
    Multiple threads concurrently attempt to purchase the EXACT SAME available listing.
    Ensures safe atomic concurrency:
    UPDATE listing SET status='IN_PROGRESS', buyer_roll_no=:buyer
    WHERE listing_id=:id AND status='AVAILABLE' AND seller_roll_no <> :buyer;
    Exactly 1 buyer must succeed (HTTP 200), all other concurrent attempts must receive HTTP 409.
    Then the seller confirms the sale to transition to SOLD.
    """
    aarav_token = get_auth_token("2024BTECH001", "ADMIN")
    headers_aarav = {"Authorization": f"Bearer {aarav_token}"}

    create_payload = {
        "title": "Rare Limited Edition JKLU IEEE Robocon T-Shirt (M)",
        "description": "Mint condition collector item from 2024 competition.",
        "price": 200.00,
        "category": "Merchandise",
        "item_condition": "NEW"
    }
    resp = client.post("/api/v1/listings", json=create_payload, headers=headers_aarav)
    assert resp.status_code == 201
    target_listing_id = resp.json()["listing_id"]

    buyer_rolls = ["2024BTECH002", "2024BTECH003", "2024BTECH004", "2024BTECH005", "2024BTECH006"]

    def attempt_purchase(roll: str) -> int:
        token = get_auth_token(roll)
        resp = client.post(
            f"/api/v1/listings/{target_listing_id}/purchase",
            headers={"Authorization": f"Bearer {token}"}
        )
        return resp.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(attempt_purchase, roll) for roll in buyer_rolls]
        status_codes = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Assert exactly 1 HTTP 200 and 4 HTTP 409
    successes = [code for code in status_codes if code == 200]
    conflicts = [code for code in status_codes if code == 409]

    assert len(successes) == 1, f"Expected exactly 1 purchase success, got {len(successes)} (results: {status_codes})"
    assert len(conflicts) == 4, f"Expected 4 conflicts, got {len(conflicts)} (results: {status_codes})"

    # Verify DB state directly (status should be IN_PROGRESS)
    db = SessionLocal()
    in_progress_listing = db.query(Listing).filter(Listing.listing_id == target_listing_id).first()
    assert in_progress_listing.status == "IN_PROGRESS"
    assert in_progress_listing.buyer_roll_no in buyer_rolls
    assert in_progress_listing.sold_at is None
    db.close()

    # Aarav (seller) confirms the sale
    resp_confirm = client.post(f"/api/v1/listings/{target_listing_id}/confirm-sale", headers=headers_aarav)
    assert resp_confirm.status_code == 200
    assert resp_confirm.json()["status"] == "SOLD"
    assert resp_confirm.json()["sold_at"] is not None


def test_leaderboard_and_analytics_overview():
    # 1. Leaderboard
    resp_lb = client.get("/api/v1/leaderboard?limit=10")
    assert resp_lb.status_code == 200
    lb_data = resp_lb.json()
    assert len(lb_data) > 0
    # Assert sorted by reputation points descending
    reputations = [item["reputation_points"] for item in lb_data]
    assert reputations == sorted(reputations, reverse=True)
    # Assert rank starts at 1
    assert lb_data[0]["rank"] == 1

    # 2. Analytics Overview
    resp_an = client.get("/api/v1/analytics/overview")
    assert resp_an.status_code == 200
    an_data = resp_an.json()
    assert an_data["total_students"] >= 30
    assert an_data["total_skills"] >= 15
    assert an_data["total_sessions"] >= 30
    assert an_data["total_listings"] >= 10

    # Programs breakdown check
    programs = [p["program"] for p in an_data["programs"]]
    assert "BTECH" in programs
    assert "BBA" in programs
    assert "BDES" in programs

    # Marketplace stats check
    mp = an_data["marketplace"]
    assert mp["total_listings"] >= 10
    assert mp["available_listings"] >= 1
    assert mp["sold_listings"] >= 1
    assert mp["total_volume"] > 0


def test_listing_edit_delete_authz_and_in_progress_guard():
    from app.core.security import create_access_token

    headers_aarav = {
        "Authorization": f"Bearer {create_access_token(subject='2024BTECH001', role='ADMIN', token_version=1)}"
    }
    headers_bhavya = {
        "Authorization": f"Bearer {create_access_token(subject='2024BTECH002', role='STUDENT', token_version=1)}"
    }

    cats_resp = client.get("/api/v1/listings/categories")
    assert cats_resp.status_code == 200
    category = cats_resp.json()[0] if cats_resp.json() else "General"

    resp_create = client.post(
        "/api/v1/listings",
        json={
            "title": "Phase 2 Test Calculator",
            "description": "Scientific calculator in good condition for DBMS verification.",
            "price": 600,
            "category": category,
            "item_condition": "GOOD",
        },
        headers=headers_aarav,
    )
    assert resp_create.status_code == 201
    listing_id = resp_create.json()["listing_id"]

    try:
        # 1. Non-owner cannot edit or delete -> 403
        resp_forbid_patch = client.patch(
            f"/api/v1/listings/{listing_id}",
            json={"title": "Tampered Title", "price": 10},
            headers=headers_bhavya,
        )
        assert resp_forbid_patch.status_code == 403

        resp_forbid_del = client.delete(
            f"/api/v1/listings/{listing_id}",
            headers=headers_bhavya,
        )
        assert resp_forbid_del.status_code == 403

        # 2. Owner edits AVAILABLE listing -> 200 & persisted
        resp_patch = client.patch(
            f"/api/v1/listings/{listing_id}",
            json={"title": "Updated Scientific Calculator", "price": 450},
            headers=headers_aarav,
        )
        assert resp_patch.status_code == 200
        assert resp_patch.json()["title"] == "Updated Scientific Calculator"
        assert float(resp_patch.json()["price"]) == 450.0

        resp_get = client.get(f"/api/v1/listings/{listing_id}")
        assert resp_get.status_code == 200
        assert resp_get.json()["title"] == "Updated Scientific Calculator"

        # 3. Buyer initiates purchase -> status becomes IN_PROGRESS
        resp_buy = client.post(
            f"/api/v1/listings/{listing_id}/purchase",
            headers=headers_bhavya,
        )
        assert resp_buy.status_code == 200
        assert resp_buy.json()["status"] == "IN_PROGRESS"

        # 4. Seller cannot edit or delete while IN_PROGRESS -> 400
        resp_blocked_patch = client.patch(
            f"/api/v1/listings/{listing_id}",
            json={"price": 999},
            headers=headers_aarav,
        )
        assert resp_blocked_patch.status_code == 400

        resp_blocked_del = client.delete(
            f"/api/v1/listings/{listing_id}",
            headers=headers_aarav,
        )
        assert resp_blocked_del.status_code == 400

        # 5. Seller cancels in-progress sale -> returns to AVAILABLE
        resp_cancel = client.post(
            f"/api/v1/listings/{listing_id}/cancel-sale",
            headers=headers_aarav,
        )
        assert resp_cancel.status_code == 200
        assert resp_cancel.json()["status"] == "AVAILABLE"

        # 6. Seller deletes AVAILABLE listing -> 204 & gone
        resp_del = client.delete(
            f"/api/v1/listings/{listing_id}",
            headers=headers_aarav,
        )
        assert resp_del.status_code == 204

        resp_gone = client.get(f"/api/v1/listings/{listing_id}")
        assert resp_gone.status_code == 404
    finally:
        db = SessionLocal()
        listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
        if listing is not None:
            db.delete(listing)
            db.commit()
        db.close()
