from aioredis.client import Redis
from fastapi import FastAPI
from loguru import logger
from redis import Redis as _Redis
from rq import Queue, pop_connection

from audible_youtube.settings import REDIS_URL


async def connect_to_redis(app: FastAPI) -> None:
    logger.info(f"Connecting to {repr(REDIS_URL)}")
    app.state.redis = Redis.from_url(REDIS_URL)  # type: ignore
    app.state.queue = Queue(connection=_Redis.from_url(REDIS_URL))
    logger.info("Established connection to Redis server.")


async def close_redis_connection(app: FastAPI) -> None:
    logger.info("Closing connection to Redis server.")
    app.state.redis.close()
    pop_connection()
    logger.info("Closed connection to redis server.")
