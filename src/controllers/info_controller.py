from fastapi import APIRouter, Depends
from src.services.info_service import InfoService

router = APIRouter()

def get_info_service():
    return InfoService()

@router.get("/")
async def get_info(info_service: InfoService = Depends(get_info_service)):
    config_values = info_service.get_config_values()
    return config_values
