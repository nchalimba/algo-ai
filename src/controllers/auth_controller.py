import traceback
from typing import Annotated

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from src.services.auth_service import verify_api_key, generate_jwt
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post('/login')
async def admin_login(authorization: Annotated[str, Header()]) -> JSONResponse:
    """
    Returns a JWT if the API key is valid.
    """
    try:
        api_key = authorization.split(' ')[-1]
        if not verify_api_key(api_key):
            raise HTTPException(status_code=401, detail='Unauthorized: Invalid API key')

        jwt_token, expires_at = generate_jwt()  # Call the function to generate JWT
        return JSONResponse(content={'token': jwt_token, 'expires_at': expires_at})
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        logger.error("Error logging in: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
