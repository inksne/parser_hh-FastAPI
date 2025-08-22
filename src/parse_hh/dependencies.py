from fastapi import Request
from .areas_index import AreaResolver 



def get_area_resolver(request: Request) -> AreaResolver:
    return request.app.state.area_resolver