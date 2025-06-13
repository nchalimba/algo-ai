import asyncio
import logging
import psycopg_pool
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator, Any
from src.config.config import app_config

logger = logging.getLogger(__name__)

# Connection pool (initialized on startup)
pool: Optional[AsyncConnectionPool] = None

# Connection settings
CONNECTION_TIMEOUT = 5  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # second

class DatabaseError(Exception):
    """Base exception for database errors"""
    pass

def get_pool() -> AsyncConnectionPool:
    """Get the database connection pool."""
    if pool is None:
        raise RuntimeError("Database connection pool is not initialized. Call init_db() first.")
    return pool

async def init_db():
    """Initialize the database connection pool with enhanced settings."""
    global pool
    if pool is not None:
        return

    try:
        pool = psycopg_pool.AsyncConnectionPool(
            conninfo=app_config.postgres.uri,
            min_size=1,
            max_size=app_config.postgres.max_pool_size,
            open=False,  # We'll open it manually after configuration
            kwargs={
                "autocommit": app_config.postgres.autocommit,
                "prepare_threshold": app_config.postgres.prepare_threshold,
                "connect_timeout": CONNECTION_TIMEOUT,
                "keepalives": 1,  # Enable keepalive
                "keepalives_idle": 30,  # Send keepalive after 30s of inactivity
                "keepalives_interval": 10,  # Resend unacked keepalive every 10s
                "keepalives_count": 5,  # Consider connection dead after 5 failed keepalives
            }
        )
        
        # Open the pool and test the connection
        await pool.open(wait=True)
        await _test_connection()
        logger.info("Database connection pool initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {e}")
        if pool:
            await pool.close()
            pool = None
        raise DatabaseError(f"Failed to initialize database: {e}")

async def _test_connection():
    """Test the database connection with retries."""
    for attempt in range(MAX_RETRIES):
        try:
            async with get_pool().connection() as conn:
                await conn.execute("SELECT 1")
                return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to connect to database after {MAX_RETRIES} attempts")
                raise
            logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))


async def close_db():
    """Close the database connection pool."""
    global pool
    if pool is not None:
        await pool.close()
        pool = None

@asynccontextmanager
async def get_db_connection() -> AsyncIterator[Any]:
    """
    Context manager for managing database connections with retry logic.
    """
    current_pool = get_pool()
    conn = None
    
    try:
        for attempt in range(MAX_RETRIES):
            try:
                conn = await current_pool.getconn(timeout=CONNECTION_TIMEOUT)
                # Test the connection
                async with conn.transaction():
                    await conn.execute("SELECT 1")
                break
            except Exception as e:
                if conn:
                    await current_pool.putconn(conn)
                    conn = None
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    logger.error("Max retries reached, giving up on database connection")
                    raise DatabaseError(f"Failed to connect to database after {MAX_RETRIES} attempts") from e
                await asyncio.sleep(RETRY_DELAY * (2 ** attempt))
        
        try:
            yield conn
        finally:
            if conn:
                await current_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Unexpected error in get_db_connection: {e}")
        raise

async def ping_db() -> bool:
    """Ping the database to check if it's alive."""
    try:
        async with get_db_connection() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database ping failed: {e}")
        return False
