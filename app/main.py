from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter, _rate_limit_exceeded_handler  # type: ignore
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException

from app.api.errors import http_error_handler
from app.api.routes import router as api_router
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.settings import (
    ALLOWED_ORIGINS,
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    DEBUG,
    RATE_LIMIT,
    REDIS_URL,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def start_application() -> FastAPI:
    app = FastAPI(title=APP_NAME, debug=DEBUG, version=APP_VERSION)

    app.openapi = custom_openapi
    app.state.limiter = Limiter(
        key_func=get_remote_address, default_limits=[RATE_LIMIT], storage_uri=REDIS_URL
    )

    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler("startup", create_start_app_handler(app))  # type: ignore
    app.add_event_handler("shutdown", create_stop_app_handler(app))  # type: ignore

    app.add_exception_handler(HTTPException, http_error_handler)  # type: ignore
    app.add_exception_handler(  # type: ignore
        RateLimitExceeded, _rate_limit_exceeded_handler
    )

    app.include_router(api_router)

    return app


app = start_application()
