# audible-youtube

Backend logic implementation for audible-youtube using FastAPI and youtube-dl.

## Usage

For better detail, start the app and go to http://127.0.0.1:8000/docs.

To convert and download YouTube videos, use  `http://127.0.0.1:8000/download` with the `url` parameter.

Example Python client:
```py
import asyncio
import urllib.request


async def download() -> None:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        urllib.request.urlretrieve,
        "http://127.0.0.1:8000/download?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "audio.m4a",
    )
    print(repr(result))


asyncio.run(download())
```

Using curl:
```
curl -X 'GET' 'http://127.0.0.1:8000/download?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ' -H 'accept: */*' --output audo_file.m4a
```

You can also pass search terms to the url parameter:
```
curl -X 'GET' 'http://127.0.0.1:8000/download?url=rick+astley+never+gonna+give+you+up' -H 'accept: */*' --output audo_file.m4a
```



## Development

### Installation

[Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository) the audible_youtube repo on GitHub, then [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository#cloning-a-repository) your fork locally.

### Setup

1. `cd` into the project directory, e.g. audible-youtube.
2. Inside the project's root directory, run `poetry shell`. This will create or start the virtual environment. Make sure [poetry](https://github.com/python-poetry/poetry#installation) is installed.
3. Run `poetry install`. This will install the project and its dependencies.

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
