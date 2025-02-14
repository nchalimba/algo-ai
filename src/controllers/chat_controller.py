import traceback
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
import json
from typing import Annotated, AsyncGenerator
from src.services.chat_service import ask_question as ask
from src.models.request_models import QuestionRequest
from src.models.response_models import chat_response
import logging

logger = logging.getLogger(__name__)

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
        traceback.print_exc()
        logger.error("Error asking question: %s", str(e))
        yield json.dumps(error_response) + "\n"

async def stream_plain_text_response(question: str, thread_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator that yields plain text response chunks.
    """
    try:
        async for response in ask(question, thread_id):
            yield response
        
        # Send final newline to indicate completion
        yield "\n"
            
    except Exception as e:
        traceback.print_exc()
        logger.error("Error asking question: %s", str(e))
        yield str(e) + "\n"

@router.post("/ask", responses=chat_response)
async def ask_question(x_user_id: Annotated[str, Header()], request_body: QuestionRequest, accept: Annotated[str, Header()] = "text/plain"):
    """
    Endpoint that streams responses for chat messages.
    Each response is a newline-delimited chunk containing:
    - text: The response text chunk (JSON format)
    - done: Boolean indicating if the stream is complete (JSON format)
    - error: Error object if an error occurred, null otherwise (JSON format)
    or plain text response
    """
    try:
        if 'application/json' in accept:
            return StreamingResponse(
                stream_json_response(request_body.question, x_user_id),
                media_type="application/x-ndjson"
            )
        else:
            return StreamingResponse(
                stream_plain_text_response(request_body.question, x_user_id),
                media_type="text/plain"
            )
    except Exception as e:
        traceback.print_exc()
        logger.error("Error asking question: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
