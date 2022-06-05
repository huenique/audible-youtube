from aioredis.client import Redis
from fastapi import FastAPI
from loguru import logger

from app.settings import REDIS_URL


async def connect_to_redis(app: FastAPI) -> None:
    logger.info(f"Connecting to {repr(REDIS_URL)}")
    app.state.redis = Redis.from_url(REDIS_URL)  # type: ignore
    logger.info("Established connection to Redis server.")


async def close_redis_connection(app: FastAPI) -> None:
    logger.info("Closing connection to Redis server.")
    await app.state.redis.close()
    logger.info("Closed connection to redis server.")
