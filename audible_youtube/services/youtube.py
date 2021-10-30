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
Result = Union[Any, None]


class YoutubeDownload:

    dl_name = ""
    dl_size = ""
    dl_path = ""

    def _download_progess_hook(self, download: dict[str, Any]):
        if download["status"] == "finished":
            self.dl_size = str(download["_total_bytes_str"])
            self.dl_name = Path(download["filename"]).name
            self.dl_path = download["filename"]

    def _search_video(self, search_term: str) -> Result:
        with YoutubeDL({"format": "bestaudio", "noplaylist": "True"}) as ydl:
            result: Optional[dict[str, Any]] = None
            result = ydl.extract_info(  # type: ignore
                f"ytsearch:{search_term}", download=False
            )
            if result:
                return result["entries"][0]

    def _save_video(self, url: str) -> "YoutubeDownload":
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
                self._save_video(result["webpage_url"])

        return self

    async def search_video(self, url: str) -> Result:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._search_video, url)

    async def save_video(self, url: str) -> "YoutubeDownload":
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._save_video, url)
