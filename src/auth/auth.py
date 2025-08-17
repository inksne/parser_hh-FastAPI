from fastapi import APIRouter, Depends, Response, Form, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from starlette import status

from .helpers import create_access_token, create_refresh_token
from .validation import get_current_auth_user_for_refresh, validate_auth_user_db
from .schemas import UserSchema

from database.database import get_async_session
from database.managers import psql_manager
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import conflict_name, bad_email_exc, user_exists_exc, server_exc
from config import configure_logging

import logging
from pydantic import BaseModel
from datetime import timedelta


configure_logging()
log = logging.getLogger(__name__)


http_bearer = HTTPBearer(auto_error=False)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


router = APIRouter(prefix='/jwt', tags=["JWT"], dependencies=[Depends(http_bearer)])


@router.post('/register')
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:
    try:
        new_user = await psql_manager.register(username=username, email=email, password=password, session=session)

        if new_user is False:
            raise user_exists_exc
        
        if new_user is None:
            raise conflict_name

        return RedirectResponse('/jwt/login/', status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException:
        raise bad_email_exc
    
    except Exception as e:
        log.error(e)
        raise server_exc


@router.post('/login/', response_model=TokenInfo)
async def auth_user_issue_jwt(response: Response, user: UserSchema = Depends(validate_auth_user_db)) -> TokenInfo:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    response.set_cookie(
        key="access_token",
          value=access_token,
            httponly=False,
              secure=False,
                max_age=int(timedelta(minutes=5).total_seconds()))
    
    response.set_cookie(
        key="refresh_token",
          value=refresh_token,
            httponly=False,
              secure=False,
                max_age=int(timedelta(days=30).total_seconds()))
    
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh/")
async def refresh_jwt(current_user: UserSchema = Depends(get_current_auth_user_for_refresh)) -> JSONResponse:
    new_access_token = create_access_token(current_user)
    response = JSONResponse(content={"access_token": new_access_token})
    response.set_cookie(
        key="access_token",
          value=new_access_token,
            httponly=False,
              secure=False,
                max_age=int(timedelta(minutes=1).total_seconds())) 
    
    return response


@router.post('/logout')
async def logout(response: Response) -> None:
    response.delete_cookie(key="access_token", httponly=False, secure=False)
    response.delete_cookie(key="refresh_token", httponly=False, secure=False)