from fastapi import Depends

from typing import Optional, Any

from .areas_index import AreaResolver
from .metro_index import MetroResolver
from basemodels import AuthGetVacanciesModel, GetVacanciesModel



def map_experience(experience: str) -> Optional[str]:
    mapping = {
        'noExperience': 'noExperience',
        'between1And3': 'between1And3',
        'between3And6': 'between3And6',
        'moreThan6': 'moreThan6'
    }

    if experience not in mapping:
        return None

    return mapping.get(experience, experience)


def map_employment_form(employment: str) -> Optional[str]:
    mapping = {
        'FULL': 'FULL',
        'PART': 'PART',
        'PROJECT': 'PROJECT',
        'FLY_IN_FLY_OUT': 'FLY_INI_FLY_OUT'
    }

    if employment not in mapping:
        return None

    return mapping.get(employment, employment)


def map_schedule(schedule: str) -> Optional[str]:
    mapping = {
        'fullDay': 'fullDay',
        'shift': 'shift',
        'flexible': 'flexible',
        'remote': 'remote'
    }

    if schedule not in mapping:
        return None

    return mapping.get(schedule, schedule)


def map_work_format(work_format: str) -> Optional[str]:
    mapping = {
        'ON_SITE': 'ON_SITE',
        'REMOTE': 'REMOTE',
        'HYBRID': 'HYBRID',
        'FIELD_WORK': 'FIELD_WORK'
    }

    if work_format not in mapping:
        return None

    return mapping.get(work_format, work_format)


def map_education(education: str) -> Optional[str]:
    mapping = {
        'not_required_or_not_specified': 'not_required_or_not_specified',
        'special_secondary': 'special_secondary',
        'higher': 'higher',
    }

    if education not in mapping:
        return None

    return mapping.get(education, education)



def auth_create_query_params(
    params: AuthGetVacanciesModel = Depends(),
    metro_resolver: MetroResolver | None = None,
    area_resolver: AreaResolver | None = None
) -> dict[str, Any]:
    query_params: dict[str, Any] = {}

    if params.text:
        query_params['text'] = params.text
        
    if params.experience:
        experience = map_experience(params.experience)

        if experience:
            query_params['experience'] = experience

    if params.employment_form:
        employment_form = map_employment_form(params.employment_form)

        if employment_form:
            query_params['employment_form'] = employment_form

    if params.schedule:
        schedule = map_schedule(params.schedule)

        if schedule:
            query_params['schedule'] = schedule

    if params.area and area_resolver is not None:
        ids = area_resolver.resolve(params.area)

        query_params['area'] = ids

    if params.salary:
        query_params['salary'] = params.salary

    if params.currency:
        query_params['currency'] = params.currency

    if getattr(params, 'metro', None) and metro_resolver is not None:
        station_ids = metro_resolver.resolve(params.metro)
        if station_ids:
            query_params['metro'] = station_ids

    if params.education:
        education = map_education(params.education)

        if education:
            query_params['education'] = education

    if params.work_format:
        work_format = map_work_format(params.work_format)

        if work_format:
            query_params['work_format'] = work_format

    if params.premium:
        query_params['premium'] = params.premium

    if params.only_with_salary:
        query_params['only_with_salary'] = params.only_with_salary

    if not params.responses_count_enabled:
        query_params['responses_count_enabled'] = params.responses_count_enabled


    query_params['page'] = params.page
    query_params['per_page'] = params.per_page
    query_params['no_magic'] = params.no_magic


    return query_params



def create_query_params(
    params: GetVacanciesModel = Depends(), area_resolver: AreaResolver | None = None
) -> dict[str, Any]:
    query_params: dict[str, Any] = {}

    if params.text:
        query_params['text'] = params.text
        
    if params.experience:
        experience = map_experience(params.experience)

        if experience:
            query_params['experience'] = experience

    if params.employment_form:
        employment_form = map_employment_form(params.employment_form)

        if employment_form:
            query_params['employment_form'] = employment_form

    if params.schedule:
        schedule = map_schedule(params.schedule)

        if schedule:
            query_params['schedule'] = schedule

    if params.area and area_resolver is not None:
        ids = area_resolver.resolve(params.area)

        query_params['area'] = ids

    if params.salary:
        query_params['salary'] = params.salary

    if params.work_format:
        work_format = map_work_format(params.work_format)

        if work_format:
            query_params['work_format'] = work_format

    query_params['page'] = params.page
    query_params['per_page'] = params.per_page
    query_params['no_magic'] = params.no_magic


    return query_params
