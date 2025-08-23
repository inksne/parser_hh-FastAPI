from fastapi import Request
from typing import Any 



def get_area_resolver(request: Request) -> Any:
    return request.app.state.area_resolver