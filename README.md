# audible-youtube

Backend logic implementation for audible-youtube using FastAPI and youtube-dl. audible-youtube is a service that enables client applications to convert and download YouTube videos via REST API endpoints.

Supported formats:

- M4A (MPEG 4 Audio)
-

## Installation

[Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository) the audible_youtube repo on GitHub, then [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository#cloning-a-repository) your fork locally.

## Setup

1. `cd` into the project directory, e.g. audible-youtube.
2. Inside the project's root directory, run `poetry shell`. This will create or start the virtual environment. Make sure [poetry](https://github.com/python-poetry/poetry#installation) is installed.
3. Run `poetry install`. This will install the project and its dependencies.
4. Run the app: `uvicorn audible_youtube.main:app`.
5. Go to `http://127.0.0.1:8000/docs`

## Usage

- ### Convert and Download Videos

  1. `/convert` (Fast option)

     ```sh
     curl -X 'GET' 'http://127.0.0.1:8000/save?video=rick+astley+never+gonna+give+you+up' --output 'audio_file.m4a'
     ```

  2. `/save` & `/download` (Slow option)

     First, make a request to the server to convert the video:

     ```sh
     curl -X 'GET' 'http://127.0.0.1:8000/save?video=rick+astley+never+gonna+give+you+up' -H 'accept: */*'
     ```

     Example response:

     ```json
     {
       "ticket": "1a79a4d60de6718e8e5b326e338ae533",
       "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
       "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
       "thumbnail": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/maxresdefault.webp"
     }
     ```

     Then, use the `ticket` value in the response body to download your audio file:

     ```sh
     curl -X 'GET' 'http://127.0.0.1:8000/download?ticket=1a79a4d60de6718e8e5b326e338ae533' -H 'accept: */*' --output 'audio_file.m4a'
     ```

  > Check out the [client example](./example/example_client.py).

- ### Search Videos

  ```sh
  curl -X 'GET' 'http://127.0.0.1:8000/search?video=rick+astley+never+gonna+give+you+up' -H 'accept: */*'
  ```

  Example response:

  ```json
  {
    "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
    "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "thumbnail": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/maxresdefault.webp"
  }
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
