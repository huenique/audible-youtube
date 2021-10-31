import asyncio
import json
import urllib.request
from typing import Any, Callable
from urllib.error import HTTPError

BASE_URL = "http://127.0.0.1:8000"


async def exec_as_aio(blocking_fn: Callable[..., Any], *args: Any):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, blocking_fn, *args)


async def parse_response(response: Any) -> Any:
    try:
        return json.loads(response.read())
    except UnicodeDecodeError:
        return response


async def search(term: str) -> dict[str, Any]:
    resp = await exec_as_aio(urllib.request.urlopen, f"{BASE_URL}/search?term={term}")
    return await parse_response(resp)


async def save(video: str) -> dict[str, Any]:
    resp = await exec_as_aio(urllib.request.urlopen, f"{BASE_URL}/save?video={video}")
    return await parse_response(resp)


async def download(ticket: str) -> None:
    try:
        await exec_as_aio(
            urllib.request.urlopen, f"{BASE_URL}/download?ticket={ticket}"
        )
    except HTTPError as http_err:
        if http_err.code == 409:
            # Clients are rate limited to 5 requests per minute by default
            # Too many requests will result in a 429 response
            await asyncio.sleep(13)
            await download(ticket)
    else:
        await exec_as_aio(
            urllib.request.urlretrieve,
            f"{BASE_URL}/download?ticket={ticket}",
            "audio_file.m4a",
        )


async def main(video: str) -> None:
    if "http" not in video:
        video = "+".join(video.split(" "))

    result = await search(video)
    print(result)
    response = await save(video)
    await download(response["ticket"])


asyncio.run(main("when the comedic timing is just perfect~"))
