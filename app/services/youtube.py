import asyncio
import os
from pathlib import Path
from typing import Any

from aioredis.client import Redis
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
from youtubesearchpython import VideosSearch
from youtubesearchpython.__future__ import VideosSearch as AioVideosSearch
from yt_dlp import YoutubeDL as YoutubeDLP
from yt_dlp.utils import DownloadError as DownloadErrorP

from app.services.redis import set_dict
from app.settings import BASE_DIR, MEDIA_ROOT
from app.utils import start_download_expiration

YOUTUBE_URL = "https://youtube.com"
FILE_DIR = "{BASE_DIR},{MEDIA_ROOT}"
YDL_OPTS: dict[str, Any] = {
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "outtmpl": os.path.join(
        *f"{BASE_DIR},{MEDIA_ROOT},%(title)s.%(epoch)s.%(ext)s".split(",")
    ),
    "format": "bestaudio[ext=m4a]",
    "progress_hooks": [],
}
FILE_EXPIRE_SECONDS = 300


class YoutubeDownload:
    filename: str = ""
    file_size: str = ""
    file_path: str = ""

    @staticmethod
    def parse_url_str(url: str) -> str:
        # Remove everything after the first occurrence of the separator (&) in the URL.
        if "&list=" in url:
            return "&".join(url.split("&")[:1])
        return url

    @staticmethod
    def search_video(search_term: str) -> Any:
        return VideosSearch(search_term, limit=1).result()  # type: ignore

    async def set_file_expiration(self) -> None:
        asyncio.create_task(
            start_download_expiration(self.file_path, FILE_EXPIRE_SECONDS)
        )

    async def set_ticket(self, redis: Redis, ticket: str) -> None:
        await set_dict(
            redis, ticket, {"file_path": self.file_path, "filename": self.filename}
        )

    def download_progess_hook(self, download: dict[str, Any]) -> None:
        if download["status"] == "finished":
            self.filename = Path(download["filename"]).name
            self.file_size = str(download["_total_bytes_str"])
            self.file_path = download["filename"]

    def set_progress_hook(self) -> None:
        YDL_OPTS["progress_hooks"] = [self.download_progess_hook]

    def download_video(self, url: str) -> Any:
        url = self.parse_url_str(url)
        self.set_progress_hook()

        try:
            with YoutubeDL(YDL_OPTS) as ydl:
                _ = ydl.extract_info(url)  # type: ignore
        except DownloadError:
            result = self.search_video(url)
            if result is not None:
                self.download_video(result["webpage_url"])

    async def save_video(self, video: str, redis: Redis, ticket: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.download_video, video)
        await self.set_ticket(redis, ticket)
        await self.set_file_expiration()


class YoutubeDownloadP(YoutubeDownload):
    @staticmethod
    async def search_video(search_term: str) -> Any:
        return await AioVideosSearch(search_term, limit=1).next()  # type: ignore

    async def download_video(self, url: str) -> Any:
        url = self.parse_url_str(url)
        self.set_progress_hook()

        try:
            with YoutubeDLP(YDL_OPTS) as ydl:
                _ = ydl.extract_info(url)  # type: ignore
        except DownloadErrorP:
            result = await self.search_video(url)
            if result is not None:
                await self.download_video(result["result"][0]["link"])
