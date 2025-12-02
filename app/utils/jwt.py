import time
from typing import Optional, Dict, Any

import jwt

from app.config import settings


def create_access_token(subject: str, extra: Optional[Dict[str, Any]] = None, expires_delta: Optional[int] = None) -> str:
    now = int(time.time())
    exp = now + (expires_delta or settings.jwt_exp_seconds)
    payload = {"sub": str(subject), "iat": now, "exp": exp}
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
