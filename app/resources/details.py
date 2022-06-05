"""
app.resources.details
~~~~~~~~~~~~~~~~~~~~~

This module contains messages and formatting for HTTP responses and documention.
"""
import json
import typing

from starlette import responses

# http error messages
TICKET_IS_NOT_READY = "please wait and resubmit your request"

TICKET_FILE_IS_MISSING = "file is missing or has been removed from filesystem"

VIDEO_IS_TOO_LONG = "the specified video is too long"

QUERY_HAS_NO_MATCH = "search query did not return a matching result"

# success messages
SEARCH_RESULT_CONTENT = {
    "application/json": {
        "example": {
            "title": "string",
            "id": "string",
            "publication_time": "string",
            "type": "string",
            "duration": "string",
            "viewcount": {"text": "string", "short": "string"},
            "link": "string",
            "thumbnails": [{"url": "string", "width": "string", "height": "string"}],
            "description": [
                {"text": "string"},
                {"text": "string", "bold": "string"},
                {"text": "string"},
                {"text": "string", "bold": "string"},
                {"text": "string"},
            ],
            "channel": {
                "name": "string",
                "id": "string",
                "thumbnails": [
                    {"url": "string", "width": "string", "height": "string"}
                ],
                "link": "string",
            },
            "accessibility": {"title": "string", "duration": "string"},
        }
    }
}

CONVERSION_NOTICE = {
    "application/json": {
        "example": {
            "ticket": "string",
            "title": "string",
            "link": "string",
            "thumbnails": [
                {
                    "url": "string",
                    "width": "string",
                    "height": "string",
                },
                {
                    "url": "string",
                    "width": "string",
                    "height": "string",
                },
            ],
        }
    }
}


def fmt_error_content(message: str):
    app_json = {"application/json": {"example": {"errors": [""]}}}
    app_json["application/json"]["example"]["errors"][0] = message

    return app_json


class AudibleYtContent:
    def __init__(self) -> None:
        self.yt_query_404 = fmt_error_content(QUERY_HAS_NO_MATCH)
        self.yt_query_507 = fmt_error_content(VIDEO_IS_TOO_LONG)
        self.yt_ticket_404 = fmt_error_content(TICKET_FILE_IS_MISSING)
        self.yt_ticket_409 = fmt_error_content(TICKET_IS_NOT_READY)

    @property
    def yt_query_404_detail(self):
        return QUERY_HAS_NO_MATCH

    @property
    def yt_query_507_detail(self):
        return VIDEO_IS_TOO_LONG

    @property
    def yt_ticket_404_detail(self):
        return TICKET_FILE_IS_MISSING

    @property
    def yt_ticket_409_detail(self):
        return TICKET_IS_NOT_READY

    @property
    def search_result_content(self):
        return SEARCH_RESULT_CONTENT

    @property
    def conversion_notice(self):
        return CONVERSION_NOTICE


class PrettyJSONResponse(responses.Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")
