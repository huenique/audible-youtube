import asyncio
import os
import secrets
import typing

import fastapi
from aioredis import client
from fastapi import responses
from starlette import background, requests, status

from app import utils
from app.api import dependencies
from app.models.domain import video
from app.resources import details
from app.services import youtube

MEDIA_TYPE = "audio/m4a"

_T = typing.TypeVar("_T", list[dict[str, typing.Any]], list[None])

router = fastapi.APIRouter()
content = details.AudibleYtContent()


async def _validate_search_result(result: _T) -> _T:
    if not result:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=content.yt_query_404_detail,
        )
    else:
        return result


async def _validate_video_duration(duration: str) -> None:
    if not await utils.validate_duration(duration, 1):
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=content.yt_query_507_detail,
        )


@router.get(
    "/download",
    name="Download",
    response_class=responses.Response,
    responses={
        status.HTTP_200_OK: {
            "content": {MEDIA_TYPE: ""},
        },
        status.HTTP_404_NOT_FOUND: {
            "content": content.yt_query_404,
            "description": "No video matched the search query.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "content": content.yt_query_507,
            "description": "The YouTube video is too big for the filesystem.",
        },
    },
)
async def download(
    query: str,
    _: requests.Request,
    bg_tasks: background.BackgroundTasks,
    youtube: youtube.YtDownloadManager = fastapi.Depends(dependencies.get_ytdl_manager),
) -> responses.FileResponse:
    result = await youtube.search_video_plus(query, 1)
    result = await _validate_search_result(result["result"])
    result = result[0]

    await _validate_video_duration(result["duration"])
    await youtube.download_video_plus(query)
    bg_tasks.add_task(os.unlink, youtube.file_download.path)  # type: ignore

    return responses.FileResponse(
        youtube.file_download.path,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=youtube.file_download.name,
    )


@router.get(
    "/save",
    name="Save",
    response_class=responses.Response,
    responses={
        status.HTTP_200_OK: {
            "content": {MEDIA_TYPE: ""},
        },
        status.HTTP_404_NOT_FOUND: {
            "content": content.yt_ticket_404,
            "description": f"The ticket or the ticket's file does not exists.",
        },
        status.HTTP_409_CONFLICT: {
            "content": content.yt_ticket_409,
            "description": f"The ticket's file is still being converted.",
        },
    },
)
async def save(
    ticket: str,
    _: requests.Request,
    bg_tasks: background.BackgroundTasks,
    redis: client.Redis = fastapi.Depends(dependencies.get_redis_connection),
) -> responses.FileResponse:
    file: typing.Any = await redis.hmget(ticket, ("path", "name"))  # type: ignore

    if all(value == b"" for value in file):
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=content.yt_ticket_409,
        )

    fpath = file[0] or ""

    if not os.path.isfile(fpath):
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=content.yt_ticket_404_detail,
        )

    bg_tasks.add_task(os.unlink, fpath)  # type: ignore
    await redis.delete(ticket)  # type: ignore

    return responses.FileResponse(
        fpath,
        media_type="audio/m4a",
        background=bg_tasks,
        filename=file[1].decode("utf-8"),
    )


@router.get(
    "/convert",
    response_model=video.Ticket,
    name="Convert",
    responses={
        status.HTTP_200_OK: {
            "content": content.conversion_notice,
        },
        status.HTTP_404_NOT_FOUND: {
            "content": content.yt_query_404,
            "description": "No video matched the search query.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "content": content.yt_query_507,
            "description": "The YouTube video is too big for the filesystem.",
        },
    },
)
async def convert(
    query: str,
    _: requests.Request,
    redis: client.Redis = fastapi.Depends(dependencies.get_redis_connection),
    youtube: youtube.YtDownloadManager = fastapi.Depends(dependencies.get_ytdl_manager),
) -> video.Ticket:
    try:
        result = await youtube.search_video_plus(query, 1)
        result = await _validate_search_result(result["result"])
        result = result[0]
        ticket = secrets.token_hex(16)

        await _validate_video_duration(result["duration"])
        asyncio.create_task(youtube.convert_video(query, redis, ticket))

        return video.Ticket(
            ticket=ticket,
            title=result["title"],
            link=result["link"],
            thumbnails=result["thumbnails"],
        )
    except (KeyError, AttributeError) as key_err:
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"msg": key_err}
        )


@router.get(
    "/search",
    name="Search",
    response_model=video.TargetMedia,
    responses={
        status.HTTP_200_OK: {
            "content": content.search_result_content,
            "description": "The search query results.",
        },
        status.HTTP_404_NOT_FOUND: {
            "content": content.yt_query_404,
            "description": "No video matched the search query.",
        },
    },
)
async def search(
    _: requests.Request,
    query: str,
    limit: int = 1,
    youtube: youtube.YtDownloadManager = fastapi.Depends(dependencies.get_ytdl_manager),
): 
    result = await youtube.search_video_plus(query, limit)
    result = await _validate_search_result(result["result"])

    try:
        return responses.ORJSONResponse(content=result[0])
    except KeyError as key_err:
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"msg": key_err}
        )


@router.get("/", include_in_schema=False)
async def read_index():
    return responses.RedirectResponse(url="/public/index.html")
