from fastapi import APIRouter, Depends, Request, Response, HTTPException, Cookie
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
import httpx
from typing import Optional
from uuid import UUID

from app.config import settings
from app.config.database import get_db
from app.repositories.user_repo import UserRepository
from app.repositories.visit_record_repo import BakeryVisitRecordRepository
from app.repositories.wishlist_repo import WishlistRepository
from app.utils.jwt import create_access_token
from app.utils.auth import get_current_user_id
from app.schemas.user import UserProfileResponse, UserProfileUpdateRequest

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


def get_current_user(session: Optional[str] = Cookie(None)) -> UUID:
    """Dependency to extract user_id from session cookie."""
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = get_current_user_id(session)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: UUID = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile with visit records and wishlist counts."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get counts
    visit_repo = BakeryVisitRecordRepository(db)
    visit_records = visit_repo.list_by_user(current_user)
    visit_records_count = len(visit_records)
    
    wishlist_repo = WishlistRepository(db)
    wishlist_items = wishlist_repo.list_by_user(current_user)
    wishlist_count = len(wishlist_items)
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_image=user.profile_image,
        created_at=user.created_at,
        visit_records_count=visit_records_count,
        wishlist_count=wishlist_count,
    )


@router.put("/me", response_model=UserProfileResponse)
def update_me(
    data: UserProfileUpdateRequest,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile (name and/or profile_image)."""
    user_repo = UserRepository(db)
    user = user_repo.update(current_user, name=data.name, profile_image=data.profile_image)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get counts
    visit_repo = BakeryVisitRecordRepository(db)
    visit_records = visit_repo.list_by_user(current_user)
    visit_records_count = len(visit_records)
    
    wishlist_repo = WishlistRepository(db)
    wishlist_items = wishlist_repo.list_by_user(current_user)
    wishlist_count = len(wishlist_items)
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_image=user.profile_image,
        created_at=user.created_at,
        visit_records_count=visit_records_count,
        wishlist_count=wishlist_count,
    )
