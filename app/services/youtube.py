import asyncio
import os
from pathlib import Path
from typing import Any, Optional, Union

from aioredis.client import Redis
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
from youtubesearchpython import VideosSearch
from youtubesearchpython.__future__ import VideosSearch as AioVideosSearch
from yt_dlp import YoutubeDL as YoutubeDLP
from yt_dlp.utils import DownloadError as DownloadErrorP

from app.services.redis import set_dict
from app.settings import BASE_DIR, FILE_EXPIRE_SECONDS, MEDIA_ROOT
from app.utils import exec_as_aio, start_download_expiration


class FileDownload:
    name: str = ""
    size: str = ""
    path: str = ""

    progress_hook: dict[str, Any] = {
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "outtmpl": os.path.join(
            *f"{BASE_DIR},{MEDIA_ROOT},%(title)s.%(epoch)s.%(ext)s".split(",")
        ),
        "format": "bestaudio[ext=m4a]",
        "progress_hooks": [],
    }


class YoutubeDownload:
    def __init__(self) -> None:
        self.file_download = FileDownload()
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None

    @staticmethod
    def parse_url_str(url: str) -> str:
        # Remove everything after the first occurrence of the separator (&) in the URL.
        if "&list=" in url:
            return "&".join(url.split("&")[:1])
        return url

    @staticmethod
    def search_video(search_term: str) -> Any:
        return VideosSearch(search_term, limit=1).result()  # type: ignore

    @staticmethod
    async def search_video_plus(search_term: str) -> Any:
        return await AioVideosSearch(search_term, limit=1).next()  # type: ignore

    def download_progess_hook(self, download: dict[str, Any]) -> None:
        assert isinstance(self.event_loop, asyncio.AbstractEventLoop)

        if download["status"] == "finished":
            self.file_download.name = Path(download["filename"]).name
            self.file_download.size = str(download["_total_bytes_str"])
            self.file_download.path = download["filename"]
            self.event_loop.create_task(
                start_download_expiration(self.file_download.path, FILE_EXPIRE_SECONDS)
            )

    async def set_progress_hook(self) -> None:
        if self.event_loop is None:
            self.event_loop = asyncio.get_running_loop()

        self.file_download.progress_hook["progress_hooks"] = [
            self.download_progess_hook
        ]

    async def set_ticket(self, redis: Redis, ticket: str) -> None:
        await set_dict(
            redis,
            ticket,
            {"path": self.file_download.path, "name": self.file_download.name},
        )

    async def download_vid(
        self,
        url: str,
        dl_manager: type[Union[YoutubeDL, YoutubeDLP]],
        err: type[Union[DownloadError, DownloadErrorP]],
    ):
        url = self.parse_url_str(url)
        await self.set_progress_hook()

        try:
            with dl_manager(self.file_download.progress_hook) as ydl:
                _ = await exec_as_aio(ydl.extract_info, url)  # type: ignore
        except err:
            result = await self.search_video_plus(url)
            if result is not None:
                await self.download_vid(result["result"][0]["link"], dl_manager, err)

    async def download_video(self, url: str) -> Any:
        await self.download_vid(url, YoutubeDL, DownloadError)

    async def download_video_plus(self, url: str) -> Any:
        await self.download_vid(url, YoutubeDLP, DownloadErrorP)

    async def convert_video(self, video: str, redis: Redis, ticket: str) -> None:
        await self.set_ticket(redis, ticket)
        await self.download_video(video)
        await self.set_ticket(redis, ticket)
