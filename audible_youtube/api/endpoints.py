import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from audible_youtube.api.utils import start_download_expiration
from audible_youtube.models.common import TargetMedia
from audible_youtube.services.youtube import YoutubeVideo

router = APIRouter()
youtube = YoutubeVideo()


@router.get("/download", name="Download", response_class=FileResponse)
async def download(video: str, _: Request) -> FileResponse:
    try:
        media = await youtube.download_video(video)
        await start_download_expiration(media.file_path)
        return FileResponse(
            media.file_path,
            media_type="audio/m4a",
            background=BackgroundTask(os.unlink, media.file_path),
            filename=media.filename,
        )
    except (FileNotFoundError, RuntimeError) as err:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=err)


@router.get("/search", response_model=TargetMedia, name="Search")
async def search(term: str):
    result = await youtube.search_video(term)
    if result:
        return TargetMedia(
            title=result["title"],
            url=result["webpage_url"],
            thumbnail=result["thumbnail"],
            search_term=term,
        )
    raise HTTPException(status_code=HTTP_404_NOT_FOUND)
