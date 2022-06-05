import fastapi
from aioredis import client
from loguru import logger

from app import settings


async def connect_to_redis(app: fastapi.FastAPI) -> None:
    logger.info(f"Connecting to {repr(settings.REDIS_URL)}")
    app.state.redis = client.Redis.from_url(settings.REDIS_URL)  # type: ignore
    logger.info("Established connection to Redis server.")


async def close_redis_connection(app: fastapi.FastAPI) -> None:
    logger.info("Closing connection to Redis server.")
    await app.state.redis.close()
    logger.info("Closed connection to redis server.")
