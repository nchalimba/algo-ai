from src.repositories.message_repository import MessageRepository
from src.models.message import Message

class MessageService:
    def __init__(self):
        self.message_repository = MessageRepository()

    async def get_user_messages(self, user_id: str):
        """
        Fetches messages for the given user by querying the repository.
        """
        rows = await self.message_repository.get_messages_by_user(user_id)
        valid_rows = [row for row in rows if row.get("metadata", {}).get("writes") is not None]
        messages = [self._parse_message_row(row) for row in valid_rows]
        return messages
    
    async def delete_all_messages(self, user_id: str):
        """
        Deletes all messages for the given user by querying the repository.
        """
        return await self.message_repository.delete_all_messages(user_id)
    
    def _parse_message_row(self, row: dict) -> Message:
        """
        Parses a database row to extract the thread_id, id, content, and type (user/ai).
        """
        metadata = row.get("metadata", {})
        writes = metadata.get("writes") or {}  # Default to an empty dict if None
        step = metadata.get("step")
        # Find content and type based on available keys in "writes"
        content, message_type = None, None

        if isinstance(writes, dict):  # Ensure writes is a dictionary
            if "__start__" in writes:  # User messages
                messages = writes.get("__start__", {}).get("messages", [])
                if isinstance(messages, list):
                    message = next(iter(messages), {})
                    content = message.get("content")
                    message_type = message.get("role")  # Typically "user"
            elif "query_or_respond" in writes:  # AI messages
                messages = writes.get("query_or_respond", {}).get("messages", [])
                if isinstance(messages, list):
                    message = next(iter(messages), {})
                    kwargs = message.get("kwargs", {})
                    content = kwargs.get("content")
                    message_type = kwargs.get("type")  # Typically "ai"

        return Message(
            thread_id=row.get("thread_id"),
            id=row.get("id"),
            content=content or "No content available",
            type=message_type or "unknown",
            step=step
        )
