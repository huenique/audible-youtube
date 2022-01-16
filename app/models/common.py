from typing import Optional

from pydantic import BaseModel


class TargetMedia(BaseModel):
    title: str
    webpage_url: str
    thumbnail: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
