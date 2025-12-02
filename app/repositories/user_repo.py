from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_kakao_id(self, kakao_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.kakao_id == kakao_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, kakao_id: Optional[str] = None, email: Optional[str] = None, name: Optional[str] = None) -> User:
        user = User(kakao_id=kakao_id, email=email, name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_or_create_from_kakao(self, kakao_profile: dict) -> User:
        kakao_id = str(kakao_profile.get("id"))
        kakao_account = kakao_profile.get("kakao_account", {})
        email = kakao_account.get("email")
        properties = kakao_profile.get("properties", {})
        name = properties.get("nickname") or kakao_account.get("profile", {}).get("nickname")

        user = self.get_by_kakao_id(kakao_id)
        if user:
            # optionally update email/name if changed
            updated = False
            if email and user.email != email:
                user.email = email
                updated = True
            if name and user.name != name:
                user.name = name
                updated = True
            if updated:
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            return user

        # try find by email
        if email:
            user = self.get_by_email(email)
            if user:
                user.kakao_id = kakao_id
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                return user

        # create new
        return self.create(kakao_id=kakao_id, email=email, name=name)

    def update(self, user_id: str, name: Optional[str] = None, profile_image: Optional[str] = None) -> Optional[User]:
        """Update user profile (name and/or profile_image)"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        if name is not None:
            user.name = name
        if profile_image is not None:
            user.profile_image = profile_image
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
