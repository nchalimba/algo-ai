import traceback
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from src.services.chat_service_2 import ChatService
from src.models.request_models import QuestionRequest

router = APIRouter()

def get_chat_service() -> ChatService:
    return ChatService()

@router.post("/ask")
async def ask_question(request: QuestionRequest, chat_service: ChatService = Depends(get_chat_service)):
    """
    Ask a question and get a streaming response based on the processed documents.
    """
    try:
        return {"response": chat_service.ask_question(request.question)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))