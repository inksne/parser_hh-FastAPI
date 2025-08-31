from fastapi import APIRouter, Depends

import logging
from typing import List

from .database.managers import psql_manager
from .database.models import User
from .database.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_auth_user
from .basemodels import AddVacancyRequest, VacancyOut
from .config import configure_logging



configure_logging()
logger = logging.getLogger(__name__)


router = APIRouter(prefix='/authenticated/api', tags=['API'])


@router.get('/vacancies')
async def get_all_vacancies_from_db(
    current_user: User = Depends(get_current_auth_user), session: AsyncSession = Depends(get_async_session),
) -> List[VacancyOut]:
    return await psql_manager.get_all_vacancies(current_user, session)



@router.post('/add_vacancy')
async def add_vacancy_to_the_db(
    params: AddVacancyRequest,
    current_user: User = Depends(get_current_auth_user), session: AsyncSession = Depends(get_async_session),
) -> None:
    await psql_manager.add_vacancy(
        params.name, params.experience, params.employment_form, params.work_format, params.schedule,
        params.salary, params.education, params.hh_link, params.premium, current_user, session
    )



@router.delete('/delete_vacancy')
async def delete_vacancy_from_db(
    vacancy_id: int,
    current_user: User = Depends(get_current_auth_user), session: AsyncSession = Depends(get_async_session),
) -> None:
    await psql_manager.delete_vacancy(vacancy_id, session)