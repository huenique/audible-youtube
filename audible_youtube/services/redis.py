from typing import Any, Sequence

from aioredis.client import Redis


async def get_value(redis: Any, key: str) -> Any:
    assert isinstance(redis, Redis)
    value: Any = await redis.get(key)  # type: ignore
    return value


async def get_dict(redis: Any, key: str, dict_keys: Sequence[Any]) -> Any:
    assert isinstance(redis, Redis)
    value: Any = await redis.hmget(key, dict_keys)  # type: ignore
    return value


async def set_pair(redis: Any, key: str, value: str) -> None:
    assert isinstance(redis, Redis)
    await redis.set(key, value)  # type: ignore


async def set_dict(redis: Any, key: str, value: dict[Any, Any]) -> None:
    assert isinstance(redis, Redis)
    await redis.hmset(key, value)  # type: ignore
