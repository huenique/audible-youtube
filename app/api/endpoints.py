import asyncio
import os
import secrets
from typing import Any, TypeVar

from aioredis.client import Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_507_INSUFFICIENT_STORAGE,
)

from app.api.dependencies import get_redis_connection, get_ytdl_manager
from app.models.domain.video import TargetMedia, Ticket
from app.resources.details import AudibleYtContent
from app.services import youtube
from app.utils import validate_duration

MEDIA_TYPE = "audio/m4a"

_T = TypeVar("_T", list[dict[str, Any]], list[None])

router = APIRouter()
content = AudibleYtContent()


async def _validate_search_result(result: _T) -> _T:
    if not result:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=content.yt_query_404_detail,
        )
    else:
        return result


async def _validate_video_duration(duration: str) -> None:
    if not await validate_duration(duration, 1):
        raise HTTPException(
            status_code=HTTP_507_INSUFFICIENT_STORAGE,
            detail=content.yt_query_507_detail,
        )


@router.get(
    "/download",
    name="Download",
    response_class=Response,
    responses={
        HTTP_200_OK: {
            "content": {MEDIA_TYPE: ""},
        },
        HTTP_404_NOT_FOUND: {
            "content": content.yt_query_404,
            "description": "No video matched the search query.",
        },
        HTTP_507_INSUFFICIENT_STORAGE: {
            "content": content.yt_query_507,
            "description": "The YouTube video is too big for the filesystem.",
        },
    },
)
async def download(
    query: str,
    _: Request,
    bg_tasks: BackgroundTasks,
    youtube: youtube.YtDownloadManager = Depends(get_ytdl_manager),
) -> FileResponse:
    result = await youtube.search_video_plus(query)
    result = await _validate_search_result(result["result"])
    result = result[0]

    await _validate_video_duration(result["duration"])
    await youtube.download_video_plus(query)
    bg_tasks.add_task(os.unlink, youtube.file_download.path)  # type: ignore

    return FileResponse(
        youtube.file_download.path,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=youtube.file_download.name,
    )


@router.get(
    "/save",
    name="Save",
    response_class=Response,
    responses={
        HTTP_200_OK: {
            "content": {MEDIA_TYPE: ""},
        },
        HTTP_404_NOT_FOUND: {
            "content": content.yt_ticket_404,
            "description": f"The ticket or the ticket's file does not exists.",
        },
        HTTP_409_CONFLICT: {
            "content": content.yt_ticket_409,
            "description": f"The ticket's file is still being converted.",
        },
    },
)
async def save(
    ticket: str,
    _: Request,
    bg_tasks: BackgroundTasks,
    redis: Redis = Depends(get_redis_connection),
) -> FileResponse:
    file: Any = await redis.hmget(ticket, ("path", "name"))  # type: ignore

    if all(value == b"" for value in file):
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=content.yt_ticket_409,
        )

    fpath = file[0] or ""

    if not os.path.isfile(fpath):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=content.yt_ticket_404_detail,
        )

    bg_tasks.add_task(os.unlink, fpath)  # type: ignore
    await redis.delete(ticket)  # type: ignore

    return FileResponse(
        fpath,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=file[1].decode("utf-8"),
    )


@router.get(
    "/convert",
    response_model=Ticket,
    name="Convert",
    responses={
        HTTP_200_OK: {
            "content": content.conversion_notice,
        },
        HTTP_404_NOT_FOUND: {
            "content": content.yt_query_404,
            "description": "No video matched the search query.",
        },
        HTTP_507_INSUFFICIENT_STORAGE: {
            "content": content.yt_query_507,
            "description": "The YouTube video is too big for the filesystem.",
        },
    },
)
async def convert(
    query: str,
    _: Request,
    redis: Redis = Depends(get_redis_connection),
    youtube: youtube.YtDownloadManager = Depends(get_ytdl_manager),
) -> Ticket:
    try:
        result = await youtube.search_video_plus(query)
        result = await _validate_search_result(result["result"])
        result = result[0]
        ticket = secrets.token_hex(16)

        await _validate_video_duration(result["duration"])
        asyncio.create_task(youtube.convert_video(query, redis, ticket))

        return Ticket(
            ticket=ticket,
            title=result["title"],
            link=result["link"],
            thumbnails=result["thumbnails"],
        )
    except (KeyError, AttributeError) as key_err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail={"msg": key_err}
        )


@router.get(
    "/search",
    name="Search",
    response_model=TargetMedia,
    responses={
        HTTP_200_OK: {
            "content": content.search_result_content,
            "description": "The search query results.",
        },
        HTTP_404_NOT_FOUND: {
            "content": content.yt_query_404,
            "description": "No video matched the search query.",
        },
    },
)
async def search(
    query: str,
    _: Request,
    youtube: youtube.YtDownloadManager = Depends(get_ytdl_manager),
) -> TargetMedia:
    result = await youtube.search_video_plus(query)
    result = await _validate_search_result(result["result"])
    result = result[0]

    try:
        return TargetMedia(
            title=result["title"],
            id=result["title"],
            type=result["type"],
            publication_time=result["title"],
            duration=result["duration"],
            viewcount=result["viewCount"],
            link=result["link"],
            thumbnails=result["thumbnails"],
            description=result["descriptionSnippet"],
            channel=result["channel"],
            accessibility=result["accessibility"],
        )
    except KeyError as key_err:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail={"msg": key_err}
        )


@router.get("/")
async def read_index():
    return RedirectResponse(url="/public/index.html")
