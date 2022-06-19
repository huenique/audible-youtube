import asyncio
import os
import pathlib
import typing

import requests
import youtube_dl
import yt_dlp
from aioredis import client
from youtubesearchpython import __future__ as ytsearch

from app import settings, utils


class FileDownload:
    name = ""
    size = ""
    path = ""

    progress_hook: dict[str, typing.Any] = {
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "outtmpl": os.path.join(
            *f"{settings.BASE_DIR},{settings.MEDIA_ROOT},%(title)s.%(epoch)s.%(ext)s".split(
                ","
            )
        ),
        "format": "bestaudio[ext=m4a]",
        "progress_hooks": [],
    }


class YtDownloadManager:
    def __init__(self) -> None:
        self.file_download = FileDownload()
        self.event_loop: typing.Optional[asyncio.AbstractEventLoop] = None
        self.client: typing.Optional[client.Redis] = None
        self.ticket: typing.Optional[str] = None
        self.using_yt_dlp = False

    @staticmethod
    def parse_url_str(url: str) -> str:
        # Remove everything after the first occurrence of the separator (&) in the URL.
        if "&list=" in url:
            return "&".join(url.split("&")[:1])
        return url

    @staticmethod
    async def search_video_plus(search_term: str, limit: int) -> typing.Any:
        return await ytsearch.VideosSearch(search_term, limit=limit).next()  # type: ignore

    @staticmethod
    async def search_video_list(search_term: str, list_: int) -> typing.Any:
        loop = asyncio.get_running_loop()
        video: dict[str, typing.Any]

        with yt_dlp.YoutubeDL(
            {
                "match_filter": yt_dlp.utils.match_filter_func("!is_live"),  # type: ignore
                "ignoreerrors": True,
                "no_warnings": True,
                "quiet": True,
                "format": "bestaudio",
                "noplaylist": True,
            }
        ) as ydl:
            try:
                await loop.run_in_executor(None, requests.get, search_term)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.MissingSchema,
            ):
                video = await loop.run_in_executor(
                    None,
                    ydl.extract_info,  # type: ignore
                    f"ytsearch{list_}:{search_term}",
                    False,
                )
            else:
                video = await loop.run_in_executor(
                    None,
                    ydl.extract_info,  # type: ignore
                    search_term,
                    False,
                )

        if "entries" in video:
            return video["entries"]
        else:
            return video

    def download_progess_hook(self, download: dict[str, typing.Any]) -> None:
        if download["status"] == "finished":
            self.file_download.name = pathlib.Path(download["filename"]).name
            self.file_download.size = str(download["_total_bytes_str"])
            self.file_download.path = download["filename"]

            if not self.using_yt_dlp and isinstance(
                self.event_loop, asyncio.AbstractEventLoop
            ):
                if isinstance(self.client, client.Redis) and isinstance(
                    self.ticket, str
                ):
                    self.event_loop.create_task(
                        utils.start_download_expiration(
                            self.client,
                            self.ticket,
                            self.file_download.path,
                            settings.FILE_EXPIRE_SECONDS,
                        )
                    )
                else:
                    raise TypeError(
                        f"{self.using_yt_dlp=}, {self.client=}, {self.ticket=}"
                    )

    async def set_progress_hook(self) -> None:
        if self.event_loop is None:
            self.event_loop = asyncio.get_running_loop()

        self.file_download.progress_hook["progress_hooks"] = [
            self.download_progess_hook
        ]

    async def download_vid(
        self,
        query: str,
        dl_manager: type[typing.Union[youtube_dl.YoutubeDL, yt_dlp.YoutubeDL]],
        err: type[
            typing.Union[youtube_dl.utils.DownloadError, yt_dlp.utils.DownloadError]
        ],
    ):
        query = self.parse_url_str(query)
        await self.set_progress_hook()

        try:
            with dl_manager(self.file_download.progress_hook) as ydl:
                _ = await utils.exec_as_aio(ydl.extract_info, query)  # type: ignore
        except err:
            result = await self.search_video_plus(query, 1)

            if result is not None:
                await self.download_vid(result["result"][0]["link"], dl_manager, err)

    async def download_video(self, query: str) -> typing.Any:
        await self.download_vid(
            query, youtube_dl.YoutubeDL, youtube_dl.utils.DownloadError
        )

    async def download_video_plus(self, query: str) -> typing.Any:
        self.using_yt_dlp = True

        await self.download_vid(query, yt_dlp.YoutubeDL, yt_dlp.utils.DownloadError)

    async def convert_video(
        self, query: str, client: client.Redis, ticket: str
    ) -> None:
        self.client = client
        self.ticket = ticket

        await client.Redis.hmset(  # type: ignore
            self.ticket,
            {"path": self.file_download.path, "name": self.file_download.name},
        )
        await self.download_video(query)

        # The file related attribs will be updated once youtube-dl or yt-dlp finishes,
        # so we call hmset() again.
        await client.Redis.hmset(  # type: ignore
            self.ticket,
            {"path": self.file_download.path, "name": self.file_download.name},
        )
