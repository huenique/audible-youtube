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

SYSTEM_ERR = "please report this error to https://github.com/huenique/audible-youtube"

# success messages
SEARCH_RESULT_CONTENT = {
    "application/json": {
        "example": {
            "type": "video",
            "id": "dQw4w9WgXcQ",
            "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
            "publishedTime": "12 years ago",
            "duration": "3:33",
            "viewCount": {"text": "1,226,115,753 views", "short": "1.2B views"},
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAfut6ib46TKYWnNm5PxBrcX8HLWg",
                    "width": 360,
                    "height": 202,
                },
                {
                    "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDRxusbm2_TGTnDWEIhBTYW2cUQkw",
                    "width": 720,
                    "height": 404,
                },
            ],
            "richThumbnail": {
                "url": "https://i.ytimg.com/an_webp/dQw4w9WgXcQ/mqdefault_6s.webp?du=3000&sqp=CPye9pQG&rs=AOn4CLDYr_LyEDlnnOvNJBPXL8lI2JF7jA",
                "width": 320,
                "height": 180,
            },
            "descriptionSnippet": [
                {"text": "“"},
                {"text": "Never Gonna Give You Up", "bold": True},
                {
                    "text": "” was a global smash on its release in July 1987, topping the charts in 25 countries including Rick's ..."
                },
            ],
            "channel": {
                "name": "Rick Astley",
                "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
                "thumbnails": [
                    {
                        "url": "https://yt3.ggpht.com/BbWaWU-qyR5nfxxXclxsI8zepppYL5x1agIPGfRdXFm5fPEewDsRRWg4x6P6fdKNhj84GoUpUI4=s88-c-k-c0x00ffffff-no-rj",
                        "width": 68,
                        "height": 68,
                    }
                ],
                "link": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
            },
            "accessibility": {
                "title": "Rick Astley - Never Gonna Give You Up (Official Music Video) by Rick Astley 12 years ago 3 minutes, 33 seconds 1,226,115,753 views",
                "duration": "3 minutes, 33 seconds",
            },
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "shelfTitle": "",
        }
    }
}

CONVERSION_NOTICE = {
    "application/json": {
        "example": {
            "ticket": "9afa41d24fd92c535bc05132344adde6",
            "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAfut6ib46TKYWnNm5PxBrcX8HLWg",
                    "width": "360",
                    "height": "202",
                },
                {
                    "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDRxusbm2_TGTnDWEIhBTYW2cUQkw",
                    "width": "720",
                    "height": "404",
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
        self.yt_query_500 = fmt_error_content(SYSTEM_ERR)
        self.yt_query_507 = fmt_error_content(VIDEO_IS_TOO_LONG)
        self.yt_ticket_404 = fmt_error_content(TICKET_FILE_IS_MISSING)
        self.yt_ticket_409 = fmt_error_content(TICKET_IS_NOT_READY)

    @property
    def yt_query_404_detail(self):
        return QUERY_HAS_NO_MATCH

    @property
    def yt_query_500_detail(self):
        return SYSTEM_ERR

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
