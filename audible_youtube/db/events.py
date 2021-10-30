import asyncio

import asyncpg
from fastapi import FastAPI
from loguru import logger

from audible_youtube.settings import (
    DATABASE_URL,
    MAX_CONNECTIONS_COUNT,
    MIN_CONNECTIONS_COUNT,
)


async def connect_to_db(app: FastAPI) -> None:
    logger.info(f"Connecting to {repr(DATABASE_URL)}")
    app.state.pool = await asyncpg.create_pool(  # type: ignore
        str(DATABASE_URL),
        min_size=MIN_CONNECTIONS_COUNT,
        max_size=MAX_CONNECTIONS_COUNT,
    )
    logger.info("Connection established.")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database.")
    await asyncio.wait_for(app.state.pool.close(), timeout=10.0)
    logger.info("Connection closed.")
