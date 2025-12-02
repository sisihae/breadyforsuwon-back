from typing import Optional, Dict, Any
from uuid import UUID

import jwt

from app.config import settings


def create_access_token(subject: str, extra: Optional[Dict[str, Any]] = None, expires_delta: Optional[int] = None) -> str:
    import time
    now = int(time.time())
    exp = now + (expires_delta or settings.jwt_exp_seconds)
    payload = {"sub": str(subject), "iat": now, "exp": exp}
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def get_current_user_id(token: Optional[str] = None) -> Optional[UUID]:
    """Extract user_id from JWT token."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if sub:
            return UUID(sub)
    except Exception:
        pass
    return None
