from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    GoogleLoginRequest,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", response_model=TokenPair, status_code=201)
async def register(data: UserRegister, service: AuthService = Depends(get_auth_service)):
    _, tokens = await service.register(data)
    return tokens


@router.post("/login", response_model=TokenPair)
async def login(data: UserLogin, service: AuthService = Depends(get_auth_service)):
    _, tokens = await service.login(data)
    return tokens


@router.post("/google", response_model=TokenPair)
async def google_login(data: GoogleLoginRequest, service: AuthService = Depends(get_auth_service)):
    _, tokens = await service.login_with_google(data.id_token)
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    return await service.refresh(data.refresh_token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
