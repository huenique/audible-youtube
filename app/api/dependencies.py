from aioredis.client import Redis
from rq import Queue
from starlette.requests import Request

from app.services.youtube import YtDownloadManager


def get_redis_queue(request: Request) -> Queue:
    return request.app.state.queue


def get_redis_connection(request: Request) -> Redis:
    return request.app.state.redis


def get_ytdl_manager() -> YtDownloadManager:
    return YtDownloadManager()
