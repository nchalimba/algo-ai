
from pydantic import BaseModel

class Message(BaseModel):
    id: str
    thread_id: str
    content: str
    type: str
    step: int