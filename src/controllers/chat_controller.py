import traceback
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
from typing import AsyncGenerator, Dict, Any
from src.services.chat_service import ask_question as ask
from src.models.request_models import QuestionRequest

router = APIRouter()

async def stream_json_response(question: str, thread_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator that yields JSON-formatted response chunks.
    Each chunk contains the response text and a done flag.
    """
    try:
        async for response in ask(question, thread_id):
            yield json.dumps({
                "text": response,
                "done": False,
                "error": None
            }) + "\n"
        
        # Send final chunk to indicate completion
        yield json.dumps({
            "text": "",
            "done": True,
            "error": None
        }) + "\n"
            
    except Exception as e:
        error_response = {
            "text": None,
            "done": True,
            "error": {
                "message": str(e),
                "type": type(e).__name__
            }
        }
        yield json.dumps(error_response) + "\n"

@router.post("/ask")
async def ask_question(request: Request, request_body: QuestionRequest):
    """
    Endpoint that streams JSON responses for chat messages.
    Each response is a newline-delimited JSON object containing:
    - text: The response text chunk
    - done: Boolean indicating if the stream is complete
    - error: Error object if an error occurred, null otherwise
    """
    try:
        return StreamingResponse(
            stream_json_response(request_body.question, request.state.user_id),
            media_type="application/x-ndjson"
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
