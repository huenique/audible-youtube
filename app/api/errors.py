from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.resources import details


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        {"errors": [exc.detail]}, status_code=exc.status_code  # type: ignore
    )


def fmt_error_content(message: str):
    app_json = {"application/json": {"example": {"detail": [""]}}}
    app_json["application/json"]["example"]["detail"].append(message)

    return app_json


class AudibleYtContent:
    def __init__(self) -> None:
        self.yt_query_404 = fmt_error_content(details.QUERY_HAS_NO_MATCH)
        self.yt_query_507 = fmt_error_content(details.VIDEO_IS_TOO_LONG)
        self.yt_ticket_404 = fmt_error_content(details.TICKET_FILE_IS_MISSING)
        self.yt_ticket_409 = fmt_error_content(details.TICKET_IS_NOT_READY)

    @property
    def yt_query_404_detail(self):
        return self.yt_query_404["application/json"]["example"]

    @property
    def yt_query_507_detail(self):
        return self.yt_query_507["application/json"]["example"]

    @property
    def yt_ticket_404_detail(self):
        return self.yt_ticket_404["application/json"]["example"]

    @property
    def yt_ticket_409_detail(self):
        return self.yt_ticket_409["application/json"]["example"]
