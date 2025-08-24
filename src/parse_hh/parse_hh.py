from fastapi import APIRouter, Depends

import httpx
import logging
from typing import Any

from .helpers import create_query_params, auth_create_query_params
from .dependencies import get_area_resolver, get_metro_resolver
from auth.validation import get_current_auth_user
from database.models import User
from config import configure_logging, APP_NAME, APP_EMAIL, ACCESS_TOKEN
from basemodels import GetVacanciesModel, AuthGetVacanciesModel
from exceptions import server_exc, api_hh_exc



configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(tags=['Parse_HH'])


@router.get('/get_vacancies')
async def get_vacancies(params: GetVacanciesModel = Depends(), area_resolver: Any = Depends(get_area_resolver)) -> Any:
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'User-Agent': f'{APP_NAME}/1.0 ({APP_EMAIL})'
        }

        query_params = create_query_params(params, area_resolver)

        params_for_httpx: list[tuple[str, str | int | float | bool | None]] = []

        for k, v in query_params.items():
            if v is None:
                continue

            if isinstance(v, (list, tuple)):
                for item in v:
                    params_for_httpx.append((k, str(item)))

            else:
                params_for_httpx.append((k, str(v)))


        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.hh.ru/vacancies',
                headers=headers,
                params=params_for_httpx
            )

            response.raise_for_status()

            logger.warning(response.json())

            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(e)
        raise api_hh_exc

    except Exception as e:
        logger.error(e)
        raise server_exc



@router.get('/authenticated/get_vacancies')
async def auth_get_vacancies(
    params: AuthGetVacanciesModel = Depends(),
    area_resolver: Any = Depends(get_area_resolver),
    metro_resolver: Any = Depends(get_metro_resolver),
    current_user: User = Depends(get_current_auth_user)
) -> Any:
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'User-Agent': f'{APP_NAME}/1.0 ({APP_EMAIL})'
        }

        query_params = auth_create_query_params(params, metro_resolver, area_resolver)

        params_for_httpx: list[tuple[str, str | int | float | bool | None]] = []

        for k, v in query_params.items():
            if v is None:
                continue

            if isinstance(v, (list, tuple)):
                for item in v:
                    params_for_httpx.append((k, str(item)))

            else:
                params_for_httpx.append((k, str(v)))

        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.hh.ru/vacancies',
                headers=headers,
                params=params_for_httpx
            )

            logger.warning(response.json())

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(e)
        raise api_hh_exc

    except Exception as e:
        logger.error(e)
        raise server_exc



@router.get("/get_areas")
async def get_areas() -> Any:
    '''
    использовать только для отладки, а именно - для получения кодов всех доступных стран и регионов
    не использовать на проде, так как сильно нагружает приложение и превышает допустимое время ожидания
    в одном каталоге с данным файлом уже лежит json со всеми кодами стран и регионов
    '''
    
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'User-Agent': f'{APP_NAME}/1.0 ({APP_EMAIL})'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://api.hh.ru/areas',
                headers=headers,
            )

            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(e)
        raise api_hh_exc

    except Exception as e:
        logger.error(e)
        raise server_exc



@router.get("/get_metro")
async def get_metro() -> Any:
    '''
    использовать только для отладки, а именно - для получения кодов всех доступных веток метро
    в одном каталоге с данным файлом уже лежит json с кодами всех веток и станций метро
    '''
    
    try:
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'User-Agent': f'{APP_NAME}/1.0 ({APP_EMAIL})'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.hh.ru/metro',
                headers=headers,
            )
            
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(e)
        raise api_hh_exc
    
    except Exception as e:
        logger.error(e)
        raise server_exc