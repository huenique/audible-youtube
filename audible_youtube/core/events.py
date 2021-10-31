from typing import Callable

from fastapi import FastAPI
from loguru import logger

from audible_youtube.db.events import close_db_connection, connect_to_db
from audible_youtube.services.events import close_redis_connection, connect_to_redis


def create_start_app_handler(app: FastAPI) -> Callable:  # type: ignore
    async def start_app() -> None:
        await connect_to_redis(app)
        await connect_to_db(app)

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    @logger.catch
    async def stop_app() -> None:
        await close_redis_connection(app)
        await close_db_connection(app)

    return stop_app
