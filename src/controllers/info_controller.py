from fastapi import APIRouter, Depends, HTTPException
from src.services.info_service import InfoService
import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_info_service():
    return InfoService()

@router.get("/")
async def get_info(info_service: InfoService = Depends(get_info_service)):
    """
    Returns information and configuration values for the app.
    """
    try:
        config_values = info_service.get_config_values()
        return config_values
    except Exception as e:
        traceback.print_exc()
        logger.error("Error getting info: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
