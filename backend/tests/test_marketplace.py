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

    # 2. Bhavya purchases the listing -> 200 OK
    resp_buy = client.post(f"/api/v1/listings/{listing_id}/purchase", headers=headers_bhavya)
    assert resp_buy.status_code == 200
    bought = resp_buy.json()
    assert bought["status"] == "SOLD"
    assert bought["buyer_roll_no"] == "2024BTECH002"
    assert bought["sold_at"] is not None

    # 3. Chirag tries to purchase the already SOLD listing -> 409 Conflict
    resp_second_buy = client.post(f"/api/v1/listings/{listing_id}/purchase", headers=headers_chirag)
    assert resp_second_buy.status_code == 409
    assert "already been sold" in resp_second_buy.json()["error"]["message"].lower()

    # 4. Modifying or deleting a SOLD listing is rejected (400 Bad Request)
    resp_edit_sold = client.patch(f"/api/v1/listings/{listing_id}", json={"price": 400.00}, headers=headers_aarav)
    assert resp_edit_sold.status_code == 400

    resp_del_sold = client.delete(f"/api/v1/listings/{listing_id}", headers=headers_aarav)
    assert resp_del_sold.status_code == 400

    # 5. Check Bhavya's purchases endpoint
    resp_purchases = client.get("/api/v1/listings/purchases", headers=headers_bhavya)
    assert resp_purchases.status_code == 200
    bought_ids = [item["listing_id"] for item in resp_purchases.json()["items"]]
    assert listing_id in bought_ids


def test_concurrent_marketplace_purchases():
    """
    CONCURRENCY TEST:
    Multiple threads concurrently attempt to purchase the EXACT SAME available listing.
    Ensures safe atomic concurrency:
    UPDATE listing SET status='SOLD', buyer_roll_no=:buyer, sold_at=NOW()
    WHERE listing_id=:id AND status='AVAILABLE' AND seller_roll_no <> :buyer;
    Exactly 1 buyer must succeed (HTTP 200), all other concurrent attempts must receive HTTP 409.
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

    # Verify DB state directly
    db = SessionLocal()
    final_listing = db.query(Listing).filter(Listing.listing_id == target_listing_id).first()
    assert final_listing.status == "SOLD"
    assert final_listing.buyer_roll_no in buyer_rolls
    assert final_listing.sold_at is not None
    db.close()


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
