import asyncio
import logging
import psycopg_pool
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from src.config.config import app_config

logger = logging.getLogger(__name__)

# Connection pool (initialized on startup)
pool: Optional[AsyncConnectionPool] = None
# SQLAlchemy async engine and session maker
async_engine = None
async_session_maker = None

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
    """Initialize the database connection pool with enhanced settings and SQLAlchemy integration."""
    global pool, async_engine, async_session_maker
    if pool is not None:
        return

    try:
        # Initialize the connection pool
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
        
        # Parse the connection string to extract components
        from urllib.parse import urlparse, parse_qs, urlunparse
        from urllib.parse import quote_plus
        
        # Parse the original URI
        parsed = urlparse(app_config.postgres.uri)
        
        # Extract query parameters
        query_params = parse_qs(parsed.query)
        
        # Remove sslmode from query params as it's not supported directly by asyncpg
        ssl_mode = query_params.pop('sslmode', ['prefer'])[0]
        
        # Rebuild the query string without sslmode
        new_query = '&'.join(
            f"{k}={v[0]}" if v else k 
            for k, v in query_params.items()
        )
        
        # Rebuild the URL with the new query
        clean_uri = urlunparse(parsed._replace(query=new_query))
        
        # Convert to SQLAlchemy async URL
        db_url = clean_uri.replace('postgresql://', 'postgresql+asyncpg://', 1)
        
        # Initialize SQLAlchemy async engine with direct connection
        async_engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            echo=getattr(app_config.postgres, 'echo_sql', False),  # Default to False if not set
            future=True,
            connect_args={
                'ssl': ssl_mode == 'require'  # Only set ssl=True if required
            }
        )
        
        # Create async session maker
        async_session_maker = sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("Database connection pool and SQLAlchemy engine initialized successfully")
        
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
    """Close the database connection pool and SQLAlchemy engine."""
    global pool, async_engine, async_session_maker
    
    # Close SQLAlchemy session maker
    if async_session_maker:
        await async_engine.dispose()
        async_session_maker = None
        logger.info("SQLAlchemy engine and session maker closed")
    
    # Close the connection pool
    if pool:
        await pool.close()
        pool = None
        logger.info("Database connection pool closed")


async def create_tables():
    """Create all tables defined in SQLModel metadata."""
    from sqlmodel import SQLModel
    from sqlalchemy.ext.asyncio import AsyncEngine
    
    if not async_engine:
        await init_db()
    
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("Database tables created successfully")


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
