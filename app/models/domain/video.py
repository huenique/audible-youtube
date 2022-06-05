from typing import Union

from pydantic import BaseModel


class TargetMedia(BaseModel):
    title: str
    id: str
    publication_time: str
    type: str
    duration: str
    viewcount: dict[str, str]
    link: str
    thumbnails: list[dict[str, Union[str, int]]]
    description: list[dict[str, Union[str, bool]]]
    channel: dict[str, Union[str, list[dict[str, Union[str, Union[int, float]]]]]]
    accessibility: dict[str, str]


class Ticket(BaseModel):
    ticket: str
    title: str
    link: str
    thumbnails: list[dict[str, Union[str, int]]]
