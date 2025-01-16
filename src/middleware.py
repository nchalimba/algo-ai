from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

EXEMPT_PATHS = ["/health", "/health/"]

async def validate_user_id_middleware(request: Request, call_next):
    print(request.url.path)
    if request.url.path in EXEMPT_PATHS:
        return await call_next(request)
    
    try:
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return JSONResponse(content={"detail": "X-User-ID header is required"}, status_code=400)

        if not is_valid_user_id(user_id):
            return JSONResponse(content={"detail": "Invalid X-User-ID format"}, status_code=400)

        request.state.user_id = user_id
        return await call_next(request)

    except HTTPException as e:
        raise e

    except Exception as e:
        return JSONResponse(content={"detail": f"An unexpected error occurred: {str(e)}"}, status_code=500)

def is_valid_user_id(user_id: str) -> bool:
    return True
    # TODO: Validate if the user_id is a UUID
    import uuid
    try:
        uuid.UUID(user_id)
        return True
    except ValueError:
        return False
