import traceback
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from src.services.message_service import MessageService

router = APIRouter()

def get_message_service() -> MessageService:
    return MessageService()

@router.get("/")
async def get_messages(x_user_id: Annotated[str, Header()], message_service: MessageService = Depends(get_message_service)):
    try:
        messages = await message_service.get_user_messages(x_user_id)
        if not messages:
            return JSONResponse([], status_code=200)
        return messages
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.delete("/")
async def delete_all_messages(x_user_id: Annotated[str, Header()], message_service: MessageService = Depends(get_message_service)):
    try:
        await message_service.delete_all_messages(x_user_id)
        return JSONResponse({}, status_code=200)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")