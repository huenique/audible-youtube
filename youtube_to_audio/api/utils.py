import asyncio
import os
from asyncio.events import AbstractEventLoop

from youtube_to_audio.settings import FILE_EXPIRE_SECONDS


async def _start_download_expiration(file_path: str, event_loop: AbstractEventLoop):
    await asyncio.sleep(FILE_EXPIRE_SECONDS)
    await event_loop.run_in_executor(None, os.unlink, file_path)


async def start_download_expiration(file_path: str):
    event_loop = asyncio.get_running_loop()
    event_loop.create_task(_start_download_expiration(file_path, event_loop))
