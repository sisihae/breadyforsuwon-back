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


class FakeChatRepository:
    def __init__(self, db):
        self.histories = {}

    def create_history(self, user_message, bot_response, metadata_json=None):
        history_id = uuid4()
        self.histories[history_id] = SimpleNamespace(
            id=history_id,
            user_message=user_message,
            bot_response=bot_response,
            metadata_json=metadata_json,
            created_at=datetime.now(),
        )
        return self.histories[history_id]

    def get_by_id(self, history_id):
        return self.histories.get(history_id)

    def list_recent(self, limit=100):
        return list(self.histories.values())[:limit]

    def delete_by_id(self, history_id):
        if history_id in self.histories:
            del self.histories[history_id]
            return True
        return False


def test_get_chat_history_by_id(monkeypatch):
    """Test GET /chat/history/{id} endpoint"""
    fake_repo = FakeChatRepository(None)
    history = fake_repo.create_history(
        user_message="수원 빵집 추천해줘",
        bot_response="수원에는 다양한 빵집이 있습니다...",
        metadata_json={"sources": [], "bread_tags": ["Croissant"], "bakery_ids": []},
    )

    monkeypatch.setattr("app.routers.chat_history.ChatRepository", lambda db: fake_repo)

    client = TestClient(main.app)
    resp = client.get(f"{settings.api_v1_prefix}/chat/history/{history.id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(history.id)
    assert data["user_message"] == "수원 빵집 추천해줘"
    assert data["bot_response"] == "수원에는 다양한 빵집이 있습니다..."
    assert "metadata_json" in data


def test_get_chat_history_by_id_not_found(monkeypatch):
    """Test GET /chat/history/{id} with non-existent ID returns 404"""
    fake_repo = FakeChatRepository(None)

    monkeypatch.setattr("app.routers.chat_history.ChatRepository", lambda db: fake_repo)

    client = TestClient(main.app)
    non_existent_id = uuid4()
    resp = client.get(f"{settings.api_v1_prefix}/chat/history/{non_existent_id}")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Chat history not found"


def test_delete_chat_history_by_id(monkeypatch):
    """Test DELETE /chat/history/{id} endpoint"""
    fake_repo = FakeChatRepository(None)
    history = fake_repo.create_history(
        user_message="수원 빵집 추천해줘",
        bot_response="수원에는 다양한 빵집이 있습니다...",
    )

    monkeypatch.setattr("app.routers.chat_history.ChatRepository", lambda db: fake_repo)

    client = TestClient(main.app)
    resp = client.delete(f"{settings.api_v1_prefix}/chat/history/{history.id}")

    assert resp.status_code == 204
    assert resp.text == ""

    # Verify the history was actually deleted
    assert fake_repo.get_by_id(history.id) is None


def test_delete_chat_history_by_id_not_found(monkeypatch):
    """Test DELETE /chat/history/{id} with non-existent ID returns 404"""
    fake_repo = FakeChatRepository(None)

    monkeypatch.setattr("app.routers.chat_history.ChatRepository", lambda db: fake_repo)

    client = TestClient(main.app)
    non_existent_id = uuid4()
    resp = client.delete(f"{settings.api_v1_prefix}/chat/history/{non_existent_id}")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Chat history not found"


def test_list_chat_history(monkeypatch):
    """Test GET /chat/history endpoint (list)"""
    fake_repo = FakeChatRepository(None)
    fake_repo.create_history(
        user_message="첫번째 질문",
        bot_response="첫번째 답변",
    )
    fake_repo.create_history(
        user_message="두번째 질문",
        bot_response="두번째 답변",
    )

    monkeypatch.setattr("app.routers.chat_history.ChatRepository", lambda db: fake_repo)

    client = TestClient(main.app)
    resp = client.get(f"{settings.api_v1_prefix}/chat/history")

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
