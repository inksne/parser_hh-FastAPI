from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

import logging
from typing import Optional, List

from ..auth.utils import hash_password
from ..auth.validation import validate_email
from ..basemodels import VacancyOut
from .models import User, Vacancy
from ..exceptions import bad_email_exc, server_exc
from ..config import configure_logging



configure_logging()
log = logging.getLogger(__name__)


class PSQLManager:
    async def register(self, username: str, email: str, password: str, session: AsyncSession) -> Optional[bool]:
        try:
            result_user = await session.execute(select(User).where(User.username == username, User.email == email))
            user = result_user.scalar_one_or_none()

            if user:
                return False
            
            hashed_password = hash_password(password).decode('utf-8')
            validate_email(email)

            new_user = User(username=username, email=email, password=hashed_password)

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return True

        except IntegrityError:
            return None
        
        except HTTPException:
            raise bad_email_exc
        
        except Exception as e:
            log.error(e)
            raise server_exc


    async def add_vacancy(
        self,
        name: str, experience: str, employment_form: str, work_format: str,
        schedule: str, salary: int, education: str, hh_link: str, premium: bool,
        current_user: User, session: AsyncSession
    ) -> None:
        try:
            new_vacancy = Vacancy(
                name=name, experience=experience, employment_form=employment_form, work_format=work_format,
                schedule=schedule, salary=salary, education=education, hh_link=hh_link, premium=premium, user_id=current_user.id
            )

            session.add(new_vacancy)
            await session.commit()
            await session.refresh(new_vacancy)

        except Exception as e:
            log.error(e)
            raise server_exc


    async def get_all_vacancies(self, current_user: User, session: AsyncSession) -> List[VacancyOut]:
        try:
            result_vacancies = await session.execute(select(Vacancy).where(Vacancy.user_id == current_user.id))
            vacancies = result_vacancies.scalars().all()

            return [VacancyOut.model_validate(v) for v in vacancies]

        except Exception as e:
            log.error(e)
            raise server_exc


    async def delete_vacancy(self, vacancy_id: int, session: AsyncSession) -> None:
        try:
            result_vacancy = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
            vacancy = result_vacancy.scalar_one_or_none()

            await session.delete(vacancy)
            await session.commit()

        except Exception as e:
            log.error(e)
            raise server_exc


psql_manager = PSQLManager()