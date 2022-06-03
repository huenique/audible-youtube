from fastapi import APIRouter

from app.api import endpoints

router = APIRouter(tags=["videos"])
router.include_router(endpoints.router)
