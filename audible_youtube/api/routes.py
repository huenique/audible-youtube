from fastapi import APIRouter

from audible_youtube.api import endpoints

router = APIRouter()
router.include_router(endpoints.router)
