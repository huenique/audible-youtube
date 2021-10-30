# audible-youtube

Backend logic implementation for audible-youtube using FastAPI and youtube-dl.

## Installation

[Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository) the audible_youtube repo on GitHub, then [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository#cloning-a-repository) your fork locally.

## Setup

1. `cd` into the project directory, e.g. audible-youtube.
2. Inside the project's root directory, run `poetry shell`. This will create or start the virtual environment. Make sure [poetry](https://github.com/python-poetry/poetry#installation) is installed.
3. Run `poetry install`. This will install the project and its dependencies.
4. Run the app: `uvicorn audible_youtube.main:app`.
5. Go to `http://127.0.0.1:8000/docs`

## Usage

**Example Python client:**

```py
import asyncio
import urllib.request
from http.client import HTTPResponse


async def search(term: str) -> HTTPResponse:
    term = "+".join(term.split(" "))
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        urllib.request.urlopen,
        f"http://127.0.0.1:8000/search?term={term}",
    )


async def download(video: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        urllib.request.urlretrieve,
        f"http://127.0.0.1:8000/download?video={video}",
        "audio.m4a",
    )


async def main(video: str) -> None:
    result = await search(video)
    print(result.read().decode())
    await download(video)


asyncio.run(main("rick astley never gonna give you up"))
```

**Using `curl` to convert and download YouTube videos:**

```
curl -X 'GET' 'http://127.0.0.1:8000/download?video=https://www.youtube.com/watch?v=dQw4w9WgXcQ' -H 'accept: */*' --output audo_file.m4a
```

You can also pass search terms to the video parameter:

```
curl -X 'GET' 'http://127.0.0.1:8000/download?video=rick+astley+never+gonna+give+you+up' -H 'accept: */*' --output audo_file.m4a
```

**Using `curl` to search for videos:**

```
curl -X 'GET' 'http://127.0.0.1:8000/search?term=rick+astley+never+gonna+give+you+up' -H 'accept: */*'
```

## Deployment

audible-youtube comes with an `app.json` file for creating an app on Heroku from a GitHub repository.

If your fork is public, you can use the following button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Otherwise, access the following link and replace `$YOUR_REPOSITORY_LINK$` with your repository link:

```
https://heroku.com/deploy?template=$YOUR_REPOSITORY_LINK$
```

If you're using a frontend app, remember to fill the `ALLOWED_ORIGINS` field with the URI/URL of said app, leave it empty otherwise. For multiple origins, use a comma-separated value (e.g. `https://app.com,example-app.com:8080,app.host.com`)

## Contributing

Check the [contributing guide](./.github/CONTRIBUTING.md) to learn more about the development process and how you can test your changes.

## License

audible-youtube is distributed under the MIT License. See [LICENSE](./LICENSE) for more information.
