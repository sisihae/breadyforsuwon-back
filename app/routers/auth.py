from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
import httpx
from typing import Optional

from app.config import settings
from app.config.database import get_db
from app.repositories.user_repo import UserRepository
from app.utils.jwt import create_access_token

router = APIRouter()


@router.get("/auth/kakao/login")
def kakao_login():
    """Return Kakao OAuth authorize URL for frontend to redirect user to."""
    base = "https://kauth.kakao.com/oauth/authorize"
    params = {
        "client_id": settings.kakao_client_id,
        "redirect_uri": settings.kakao_redirect_uri,
        "response_type": "code",
    }
    # build url
    url = f"{base}?client_id={params['client_id']}&redirect_uri={params['redirect_uri']}&response_type=code"
    return JSONResponse({"authorize_url": url})


@router.get("/auth/kakao/callback")
def kakao_callback(code: Optional[str] = None, db: Session = Depends(get_db)):
    """Callback handler: exchange code -> token, fetch profile, create/find user, set session cookie."""
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.kakao_client_id,
        "redirect_uri": settings.kakao_redirect_uri,
        "code": code,
    }
    if settings.kakao_client_secret:
        data["client_secret"] = settings.kakao_client_secret

    try:
        with httpx.Client() as client:
            token_resp = client.post(token_url, data=data, timeout=10.0)
            token_resp.raise_for_status()
            token_json = token_resp.json()

            access_token = token_json.get("access_token")
            if not access_token:
                raise HTTPException(status_code=500, detail="Failed to obtain access token")

            # fetch profile
            profile_url = "https://kapi.kakao.com/v2/user/me"
            profile_resp = client.get(profile_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10.0)
            profile_resp.raise_for_status()
            profile = profile_resp.json()

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"OAuth request failed: {e}")

    # create or find user
    repo = UserRepository(db)
    user = repo.get_or_create_from_kakao(profile)

    # create JWT and set as cookie
    token = create_access_token(subject=str(user.id))
    response = RedirectResponse(url=settings.frontend_url)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.jwt_exp_seconds,
        path="/",
    )
    return response


@router.post("/auth/logout")
def kakao_logout(response: Response):
    """Clear the session cookie to log out the user."""
    resp = JSONResponse({"ok": True})
    # Clear cookie by setting empty value and max-age=0
    resp.delete_cookie(key=settings.session_cookie_name, path="/")
    return resp
