import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database import init_db, close_db, create_tables
from src.models.problem import Problem
from sqlmodel import select

async def main():
    try:
        # Initialize the database connection
        await init_db()
        print("✅ Database connection initialized")
        
        # Create tables
        await create_tables()
        print("✅ Database tables created")
        
        print("\n🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        # Clean up
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
