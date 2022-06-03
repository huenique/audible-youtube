from typing import Any, Sequence

from aioredis.client import Redis
from loguru import logger


@logger.catch
async def get_value(redis: Redis, key: str) -> Any:
    return await redis.get(key)  # type: ignore


@logger.catch
async def get_dict(redis: Redis, key: str, fields: Sequence[Any]) -> Any:
    return await redis.hmget(key, fields)  # type: ignore


@logger.catch
async def set_pair(redis: Redis, key: str, value: str) -> Any:
    return await redis.set(key, value)  # type: ignore


@logger.catch
async def set_dict(redis: Redis, key: str, value: dict[Any, Any]) -> Any:
    return await redis.hmset(key, value)  # type: ignore


@logger.catch
async def ticket_exists(redis: Redis, ticket: str, field: str) -> Any:
    return await redis.hexists(ticket, field)  # type: ignore
