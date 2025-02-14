from src.repositories.message_repository import MessageRepository
from src.models.response_models import MessageResponse, MessageSource
from src.config.config import NO_INFO_RESPONSE

class MessageService:
    def __init__(self):
        self.message_repository = MessageRepository()
        self.sources = []

    async def get_user_messages(self, user_id: str):
        """
        Fetches messages for the given user by querying the repository.
        """
        rows = await self.message_repository.get_messages_by_user(user_id)
        valid_rows = [row for row in rows if row.get("metadata", {}).get("writes") is not None]
        messages = [self._parse_message_row(row) for row in valid_rows]
        messages = [message for message in messages if message is not None]
        # sort messages by step
        messages = sorted(messages, key=lambda x: x.step)
        return messages
    
    async def delete_all_messages(self, user_id: str):
        """
        Deletes all messages for the given user by querying the repository.
        """
        return await self.message_repository.delete_all_messages(user_id)
    
    def _parse_user_message(self, message: dict):
        content = message.get("content")
        type = message.get("role")
        return content, type
    
    def _parse_ai_message(self, message: dict):
        kwargs = message.get("kwargs", {})
        content = kwargs.get("content")
        message_type = kwargs.get("type") 
        return content, message_type
    
    def _get_sources(self, message: dict):
        artifacts = message.get("kwargs", {}).get("artifact", [])
        source_keys = set()
        sources = []
        for artifact in artifacts:
            source_key = artifact.get("kwargs", {}).get("metadata", {}).get("source_key")
            if source_key in source_keys:
                continue
            source_keys.add(source_key)
            source_label = artifact.get("kwargs", {}).get("metadata", {}).get("source_label")
            sources.append(MessageSource(source_key=source_key, source_label=source_label))

        return sources

    def _parse_message_row(self, row: dict) -> MessageResponse:
        """
        Parses a database row to extract the thread_id, id, content, and type (user/ai).
        """
        metadata = row.get("metadata", {})
        writes = metadata.get("writes") or {}  # Default to an empty dict if None
        step = metadata.get("step")
        # Find content and type based on available keys in "writes"
        content, message_type = None, None
        sources = []

        if isinstance(writes, dict):  # Ensure writes is a dictionary
            if "__start__" in writes:  # User messages
                messages = writes.get("__start__", {}).get("messages", [])
                if not isinstance(messages, list):
                    return None
                
                message = next(iter(messages), {})
                content, message_type = self._parse_user_message(message)
            elif "direct_response" in writes:  # potential AI message
                messages = writes.get("direct_response", {}).get("messages", [])
                if not isinstance(messages, list):
                    return None
                
                message = next(iter(messages), {})
                content, message_type = self._parse_ai_message(message)
            elif "tools" in writes:  # source
                messages = writes.get("tools", {}).get("messages", [])
                if not isinstance(messages, list):
                    return None
                
                message = next(iter(messages), {})
                my_sources = self._get_sources(message)
                self.sources = my_sources
                return None
            elif "generate" in writes:  # ai message
                messages = writes.get("generate", {}).get("messages", [])
                if not isinstance(messages, list):
                    return None
                
                message = next(iter(messages), {})
                content, message_type = self._parse_ai_message(message)
                if not content.startswith(NO_INFO_RESPONSE):
                    sources = self.sources
                    self.sources = []
            else: 
                return None

        return MessageResponse(
            thread_id=row.get("thread_id"),
            id=row.get("id"),
            content=content,
            type=message_type,
            step=step,
            sources=sources
        )
