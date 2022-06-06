import typing

import pydantic


class TargetMedia(pydantic.BaseModel):
    type_: str
    id: str
    title: str
    publication_time: str
    duration: str
    view_count: dict[str, str]
    thumbnails: list[dict[str, typing.Union[str, int]]]
    rich_thumbnail: dict[str, typing.Union[str, int]]
    description_snippet: list[dict[str, typing.Any]]
    channel: dict[str, typing.Any]
    accessibility: dict[str, str]
    link: str
    shelf_title: typing.Optional[typing.Any] = None


class Ticket(pydantic.BaseModel):
    ticket: str
    title: str
    link: str
    thumbnails: list[dict[str, typing.Union[str, int]]]
