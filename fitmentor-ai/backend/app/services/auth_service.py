"""
Auth business logic. Endpoints stay thin and call into here.
"""
import uuid

from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import AuthProvider, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair, UserLogin, UserRegister


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def _issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def register(self, data: UserRegister) -> tuple[User, TokenPair]:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            auth_provider=AuthProvider.EMAIL,
        )
        user = await self.repo.create(user)
        return user, self._issue_tokens(user)

    async def login(self, data: UserLogin) -> tuple[User, TokenPair]:
        user = await self.repo.get_by_email(data.email)
        if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")
        return user, self._issue_tokens(user)

    async def login_with_google(self, id_token_str: str) -> tuple[User, TokenPair]:
        try:
            claims = google_id_token.verify_oauth2_token(
                id_token_str, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Google token")

        google_sub = claims["sub"]
        email = claims.get("email")
        full_name = claims.get("name", email)

        user = await self.repo.get_by_google_sub(google_sub)
        if not user:
            # Link to an existing email account, or create a new one.
            user = await self.repo.get_by_email(email)
            if user:
                user.google_sub = google_sub
                await self.repo.db.commit()
            else:
                user = User(
                    email=email,
                    full_name=full_name,
                    auth_provider=AuthProvider.GOOGLE,
                    google_sub=google_sub,
                )
                user = await self.repo.create(user)

        return user, self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
        except Exception:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

        user_id = uuid.UUID(payload["sub"])
        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")

        return TokenPair(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )
