import typing

import pydantic


class TargetMedia(pydantic.BaseModel):
    title: str
    id: str
    publication_time: str
    type: str
    duration: str
    viewcount: dict[str, str]
    link: str
    thumbnails: list[dict[str, typing.Any]]
    description: dict[str, typing.Any]
    channel: dict[str, typing.Any]
    accessibility: dict[str, str]


class Ticket(pydantic.BaseModel):
    ticket: str
    title: str
    link: str
    thumbnails: list[dict[str, typing.Union[str, int]]]
