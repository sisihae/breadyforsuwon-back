from fastapi.testclient import TestClient
from types import SimpleNamespace
from uuid import uuid4
from datetime import datetime
import sys
import os

# Add parent directory to path for app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.main as main
from app.config import settings


class FakeUserRepo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id):
        return SimpleNamespace(
            id=user_id,
            email="test@example.com",
            name="Test User",
            kakao_id="123456",
            profile_image=None,
            created_at=datetime.now(),
        )


class FakeVisitRecordRepo:
    def __init__(self, db):
        pass
    
    def list_by_user(self, user_id):
        return [
            SimpleNamespace(id=uuid4()),
            SimpleNamespace(id=uuid4()),
        ]


class FakeWishlistRepo:
    def __init__(self, db):
        pass
    
    def list_by_user(self, user_id):
        return [
            SimpleNamespace(id=uuid4()),
        ]


def test_get_me(monkeypatch):
    user_id = uuid4()

    monkeypatch.setattr("app.routers.auth.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.auth.UserRepository", FakeUserRepo)
    monkeypatch.setattr("app.routers.auth.BakeryVisitRecordRepository", FakeVisitRecordRepo)
    monkeypatch.setattr("app.routers.auth.WishlistRepository", FakeWishlistRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.get(f"{settings.api_v1_prefix}/me")
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["email"] == "test@example.com"
    assert profile["name"] == "Test User"
    assert profile["visit_records_count"] == 2
    assert profile["wishlist_count"] == 1
