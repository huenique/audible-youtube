import typing

import pydantic
from fastapi import exceptions, responses
from fastapi.openapi import constants, utils
from starlette import requests, status


async def http422_error_handler(
    _: requests.Request,
    exc: typing.Union[exceptions.RequestValidationError, pydantic.ValidationError],
) -> responses.ORJSONResponse:
    return responses.ORJSONResponse(
        {"errors": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


utils.validation_error_response_definition["properties"] = {
    "errors": {
        "title": "Errors",
        "type": "array",
        "items": {"$ref": "{0}ValidationError".format(constants.REF_PREFIX)},
    },
}
