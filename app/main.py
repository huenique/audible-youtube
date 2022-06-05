import fastapi
from fastapi import exceptions, staticfiles
from fastapi.middleware import cors
from fastapi.openapi import utils
from slowapi import errors, extension, middleware, util

from app import settings
from app.api.errors import http_error, validation_error
from app.api.routes import router as api_router
from app.core import events


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = utils.get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def start_application() -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        title=settings.APP_NAME, debug=settings.DEBUG, version=settings.APP_VERSION
    )

    app.mount("/public", staticfiles.StaticFiles(directory="public"), name="public")
    app.openapi = custom_openapi
    app.state.limiter = extension.Limiter(
        key_func=util.get_remote_address,
        default_limits=[settings.RATE_LIMIT],
        storage_uri=settings.REDIS_URL,
    )

    app.add_middleware(middleware.SlowAPIMiddleware)
    app.add_middleware(
        cors.CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler("startup", events.create_start_app_handler(app))  # type: ignore
    app.add_event_handler("shutdown", events.create_stop_app_handler(app))  # type: ignore

    app.add_exception_handler(exceptions.HTTPException, http_error.http_error_handler)  # type: ignore
    app.add_exception_handler(exceptions.RequestValidationError, validation_error.http422_error_handler)  # type: ignore
    app.add_exception_handler(  # type: ignore
        errors.RateLimitExceeded, extension._rate_limit_exceeded_handler  # type: ignore
    )

    app.include_router(api_router)

    return app


app = start_application()
