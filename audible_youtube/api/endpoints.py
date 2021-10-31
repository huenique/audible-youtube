import asyncio
import os

from aioredis.client import Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_507_INSUFFICIENT_STORAGE,
)

from audible_youtube.api.dependencies import get_redis_connection
from audible_youtube.models import common
from audible_youtube.services import redis as _redis
from audible_youtube.services import youtube as _youtube
from audible_youtube.utils import exec_as_aio, file_exists, generate_ticket

MAX_VIDEO_DURATION = 600

router = APIRouter()


@router.get("/download", name="Download")
async def download(
    ticket: str, _: Request, redis: Redis = Depends(get_redis_connection)
) -> FileResponse:
    file = await _redis.get_dict(redis, ticket, ("file_path", "filename"))

    if any(value is None for value in file):
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"{ticket} is not ready; resubmit request",
        )

    file = [value.decode("utf-8") for value in file]
    file_path = file[0]
    filename = file[1]

    if not await file_exists(file_path):
        logger.info(f"{filename=}, {file_path=}")
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"{ticket}'s file is missing",
        )

    return FileResponse(
        file_path,
        media_type="audio/m4a",
        background=BackgroundTask(os.unlink, file_path),
        filename=filename,
    )


@router.get("/save", name="Save")
async def save(
    video: str, _: Request, redis: Redis = Depends(get_redis_connection)
) -> JSONResponse:
    try:
        ticket = await generate_ticket()
        result = await exec_as_aio(_youtube.YoutubeVideo.search_video, video)
        title = result["title"]

        if (duration := result["duration"]) > MAX_VIDEO_DURATION:
            raise HTTPException(
                status_code=HTTP_507_INSUFFICIENT_STORAGE,
                detail=f"video exceeds {MAX_VIDEO_DURATION} seconds: {duration}, {title}",
            )

        asyncio.create_task(_youtube.YoutubeVideo().save_video(video, redis, ticket))
        return JSONResponse(
            {
                "ticket": ticket,
                "title": title,
                "webpage_url": result["webpage_url"],
                "thumbnail": result["thumbnail"],
            },
            media_type="application/json",
        )
    except (KeyError, AttributeError):
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/search", response_model=common.TargetMedia, name="Search")
async def search(term: str, _: Request) -> common.TargetMedia:
    result = await exec_as_aio(_youtube.YoutubeVideo().search_video, term)
    try:
        return common.TargetMedia(
            title=result["title"],
            webpage_url=result["webpage_url"],
            thumbnail=result["thumbnail"],
        )
    except KeyError:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
