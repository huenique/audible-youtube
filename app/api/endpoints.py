import asyncio
import os
import secrets
from typing import Any, TypeVar

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

from app.api.dependencies import get_redis_connection, get_ytdl_manager
from app.models import common
from app.services import redis as redis_
from app.services import youtube
from app.settings import MAX_VIDEO_DURATION
from app.utils import validate_duration

_T = TypeVar("_T", list[dict[str, Any]], list[None])


router = APIRouter()


async def _validate_duration(duration: str, title: str) -> None:
    if not await validate_duration(duration, 1, MAX_VIDEO_DURATION):
        raise HTTPException(
            status_code=HTTP_507_INSUFFICIENT_STORAGE,
            detail=f"video exceeds {MAX_VIDEO_DURATION} seconds: {duration}, {title}",
        )


async def _validate_query_result(result: _T, query: str) -> _T:
    if not result:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"no matching result: {query}",
        )
    return result


@router.get("/download", name="Download")
async def download(
    query: str,
    _: Request,
    bg_tasks: BackgroundTasks,
    youtube: youtube.YoutubeDownload = Depends(get_ytdl_manager),
) -> FileResponse:
    result = await youtube.search_video_plus(query)
    result = await _validate_query_result(result["result"], query)
    result = result[0]

    await _validate_duration(result["duration"], result["title"])
    await youtube.download_video_plus(query)
    bg_tasks.add_task(os.unlink, youtube.file_download.path)  # type: ignore

    return FileResponse(
        youtube.file_download.path,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=youtube.file_download.name,
    )


@router.get("/save", name="Save")
async def save(
    ticket: str,
    _: Request,
    bg_tasks: BackgroundTasks,
    redis: Redis = Depends(get_redis_connection),
) -> FileResponse:
    print("here")
    file = await redis_.get_dict(redis, ticket, ("path", "name"))

    if all(value == b"" for value in file):
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"{ticket} is not ready. Please wait and resubmit your request",
        )

    path = file[0] or ""

    if not os.path.isfile(path):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"{ticket}'s file is missing or has been removed from filesystem",
        )

    bg_tasks.add_task(os.unlink, path)  # type: ignore

    return FileResponse(
        path,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=file[1].decode("utf-8"),
    )


@router.get("/convert", response_model=common.Ticket, name="Convert")
async def convert(
    query: str,
    _: Request,
    redis: Redis = Depends(get_redis_connection),
    youtube: youtube.YoutubeDownload = Depends(get_ytdl_manager),
) -> common.Ticket:
    try:
        result = await youtube.search_video_plus(query)
        result = await _validate_query_result(result["result"], query)
        result = result[0]
        title = result["title"]
        ticket = secrets.token_hex(16)

        await _validate_duration(result["duration"], title)

        asyncio.create_task(youtube.convert_video(query, redis, ticket))

        return common.Ticket(
            ticket=ticket,
            title=title,
            link=result["link"],
            thumbnails=result["thumbnails"],
        )
    except (KeyError, AttributeError) as key_err:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR) from key_err


@router.get("/search", response_model=common.TargetMedia, name="Search")
async def search(
    query: str, _: Request, youtube: youtube.YoutubeDownload = Depends(get_ytdl_manager)
) -> common.TargetMedia:
    result = await youtube.search_video_plus(query)
    result = await _validate_query_result(result["result"], query)
    result = result[0]

    try:
        return common.TargetMedia(
            title=result["title"],
            link=result["link"],
            thumbnails=result["thumbnails"],
        )
    except KeyError as key_err:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR) from key_err
