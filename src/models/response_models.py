
from typing import Literal
from pydantic import BaseModel


class AuthResponse(BaseModel):
    token: str
    expires_at: float

class EmptyResponse(BaseModel):
    pass

class DocumentResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    vector_store: Literal["up", "down"]
    db: Literal["up", "down"]

class InfoResponse(BaseModel):
    llm_provider: str
    llm: str
    embedding_model: str
    rag_version: str
    chunk_size: int
    chunk_overlap: int
    vector_dimension: int
    sources: list[str]

class MessageSource(BaseModel):
    source_key: str
    source_label: str

class MessageResponse(BaseModel):
    id: str
    thread_id: str
    content: str
    type: str
    step: int
    sources: list[MessageSource] = []

chat_response = {
    200: { "content": {
            "application/json": {
                "example": { "text": "Response chunk", "done": False, "error": None }
            },
            "text/plain": { "example": "Response text chunk" }
        }}
}