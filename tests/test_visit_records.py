from fastapi.testclient import TestClient
from types import SimpleNamespace
from uuid import uuid4
from datetime import date, datetime
import sys
import os

# Add parent directory to path for app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.main as main
from app.config import settings


class FakeVisitRecordRepo:
    def __init__(self, db):
        self.records = {}

    def create(self, user_id, bakery_id, visit_date, rating, bread_purchased=None, review=None):
        record_id = uuid4()
        now = datetime.now()
        self.records[record_id] = SimpleNamespace(
            id=record_id,
            user_id=user_id,
            bakery_id=bakery_id,
            visit_date=visit_date,
            rating=rating,
            bread_purchased=bread_purchased,
            review=review,
            created_at=now,
            updated_at=now,
        )
        return self.records[record_id]

    def get_by_id(self, record_id):
        return self.records.get(record_id)

    def list_by_user(self, user_id):
        return [r for r in self.records.values() if r.user_id == user_id]

    def update(self, record_id, visit_date=None, rating=None, bread_purchased=None, review=None):
        record = self.records.get(record_id)
        if not record:
            return None
        if visit_date is not None:
            record.visit_date = visit_date
        if rating is not None:
            record.rating = rating
        if bread_purchased is not None:
            record.bread_purchased = bread_purchased
        if review is not None:
            record.review = review
        record.updated_at = datetime.now()
        return record

    def delete(self, record_id):
        if record_id in self.records:
            del self.records[record_id]
            return True
        return False


class FakeBakeryRepo:
    def __init__(self, db):
        self.db = db
    
    def get_by_id(self, bakery_id):
        return SimpleNamespace(
            id=bakery_id,
            name="Test Bakery",
            address="123 Main St",
            bread_tags_rel=[],
        )


def test_list_visit_records(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    
    monkeypatch.setattr("app.routers.visit_records.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.visit_records.BakeryVisitRecordRepository", FakeVisitRecordRepo)
    monkeypatch.setattr("app.routers.visit_records.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.get(f"{settings.api_v1_prefix}/visit-records")
    assert resp.status_code == 200
    records = resp.json()
    assert isinstance(records, list)


def test_create_visit_record(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    visit_date = date(2025, 12, 2)
    
    monkeypatch.setattr("app.routers.visit_records.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.visit_records.BakeryVisitRecordRepository", FakeVisitRecordRepo)
    monkeypatch.setattr("app.routers.visit_records.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.post(
        f"{settings.api_v1_prefix}/visit-records",
        json={
            "bakery_id": str(bakery_id),
            "visit_date": "2025-12-02",
            "rating": 5,
            "bread_purchased": "크루아상, 바게트",
            "review": "정말 맛있었어요!"
        },
    )
    assert resp.status_code == 200
    record = resp.json()
    assert record["rating"] == 5
    assert record["bread_purchased"] == "크루아상, 바게트"


def test_update_visit_record(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    visit_date = date(2025, 12, 2)
    
    # Create fake repo with a record
    fake_repo_instance = FakeVisitRecordRepo(None)
    fake_record = fake_repo_instance.create(user_id, bakery_id, visit_date, 4, "크루아상")
    
    monkeypatch.setattr("app.routers.visit_records.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.visit_records.BakeryVisitRecordRepository", lambda db: fake_repo_instance)
    monkeypatch.setattr("app.routers.visit_records.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.patch(
        f"{settings.api_v1_prefix}/visit-records/{fake_record.id}",
        json={"rating": 5, "review": "다시 가고 싶어요!"},
    )
    assert resp.status_code == 200
    record = resp.json()
    assert record["rating"] == 5
    assert record["review"] == "다시 가고 싶어요!"


def test_delete_visit_record(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    visit_date = date(2025, 12, 2)
    
    fake_repo_instance = FakeVisitRecordRepo(None)
    fake_record = fake_repo_instance.create(user_id, bakery_id, visit_date, 4)
    
    monkeypatch.setattr("app.routers.visit_records.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.visit_records.BakeryVisitRecordRepository", lambda db: fake_repo_instance)
    monkeypatch.setattr("app.routers.visit_records.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.delete(f"{settings.api_v1_prefix}/visit-records/{fake_record.id}")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
