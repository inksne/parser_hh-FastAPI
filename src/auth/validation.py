from fastapi import Depends, HTTPException, Request, Form
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import logging
from typing import Any, Callable, Coroutine

from .helpers import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from .utils import decode_jwt, validate_password
from .schemas import UserSchema
from ..database.database import get_async_session
from ..database.models import User
from ..config import configure_logging
from ..exceptions import (
    bad_token_exc,
    not_found_access_exc,
    not_found_refresh_exc,
    not_found_token_user_exc,
    unauthed_exc,
    bad_email_exc
)


configure_logging()
logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login")


def get_current_access_token_payload(request: Request) -> Any:
    '''получение access токена'''
    token = request.cookies.get("access_token")
    if not token:
        raise not_found_access_exc
    
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError:
        raise bad_token_exc
    
    return payload


def get_current_refresh_token_payload(request: Request) -> Any:
    '''получение refresh токена'''
    token = request.cookies.get("refresh_token")
    if not token:
        raise not_found_refresh_exc
    
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError:
        raise bad_token_exc
    
    return payload


def validate_token_type(payload: dict[str, Any], token_type: str) -> bool:
    '''проверка на подходящий токен (используется в разных случаях)'''
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Неверный тип токена {current_token_type!r}, ожидается: {token_type!r}"
    )


def get_current_auth_user_from_access_token_of_type(
        token_type: str
    ) -> Callable[[dict[str, Any], AsyncSession], Coroutine[Any, Any, User]]:
    '''проверка access токена'''
    async def get_auth_user_from_token(
            payload: dict[str, Any] = Depends(get_current_access_token_payload),
            db: AsyncSession = Depends(get_async_session)
        ) -> User:

        validate_token_type(payload, token_type)

        return await get_user_by_token_sub(payload, db)
    
    return get_auth_user_from_token


def get_current_auth_user_from_refresh_token_of_type(
        token_type: str
    ) -> Callable[[dict[str, Any], AsyncSession], Coroutine[Any, Any, User]]:
    '''проверка refresh токена'''
    async def get_auth_user_from_token(
            payload: dict[str, Any] = Depends(get_current_refresh_token_payload),
            db: AsyncSession = Depends(get_async_session)
        ) -> User:

        validate_token_type(payload, token_type)

        return await get_user_by_token_sub(payload, db)
    
    return get_auth_user_from_token


get_current_auth_user = get_current_auth_user_from_access_token_of_type(ACCESS_TOKEN_TYPE)

get_current_auth_user_for_refresh = get_current_auth_user_from_refresh_token_of_type(REFRESH_TOKEN_TYPE)

async def get_user_by_token_sub(payload: dict[str, Any], db: AsyncSession) -> User:
    '''получение пользователя по access токену'''
    username: str | None = payload.get("sub")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if user is None:
        raise not_found_token_user_exc

    return user


async def validate_auth_user_db(
        username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_async_session)
    ) -> UserSchema:
    '''валидация введенных пользователем данных (используется для входа)'''
    result_user = await db.execute(select(User).where(User.username == username))
    user = result_user.scalars().first()  

    if not user:
        raise unauthed_exc
    
    if not validate_password(password=password, hashed_password=user.password.encode('utf-8')):
        raise unauthed_exc
    
    return UserSchema.from_attributes(user)


def validate_email(email: str) -> None:
    if email in [None, '', 'null'] or '@' not in email or '.' not in email:
        raise bad_email_exc