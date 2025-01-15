import psycopg_pool
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from src.config.config import app_config


# Setup the connection pool (asynchronous)
DATABASE_URL = app_config.postgres.uri

pool: AsyncConnectionPool = psycopg_pool.AsyncConnectionPool(
    conninfo=app_config.postgres.uri,
    max_size=app_config.postgres.max_pool_size,
    kwargs={
        "autocommit": app_config.postgres.autocommit,
        "prepare_threshold": app_config.postgres.prepare_threshold
    }
)

@asynccontextmanager
async def get_db_connection():
    """
    Context manager for managing database connections using the connection pool.
    """
    async with pool.connection() as conn:
        yield conn

async def ping_db():
    async with get_db_connection() as conn:
        await conn.execute("SELECT 1")
