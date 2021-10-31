import asyncio
import os
from asyncio.events import AbstractEventLoop
from pathlib import Path
from typing import Any, Optional

from aioredis.client import Redis
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError

from audible_youtube.services.redis import set_dict
from audible_youtube.settings import BASE_DIR, MEDIA_ROOT
from audible_youtube.utils import start_download_expiration

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


class YoutubeVideo:
    filename: str = ""
    file_size: str = ""
    file_path: str = ""

    @staticmethod
    def search_video(search_term: str) -> Any:
        with YoutubeDL(YDL_OPTS) as ydl:
            result: Optional[dict[str, Any]] = None
            result = ydl.extract_info(  # type: ignore
                f"ytsearch:{search_term}", download=False
            )
            assert result is not None
            return result["entries"][0]

    async def set_file_expiration(self) -> None:
        asyncio.create_task(
            start_download_expiration(self.file_path, FILE_EXPIRE_SECONDS)
        )

    async def set_ticket(self, redis: Redis, ticket: str) -> None:
        await set_dict(
            redis, ticket, {"file_path": self.file_path, "filename": self.filename}
        )

    def download_progess_hook(self, download: dict[str, Any]):
        if download["status"] == "finished":
            self.filename = Path(download["filename"]).name
            self.file_size = str(download["_total_bytes_str"])
            self.file_path = download["filename"]

    def download_video(
        self, url: str, redis: Redis, ticket: str, loop: AbstractEventLoop
    ) -> "YoutubeVideo":
        # Remove everything after the first occurrence of the separator (&) in the URL.
        if "&list=" in url:
            url = "&".join(url.split("&")[:1])

        YDL_OPTS["progress_hooks"] = [self.download_progess_hook]

        try:
            with YoutubeDL(YDL_OPTS) as ydl:
                _ = ydl.extract_info(url)  # type: ignore
        except DownloadError:
            result = self.search_video(url)
            if result is not None:
                self.download_video(result["webpage_url"], redis, ticket, loop)

        return self

    async def save_video(self, video: str, redis: Redis, ticket: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self.download_video, video, redis, ticket, loop
        )
        await self.set_ticket(redis, ticket)
        await self.set_file_expiration()
