import fastapi
from starlette import requests, responses


async def http_error_handler(
    _: requests.Request, exc: fastapi.HTTPException
) -> responses.JSONResponse:
    return responses.JSONResponse(
        {"errors": [exc.detail]}, status_code=exc.status_code  # type: ignore
    )
