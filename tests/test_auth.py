from fastapi.testclient import TestClient
from types import SimpleNamespace
from uuid import uuid4
import sys
import os

# Add parent directory to path for app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.main as main
from app.config import settings


class FakeResponse:
    def __init__(self, json_data):
        self._json = json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        return None


class FakeClient:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, data=None, timeout=None):
        return FakeResponse({"access_token": "fake-access-token"})

    def get(self, url, headers=None, timeout=None):
        return FakeResponse({
            "id": 123456,
            "kakao_account": {"email": "test@example.com"},
            "properties": {"nickname": "TestUser"},
        })


def test_kakao_callback_sets_cookie(monkeypatch):
    # configure settings for test
    settings.kakao_client_id = "dummy"
    settings.kakao_client_secret = ""
    settings.kakao_redirect_uri = "http://test/callback"
    settings.frontend_url = "http://frontend.test/"

    # replace httpx.Client with fake
    monkeypatch.setattr("httpx.Client", FakeClient)

    # replace UserRepository to avoid DB access
    class FakeRepo:
        def __init__(self, db):
            pass

        def get_or_create_from_kakao(self, profile):
            return SimpleNamespace(id=uuid4())

    monkeypatch.setattr("app.routers.auth.UserRepository", FakeRepo)

    client = TestClient(main.app)

    # call callback without following redirect to inspect cookie
    resp = client.get(f"{settings.api_v1_prefix}/auth/kakao/callback?code=abc", allow_redirects=False)

    assert resp.status_code in (302, 307)
    # ensure cookie header present
    cookies = resp.headers.get("set-cookie")
    assert cookies is not None
    assert settings.session_cookie_name in cookies


def test_logout_clears_cookie():
    client = TestClient(main.app)
    resp = client.post(f"{settings.api_v1_prefix}/auth/logout")
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie")
    assert set_cookie is not None
    # cookie should be cleared (Max-Age=0 or expires in past)
    assert settings.session_cookie_name in set_cookie
    assert ("Max-Age=0" in set_cookie) or ("expires=" in set_cookie.lower())
