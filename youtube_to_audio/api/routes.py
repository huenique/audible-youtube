from fastapi import APIRouter

from youtube_to_audio.api import endpoints

router = APIRouter()
router.include_router(endpoints.router)
