
from pydantic import BaseModel

class Source(BaseModel):
    source_key: str
    source_label: str

class Message(BaseModel):
    id: str
    thread_id: str
    content: str
    type: str
    step: int
    sources: list[Source] = []