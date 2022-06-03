import asyncio
import json
import urllib.request
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import urlencode

BASE_URL = "http://127.0.0.1:8000"


async def exec_as_aio(blocking_fn: Callable[..., Any], *args: Any) -> Any:
    """Asyncronously run blocking functions.

    Args:
        blocking_fn (Callable[..., Any]): The blocking fn.

    Returns:
        Any: The return value/s of the blocking fn.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, blocking_fn, *args)


async def parse_response(json_: Any) -> Any:
    """Convert JSON object to a python data type.

    Args:
        response (Any): The JSON object to deserialize.

    Returns:
        Any: The deserialized JSON object.
    """
    try:
        return json.loads(json_.read())
    except UnicodeDecodeError:
        return json_


async def search(query: str) -> dict[str, Any]:
    """Make a request to the /search endpoint.

    Args:
        query (str): The search term/query.

    Returns:
        dict[str, Any]: The search result.
    """
    resp = await exec_as_aio(urllib.request.urlopen, f"{BASE_URL}/search?{query}")
    return await parse_response(resp)


async def convert(query: str) -> dict[str, Any]:
    """Make a request to convert a video to audio.

    Args:
        query (str): The search term/query or video url.

    Returns:
        dict[str, Any]: A JSON response.
    """
    resp = await exec_as_aio(urllib.request.urlopen, f"{BASE_URL}/convert?{query}")
    return await parse_response(resp)


async def save(ticket: str) -> None:
    """Save the audio file using assigned ticket.

    Args:
        ticket (str): The value of the ticket key in the JSON response.
    """
    try:
        filedata = await exec_as_aio(
            urllib.request.urlopen, f"{BASE_URL}/save?{ticket}"
        )
        datatowrite = filedata.read()
        with open("audio_file.m4a", "wb") as f:
            f.write(datatowrite)
    except HTTPError as http_err:
        if http_err.code == 409:
            # Clients are rate limited to 5 requests per minute by default
            # Too many requests will result in a 429 response
            await asyncio.sleep(13)
            await save(ticket)
    else:
        await exec_as_aio(
            urllib.request.urlretrieve,
            f"{BASE_URL}/download?{ticket}",
            "audio_file.m4a",
        )


async def main(query: str) -> None:
    query = urlencode({"query": query}) if "http" not in query else query

    result = await search(query)
    print(result)

    response = await convert(query)
    print(response)
    await save(f"""ticket={response["ticket"]}""")


asyncio.run(main("when the comedic timing is just perfect~"))
