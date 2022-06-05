from aioredis import client
from starlette import requests

from app.services import youtube


def get_redis_connection(request: requests.Request) -> client.Redis:
    return request.app.state.redis


def get_ytdl_manager() -> youtube.YtDownloadManager:
    return youtube.YtDownloadManager()
