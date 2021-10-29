from typing import Optional

from pydantic import BaseModel


class TargetMedia(BaseModel):
    title: str
    url: str
    thumbnail: str
    search_term: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
