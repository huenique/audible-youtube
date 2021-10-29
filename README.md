# youtube-to-audio

Backend logic implementation for youtube-to-audio using FastAPI and youtube-dl.

## Development

### Installation

[Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository) the youtube_to_audio repo on GitHub, then [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository#cloning-a-repository) your repo locally.

### Setup

1. `cd` into the project directory, e.g. youtube-to-audio.
2. Make sure [poetry](https://github.com/python-poetry/poetry#installation) is installed.
3. Inside the project directory, run `poetry shell`. This will create or start the virtual environment.
4. Run `poetry install`. This will install the project and its dependencies.

## Deployment

youtube-to-audio comes with an `app.json` file for creating an app on Heroku from a GitHub repository.

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

youtube-to-audio is distributed under the MIT License. See [LICENSE](./LICENSE) for more information.
