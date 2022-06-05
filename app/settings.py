from pathlib import Path

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config(".env")

# global vars used by OpenAPI
APP_NAME = "audible-youtube"

APP_DESCRIPTION = "Convert YouTube videos to audio files using REST API endpoints"

APP_VERSION = "1.1.0-alpha.3"

# Secrets or config vars
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_ORIGINS: list[str] = config(
    "ALLOWED_ORIGINS",
    cast=CommaSeparatedStrings,
    default=["*"],
)

REDIS_URL = config("REDIS_URL")

RATE_LIMIT = config(
    "RATE_LIMIT", cast=str, default="5/minute"  # Number of requests per minute
)

BASE_DIR = Path(__file__).resolve().parent

# Download manager settings
MEDIA_ROOT = "media"

FILE_EXPIRE_SECONDS = 60

MAX_VIDEO_DURATION = 600
