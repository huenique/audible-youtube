# audible-youtube

audible-youtube is a backend service that enables application softwares to convert and download YouTube videos using REST API endpoints.

The project aims to decouple and eliminate the overhead of converting YouTube videos to audio files from other apps or services.

Supported audio formats:

- M4A (MPEG 4 Audio)
-

> Try it here: https://audible-youtube.herokuapp.com/docs

> *TODO:*
> - [ ] Support MP3 format
> - [ ] Implement webhook for slow option

## Technologies
> Please refer to the dependencies section in the [pyproject.toml](pyproject.toml) file.

## Installation

[Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository) the audible_youtube repo on GitHub, then [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository#cloning-a-repository) your fork locally.

## Setup

1. `cd` into the project directory, e.g. audible-youtube.
2. Inside the project's root directory, run `poetry shell`. This will create or start the virtual environment. Make sure [poetry](https://github.com/python-poetry/poetry#installation) is installed.
3. Run `poetry install`. This will install the project and its dependencies.
4. Run the app: `uvicorn app.main:app`.
5. Go to `http://127.0.0.1:8000/docs`

## Usage

### Convert and Download Videos

1. `/download` (**Fast option/Recommended**)

    Simply make a GET request to the `/download` path with your search term in the query parameter.

    ```
    /download?query=your+search+term
    ```

    ```sh
    curl -X 'GET' \
    'http://127.0.0.1:8000/download?query=rick+astley+never+gonna+give+you+up' \
      -H 'accept: application/json' \
      -o 'your_audio_file.m4a'
    ```

    >

2. `/convert` & `/save` (Slow option)

    First, make a request to the server to convert the video.

    ```
    /convert?query=your+search+term
    ```

    ```sh
    curl -X 'GET' \
      'http://127.0.0.1:8000/convert?query=rick+astley+never+gonna+give+you+up' \
      -H 'accept: application/json'
    ```

    Example JSON response:

    ```json
    {
      "ticket":"7aa156139564bd03b63178ec2ddffb27",
      "title":"Rick Astley - Never Gonna Give You Up (Official Music Video)",
      "link":"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "thumbnails":[
        {
          "url":"https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAfut6ib46TKYWnNm5PxBrcX8HLWg",
          "width":"360",
          "height":"202"
        },
        {
          "url":"https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDRxusbm2_TGTnDWEIhBTYW2cUQkw",
          "width":"720",
          "height":"404"
        }
      ]
    }
    ```

    Then use the value of the `ticket` key in the JSON response to download your audio file.

    ```
    /save?ticket=your+assigned+ticket
    ```

    ```sh
    curl -X 'GET' \
    'http://127.0.0.1:8000/save?ticket=7aa156139564bd03b63178ec2ddffb27' \
        -H 'accept: application/json' \
        -o 'your_audio_file.m4a'
    ```

    Your file is likely not ready if the response or file content looks like this:

    ```json
    {
      "errors":[
          "7aa156139564bd03b63178ec2ddffb27 is not ready. Please wait and resubmit your request"
      ]
    }
    ```

    If you get the above error, try again shortly.

> **IMPORTANT NOTES:**
> - The system rate limits requests to 5 per minute.
> - A file is set expire after 2 minutes or once you finish downloading it.

> **Check out the [client examples](./example).**

### Search Videos

Simply make a GET request to the `/search` path and pass the search term as a query string.

```
/search?query=your+search+term
```

```sh
curl -X 'GET' \
  'http://127.0.0.1:8000/search?query=rick+astley+never+gonna+give+you+up' \
  -H 'accept: application/json'
```

Example JSON response:
<details>
<summary><b>Show Example</b></summary>
<br>
<table>
<tr>
<td>

```json
{
  "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "id": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "publication_time": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "type": "video",
  "duration": "3:33",
  "viewcount": {
    "text": "1,224,529,631 views",
    "short": "1.2B views"
  },
  "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "thumbnails": [
    {
      "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAfut6ib46TKYWnNm5PxBrcX8HLWg",
      "width": "360",
      "height": "202"
    },
    {
      "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDRxusbm2_TGTnDWEIhBTYW2cUQkw",
      "width": "720",
      "height": "404"
    }
  ],
  "description": [
    {
      "text": "“"
    },
    {
      "text": "Never",
      "bold": "True"
    },
    {
      "text": " Gonna Give You Up” was a global smash on its release in July 1987, topping the charts in 25 countries including Rick's ..."
    }
  ],
  "channel": {
    "name": "Rick Astley",
    "id": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "thumbnails": [
      {
        "url": "https://yt3.ggpht.com/BbWaWU-qyR5nfxxXclxsI8zepppYL5x1agIPGfRdXFm5fPEewDsRRWg4x6P6fdKNhj84GoUpUI4=s88-c-k-c0x00ffffff-no-rj",
        "width": "68",
        "height": "68"
      }
    ],
    "link": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
  },
  "accessibility": {
    "title": "Rick Astley - Never Gonna Give You Up (Official Music Video) by Rick Astley 12 years ago 3 minutes, 33 seconds 1,224,529,631 views",
    "duration": "3 minutes, 33 seconds"
  }
}
```
</td>
</tr>
</table>
</details>
<br>

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

Have a question?\
Discord: [cnif.coffee#5404](https://discordapp.com/users/319861160239431682)\
E-mail: hjucode@gmail.com

## License

audible-youtube is distributed under the MIT License. See [LICENSE](./LICENSE) for more information.
