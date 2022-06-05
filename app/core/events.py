import typing

import fastapi
from loguru import logger

from app.services import events


def create_start_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    async def start_app() -> None:
        await events.connect_to_redis(app)

    return start_app


def create_stop_app_handler(app: fastapi.FastAPI) -> typing.Callable[..., typing.Any]:
    @logger.catch
    async def stop_app() -> None:
        await events.close_redis_connection(app)

    return stop_app
