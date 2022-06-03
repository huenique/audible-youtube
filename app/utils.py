import asyncio
import os
import secrets
from typing import Any, Callable

from loguru import logger


async def start_download_expiration(path: str, seconds: int) -> None:
    await asyncio.sleep(seconds)
    try:
        os.unlink(path)
        logger.info(f"Removed: {path}")
    except FileNotFoundError:
        logger.info(f"Already removed: {path}")


async def generate_ticket() -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, secrets.token_hex, 16)


async def exec_as_aio(blocking_fn: Callable[..., Any], *args: Any):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, blocking_fn, *args)


async def file_exists(path: str) -> bool:
    return await exec_as_aio(os.path.isfile, path)


async def validate_duration(time: str, postion: int, max: int) -> bool:
    """Check if the duration of the media is less than or equal to the specified
    maximum value.

    Args:
        time (str): The given duration.
        postion (int): Index the duration to check
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

    if int(hms[postion]) > max:
        return False
    else:
        return True
