from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session
from database.models import User
from database.managers import psql_manager

from auth import get_current_auth_user
from config import configure_logging


configure_logging()
log = logging.getLogger(__name__)


router = APIRouter(tags=['Templates'])


templates = Jinja2Templates(directory='templates')



@router.get("/", response_class=HTMLResponse)
async def get_base_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, "index.html")


@router.get('/about_us', response_class=HTMLResponse)
async def get_about_us_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, 'about_us.html')


@router.get('/jwt/register', response_class=HTMLResponse)
async def get_register_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, 'register.html')


@router.get('/jwt/login/', response_class=HTMLResponse)
async def get_login_page(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request, 'login.html')


@router.get('/authenticated/', response_class=HTMLResponse)
async def get_auth_page(request: Request, current_user: User = Depends(get_current_auth_user)) -> _TemplateResponse:
    return templates.TemplateResponse(request, "authenticated.html")