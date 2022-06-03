import asyncio
import os

from aioredis.client import Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_507_INSUFFICIENT_STORAGE,
)

from app.api.dependencies import get_redis_connection
from app.models import common
from app.services import redis as _redis
from app.services import youtube
from app.utils import file_exists, generate_ticket, valid_duration

MAX_VIDEO_DURATION = 900

router = APIRouter()


@router.get("/download", name="Download")
async def download(video: str, _: Request, bg_tasks: BackgroundTasks) -> FileResponse:
    media = youtube.YoutubeDownloadPlus()
    await media.download_video(video)
    bg_tasks.add_task(os.unlink, media.path)  # type: ignore

    return FileResponse(
        media.file_download.path,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=media.file_download.name,
    )


@router.get("/save", name="Save")
async def save(
    ticket: str,
    _: Request,
    bg_tasks: BackgroundTasks,
    redis: Redis = Depends(get_redis_connection),
) -> FileResponse:
    file = await _redis.get_dict(redis, ticket, ("path", "name"))

    if all(value is None for value in file):
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"{ticket} is not ready. Please wait and resubmit your request",
        )

    file = [value.decode("utf-8") for value in file]
    path, name = file[0], file[1]

    if not await file_exists(path):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"{ticket}'s file is missing or has been removed from filesystem",
        )

    bg_tasks.add_task(os.unlink, path)  # type: ignore

    return FileResponse(
        path,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=name,
    )


@router.get("/convert", response_model=common.Ticket, name="Convert")
async def convert(
    video: str, _: Request, redis: Redis = Depends(get_redis_connection)
) -> common.Ticket:
    try:
        ticket = await generate_ticket()
        result = await youtube.YoutubeDownloadPlus.search_video(video)
        result = result["result"][0]
        title = result["title"]
        duration = result["duration"]

        if not await valid_duration(duration, 1, MAX_VIDEO_DURATION):
            raise HTTPException(
                status_code=HTTP_507_INSUFFICIENT_STORAGE,
                detail=f"video exceeds {MAX_VIDEO_DURATION} seconds: {duration}, {title}",
            )

        asyncio.create_task(
            youtube.YoutubeDownload().convert_video(video, redis, ticket)
        )

        return common.Ticket(
            ticket=ticket,
            title=title,
            link=result["link"],
            thumbnails=result["thumbnails"],
        )
    except (KeyError, AttributeError) as key_err:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR) from key_err


@router.get("/search", response_model=common.TargetMedia, name="Search")
async def search(term: str, _: Request) -> common.TargetMedia:
    result = await youtube.YoutubeDownloadPlus.search_video(term)
    result = result["result"][0]

    try:
        return common.TargetMedia(
            title=result["title"],
            link=result["link"],
            thumbnails=result["thumbnails"],
        )
    except KeyError as key_err:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR) from key_err
