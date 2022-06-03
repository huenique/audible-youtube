from typing import Optional, Union

from pydantic import BaseModel


class TargetMedia(BaseModel):
    title: str
    link: str
    thumbnails: list[dict[str, Union[str, int]]]


class Token(BaseModel):
    access_token: str
    token_type: str


class Ticket(BaseModel):
    ticket: str
    title: str
    link: str
    thumbnails: list[dict[str, Union[str, int]]]


class TokenData(BaseModel):
    username: Optional[str] = None
