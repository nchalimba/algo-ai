from typing import List, Dict, Any
from src.database import get_db_connection


class MessageRepository:
    def __init__(self):
        pass

    async def get_messages_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetches all messages from the "checkpoints" table where thread_id matches user_id.
        Also retrieves the metadata column.
        """
        query = """
        SELECT checkpoint_id, thread_id, metadata
        FROM checkpoints
        WHERE thread_id = %s;
        """
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (user_id,))
                rows = await cursor.fetchall()

        # Mapping the result to a more understandable structure
        return [{"id": row[0], "thread_id": row[1], "metadata": row[2]} for row in rows]
    
    async def delete_all_messages(self, user_id: str):
        """
        Deletes all messages from the "checkpoints" table where thread_id matches user_id.
        """
        queries = [
            """
            DELETE FROM checkpoints
            WHERE thread_id = %s;
            """,
            """
            DELETE FROM checkpoint_writes
            WHERE thread_id = %s;
            """,
            """
            DELETE FROM checkpoint_blobs
            WHERE thread_id = %s;
            """
        ]
        print("Deleting all messages for user_id:", user_id)
        async with get_db_connection() as conn:
            async with conn.cursor() as cursor:
                for query in queries:
                    await cursor.execute(query, (user_id,))
                await conn.commit()  # Commit transaction
