from pathlib import Path

import databases
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config(".env")

# Global vars used by OpenAPI
APP_NAME = "audible-youtube"

APP_DESCRIPTION = "Convert YouTube videos to audio files using REST API endpoints"

APP_VERSION = "1.1.0-alpha.2"

# Secrets or env settings
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_ORIGINS: list[str] = config(
    "ALLOWED_ORIGINS",
    cast=CommaSeparatedStrings,
    default=["*"],
)

DATABASE_URL = config("DATABASE_URL", cast=databases.DatabaseURL)

MAX_CONNECTIONS_COUNT = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)

MIN_CONNECTIONS_COUNT = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

REDIS_URL = config("REDIS_URL")

RATE_LIMIT = config(
    "RATE_LIMIT", cast=str, default="5/minute"  # Number of requests per minute
)

# User authentication
SECRET_KEY = config("SECRET_KEY", cast=str, default="secret")

ALGORITHM = config("ALGORITHM", cast=str, default="HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30
)

BASE_DIR = Path(__file__).resolve().parent

# Download manager settings
MEDIA_ROOT = "media"

FILE_EXPIRE_SECONDS = 60

MAX_VIDEO_DURATION = 600
