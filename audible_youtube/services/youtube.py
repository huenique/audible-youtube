import asyncio
import os
from pathlib import Path
from typing import Any, Optional, Union

from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError

from audible_youtube.settings import BASE_DIR, MEDIA_ROOT

YOUTUBE_URL = "https://youtube.com"
FILE_DIR = "{BASE_DIR},{MEDIA_ROOT}"
YDL_OPTS: dict[str, Any] = {
    "quiet": True,
    "no_warnings": True,
    "outtmpl": os.path.join(
        *f"{BASE_DIR},{MEDIA_ROOT},%(title)s.%(epoch)s.%(ext)s".split(",")
    ),
    "format": "bestaudio[ext=m4a]",
    "progress_hooks": [],
}
SearchResult = Union[Any, None]


class YoutubeVideo:
    filename: str = ""
    file_size: str = ""
    file_path: str = ""

    def _download_progess_hook(self, download: dict[str, Any]):
        if download["status"] == "finished":
            self.filename = Path(download["filename"]).name
            self.file_size = str(download["_total_bytes_str"])
            self.file_path = download["filename"]

    def _search_video(self, search_term: str) -> SearchResult:
        with YoutubeDL({"format": "bestaudio", "noplaylist": "True"}) as ydl:
            result: Optional[dict[str, Any]] = None
            result = ydl.extract_info(  # type: ignore
                f"ytsearch:{search_term}", download=False
            )
            if result:
                return result["entries"][0]

    def _download_video(self, url: str) -> "YoutubeVideo":
        # Remove everything after the first occurrence of the separator (&) in the URL.
        if "&list=" in url:
            url = "&".join(url.split("&")[:1])

        YDL_OPTS["progress_hooks"] = [self._download_progess_hook]

        try:
            with YoutubeDL(YDL_OPTS) as ydl:
                _ = ydl.extract_info(url)  # type: ignore
        except DownloadError:
            result = self._search_video(url)
            if result is not None:
                self._download_video(result["webpage_url"])

        return self

    async def search_video(self, term: str) -> SearchResult:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._search_video, term)

    async def download_video(self, url: str) -> "YoutubeVideo":
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._download_video, url)
