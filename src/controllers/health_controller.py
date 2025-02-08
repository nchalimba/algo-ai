import traceback
from fastapi import APIRouter, Depends
from src.services.vector_store import VectorStore
from src.database import ping_db

router = APIRouter()

def get_vector_store() -> VectorStore:
    return VectorStore()

@router.get("/")
async def health_check(vector_store: VectorStore = Depends(get_vector_store)):
    """
    Health check endpoint.
    Pings the vector store and the postgres db
    """
    response = {}
    try:
        vector_store.ping()
        response["vector_store"] = "up"
    except Exception:
        traceback.print_exc()
        response["vector_store"] = "down"


    try:
        await ping_db()
        response["db"] = "up"
    except Exception:
        traceback.print_exc()
        response["db"] = "down"

    return response
