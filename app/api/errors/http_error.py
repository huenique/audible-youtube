import fastapi
from fastapi import responses
from starlette import requests


async def http_error_handler(
    _: requests.Request, exc: fastapi.HTTPException
) -> responses.ORJSONResponse:
    return responses.ORJSONResponse(
        {"errors": [exc.detail]}, status_code=exc.status_code  # type: ignore
    )
