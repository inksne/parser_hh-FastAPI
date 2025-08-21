from fastapi import Depends

from typing import Optional, Any

from basemodels import GetVacanciesModel



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



def create_query_params(params: GetVacanciesModel = Depends()) -> dict[str, Any]:
    query_params = {}
        
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

    if params.area:
        query_params['area'] = params.area

    if params.salary:
        query_params['salary'] = params.salary

    if params.currency:
        query_params['currency'] = params.currency

    if params.metro:
        query_params['metro'] = params.metro

    if params.education:
        education = map_education(params.education)

        if education:
            query_params['education'] = education

    if params.work_format:
        work_format = map_work_format(params.work_format)

        if work_format:
            query_params['work_format'] = work_format

    if not params.no_magic:
        query_params['no_magic'] = params.no_magic

    if params.premium:
        query_params['premium'] = params.premium

    if not params.responses_count_enabled:
        query_params['responses_count_enabled'] = params.responses_count_enabled


    query_params['page'] = params.page
    query_params['per_page'] = params.per_page


    return query_params