from fastapi.testclient import TestClient
from types import SimpleNamespace
from uuid import uuid4
import sys
import os

# Add parent directory to path for app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.main as main
from app.config import settings


class FakeRepo:
    def __init__(self, db):
        self.items = {}

    def create(self, user_id, bakery_id, note=None):
        item_id = uuid4()
        self.items[item_id] = SimpleNamespace(
            id=item_id,
            user_id=user_id,
            bakery_id=bakery_id,
            note=note,
            visited=False,
            created_at=None,
            updated_at=None,
        )
        return self.items[item_id]

    def get_by_id(self, item_id):
        return self.items.get(item_id)

    def list_by_user(self, user_id):
        return [item for item in self.items.values() if item.user_id == user_id]

    def update(self, item_id, note=None, visited=None):
        item = self.items.get(item_id)
        if not item:
            return None
        if note is not None:
            item.note = note
        if visited is not None:
            item.visited = visited
        return item

    def delete(self, item_id):
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False


class FakeBakeryRepo:
    def get_by_id(self, bakery_id):
        return SimpleNamespace(
            id=bakery_id,
            name="Test Bakery",
            address="123 Main St",
            bread_tags_rel=[SimpleNamespace(name="Croissant"), SimpleNamespace(name="Sourdough")],
        )


def test_list_wishlist(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    
    def mock_get_current_user(session=None):
        return user_id
    
    monkeypatch.setattr("app.routers.wishlist.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.wishlist.WishlistRepository", FakeRepo)
    monkeypatch.setattr("app.routers.wishlist.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    
    # Set session cookie
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.get(f"{settings.api_v1_prefix}/wishlist")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)


def test_create_wishlist_item(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    
    monkeypatch.setattr("app.routers.wishlist.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.wishlist.WishlistRepository", FakeRepo)
    monkeypatch.setattr("app.routers.wishlist.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.post(
        f"{settings.api_v1_prefix}/wishlist",
        json={"bakery_id": str(bakery_id)},
    )
    assert resp.status_code == 200
    item = resp.json()
    assert item["bakery_id"] == str(bakery_id)
    assert item["visited"] is False


def test_update_wishlist_item(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    item_id = uuid4()
    
    # Prepare fake repo with an item
    fake_repo_instance = FakeRepo(None)
    fake_item = fake_repo_instance.create(user_id, bakery_id)
    
    monkeypatch.setattr("app.routers.wishlist.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.wishlist.WishlistRepository", lambda db: fake_repo_instance)
    monkeypatch.setattr("app.routers.wishlist.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.patch(
        f"{settings.api_v1_prefix}/wishlist/{fake_item.id}",
        json={"visited": True, "note": "Great bakery!"},
    )
    assert resp.status_code == 200
    item = resp.json()
    assert item["visited"] is True
    assert item["note"] == "Great bakery!"


def test_delete_wishlist_item(monkeypatch):
    user_id = uuid4()
    bakery_id = uuid4()
    
    fake_repo_instance = FakeRepo(None)
    fake_item = fake_repo_instance.create(user_id, bakery_id)
    
    monkeypatch.setattr("app.routers.wishlist.get_current_user_id", lambda token: user_id)
    monkeypatch.setattr("app.routers.wishlist.WishlistRepository", lambda db: fake_repo_instance)
    monkeypatch.setattr("app.routers.wishlist.BakeryRepository", FakeBakeryRepo)
    
    client = TestClient(main.app)
    client.cookies.set(settings.session_cookie_name, "fake-token")
    
    resp = client.delete(f"{settings.api_v1_prefix}/wishlist/{fake_item.id}")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
