import traceback
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from src.services.chat_service import ask_question as ask
from src.models.request_models import QuestionRequest

router = APIRouter()

async def stream_graph_response(question: str, thread_id: str):
    """
    Async generator to stream graph responses.
    """
    try:
        # Use the ask function to yield responses
        async for response in ask(question, thread_id):
            yield response
    except Exception as e:
        traceback.print_exc()
        yield f"Error: {str(e)}"

@router.post("/ask")
async def ask_question(request: Request, request_body: QuestionRequest):
    """
    Ask a question and stream the response to the user.
    """
    try:
        return StreamingResponse(
            stream_graph_response(request_body.question, request.state.user_id),
            media_type="text/plain"  # Adjust media type as needed
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
