from pydantic import BaseModel
from typing import Optional



class GetVacanciesModel(BaseModel):
    page: Optional[int] = 0
    per_page: Optional[int] = 20
    text: Optional[str] = None
    experience: Optional[str] = None
    employment_form: Optional[str] = None
    work_format: Optional[str] = None
    schedule: Optional[str] = None
    area: Optional[str] = None
    salary: Optional[str] = None
    no_magic: Optional[bool] = True


class AuthGetVacanciesModel(BaseModel):
    page: Optional[int] = 0
    per_page: Optional[int] = 20
    text: Optional[str] = None
    experience: Optional[str] = None
    employment_form: Optional[str] = None
    work_format: Optional[str] = None
    schedule: Optional[str] = None
    area: Optional[str] = None
    salary: Optional[str] = None
    currency: Optional[str] = None
    metro: Optional[str] = None
    education: Optional[str] = None
    only_with_salary: Optional[bool] = False
    no_magic: Optional[bool] = False
    premium: Optional[bool] = False
    responses_count_enabled: Optional[bool] = True


class AddVacancyRequest(BaseModel):
    name: str
    experience: str
    employment_form: str
    work_format: str
    schedule: str
    salary: int
    education: str
    hh_link: str
    premium: bool


class VacancyOut(BaseModel):
    id: int
    name: str
    experience: str
    employment_form: str
    work_format: str
    schedule: str
    salary: int
    education: str
    hh_link: str
    premium: bool

    model_config = {"from_attributes": True}