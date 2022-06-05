import fastapi

from app.api import endpoints

router = fastapi.APIRouter(tags=["videos"])
router.include_router(endpoints.router)
