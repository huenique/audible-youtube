from pathlib import Path

import databases
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, URLPath

config = Config(".env")

APP_NAME = config("APP_NAME", cast=str, default="")
APP_DESCRIPTION = config("APP_DESCRIPTION", cast=str, default="")
APP_VERSION = config("APP_VERSION", cast=str, default="")

DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_ORIGINS: list[str] = config(
    "ALLOWED_ORIGINS",
    cast=CommaSeparatedStrings,
    default="",
)

DATABASE_URL = config("DATABASE_URL", cast=databases.DatabaseURL)
MAX_CONNECTIONS_COUNT = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

REDIS_URL = config("REDIS_URL", cast=URLPath)

# Rate limiter
RATE_LIMIT = "5/minute"  # Number of requests per minute

# Authentication
SECRET_KEY = config("SECRET_KEY", cast=str)
ALGORITHM = config("ALGORITHM", cast=str, default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30
)

BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = "media"
