import typing

import pydantic


class User(pydantic.BaseModel):
    username: str
    email: typing.Optional[str] = None
    disabled: typing.Optional[bool] = None


class UserInDB(User):
    hashed_password: str
