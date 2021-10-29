import os

from fastapi import APIRouter, HTTPException
from fastapi.background import BackgroundTasks
from fastapi.responses import FileResponse
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from youtube_to_audio.models.common import TargetMedia
from youtube_to_audio.services.youtube import YoutubeDownload

router = APIRouter()
ydl = YoutubeDownload()


@router.get("/download", name="Download", response_class=FileResponse)
async def download(
    url: str, _: Request, background_tasks: BackgroundTasks
) -> FileResponse:
    try:
        media = await ydl.save_video(url)
        background_tasks.add_task(os.unlink, media.dl_path)  # type: ignore
        return FileResponse(
            media.dl_path, media_type="audio/m4a", filename=media.dl_name
        )
    except (FileNotFoundError, Exception) as err:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=err)


@router.get("/search", response_model=TargetMedia, name="Search")
async def search(term: str):
    result = await ydl.search_video(term)
    if result:
        return TargetMedia(
            title=result["title"],
            url=result["webpage_url"],
            thumbnail=result["thumbnail"],
            search_term=term,
        )
    raise HTTPException(status_code=HTTP_404_NOT_FOUND)
