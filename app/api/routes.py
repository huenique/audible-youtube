from fastapi import APIRouter

from app.api import endpoints

router = APIRouter()
router.include_router(endpoints.router)
