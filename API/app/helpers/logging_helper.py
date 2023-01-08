import logging
import os
from typing import Any, Callable, Coroutine

from fastapi import Request, Response
from fastapi.logger import logger as fastapi_logger
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask
from starlette.requests import Request as StarletteRequest
from starlette.responses import StreamingResponse


# https://stackoverflow.com/a/73464007
class LoggingRoute(APIRoute):
    @staticmethod
    def log_request_info(request: Request, response: Response, req_body: Request, res_body: Request) -> None:
        logging.info(
            f'URL: {request.url}, '
            f'QUERY_PARAMS: {request.query_params}, '
            f'PATH_PARAMS: {request.path_params}, '
            f'HEADERS: {request.headers}, '
            f'REQUEST_BODY: {req_body}, '
            f'RESPONSE_STATUS: {response.status_code}, '
            f'RESPONSE_BODY: {res_body}, '
        )

    def get_route_handler(self) -> Callable[[StarletteRequest], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_body = await request.body()
            response = await original_route_handler(request)

            if isinstance(response, StreamingResponse):
                res_body = b''
                async for item in response.body_iterator:
                    res_body += item

                task = BackgroundTask(LoggingRoute.log_request_info, request, response, req_body, res_body)
                return Response(content=res_body, status_code=response.status_code,
                                headers=dict(response.headers), media_type=response.media_type, background=task)
            else:
                res_body = response.body
                response.background = BackgroundTask(LoggingRoute.log_request_info, request,
                                                     response, req_body, res_body)
                return response

        return custom_route_handler


# https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker/issues/19#issuecomment-885595200
def set_up_logging() -> None:
    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        gunicorn_error_logger = logging.getLogger("gunicorn.error")
        gunicorn_logger = logging.getLogger("gunicorn")

        fastapi_logger.setLevel(gunicorn_logger.level)
        fastapi_logger.handlers = gunicorn_error_logger.handlers
        root_logger = logging.getLogger()
        root_logger.setLevel(gunicorn_logger.level)

        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.handlers = gunicorn_error_logger.handlers
    else:
        logging_format = """[%(levelname)s] - [%(asctime)s %(process)d:%(threadName)s] %(name)s -
                            %(message)s | %(filename)s:%(lineno)d"""
        logging.basicConfig(
            level=logging.INFO,
            format=logging_format
        )
