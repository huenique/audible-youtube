import asyncio
import os
import typing

from aioredis import client
from loguru import logger

from app import settings


async def start_download_expiration(
    redis: client.Redis, ticket: str, fpath: str, seconds: int
) -> None:
    """Remove the specified file and its corresponding ticket after a specified amount
    of time.

    Args:
        redis (Redis): An instance of `aioredis.client.Redis`.
        ticket (str): The ticket for the file.
        fpath (str): The path of the file to remove.
        seconds (int): Time to wait before removing the file and the ticket.
    """
    await asyncio.sleep(seconds)

    if ticket is not None:
        await redis.delete(ticket)  # type: ignore

    try:
        os.unlink(fpath)
        logger.info(f"Removed: {fpath}")
    except FileNotFoundError:
        logger.info(f"Already removed: {fpath}")


async def exec_as_aio(
    blocking_fn: typing.Callable[..., typing.Any], *args: typing.Any
) -> typing.Any:
    """Asynchronously run blocking functions or methods.

    Args:
        blocking_fn (Callable[..., Any]): The blocking function/method.

    Returns:
        Any: The return value of the blocking function/method.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, blocking_fn, *args)


async def validate_duration(
    time: str, postion: int, max: int = settings.MAX_VIDEO_DURATION
) -> bool:
    """Check if the duration of the media is less than or equal to the specified
    maximum value.

    Args:
        time (str): The given duration.
        postion (int): Index of the unit of time to check
            0 - second,
            1 - minute,
            2 - hour
        max (int): The maximum duration.

    Returns:
        bool: True if the duration is valid, False otherwise.
    """
    hms = time.split(":")
    hms.reverse()

    if len(hms) > 2:
        return False

    if postion > 0:
        unit_multiplier = 60
    else:
        unit_multiplier = 1

    if int(hms[postion]) * unit_multiplier >= max:
        return False
    else:
        return True
