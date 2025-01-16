from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def validate_user_id_middleware(request: Request, call_next):
    try:
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return JSONResponse(content={"detail": "X-User-ID header is required"}, status_code=400)

        if not is_valid_user_id(user_id):
            return JSONResponse(content={"detail": "Invalid X-User-ID format"}, status_code=400)


        # Attach the user_id to the request state for later use in endpoints
        request.state.user_id = user_id
        return await call_next(request)

    except HTTPException as e:
        # Explicitly handle HTTP exceptions and propagate them as is
        raise e

    except Exception as e:
        # Handle unexpected exceptions gracefully
        return JSONResponse(content={"detail": f"An unexpected error occurred: {str(e)}"}, status_code=500)

def is_valid_user_id(user_id: str) -> bool:
    return True
    # Example: Validate if the user_id is a UUID
    import uuid
    try:
        uuid.UUID(user_id)
        return True
    except ValueError:
        return False
