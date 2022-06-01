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
