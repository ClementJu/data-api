from fastapi import APIRouter, Response

from app.helpers.logging_helper import LoggingRoute

health_router = APIRouter(
    prefix='/health',
    tags=['health'],
    responses={404: {'description': 'Not found'}},
    route_class=LoggingRoute
)


@health_router.get("")
async def get_health_status(response: Response) -> str:
    response.status_code = 200
    return 'Ok'
