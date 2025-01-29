from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from src.controllers.document_controller import router as document_router
from src.controllers.chat_controller import router as chat_router
from src.controllers.message_controller import router as message_router
from src.controllers.health_controller import router as health_router
from src.controllers.info_controller import router as info_router
from src.middleware import validate_user_id_middleware
from src.config.config import app_config

load_dotenv()

app = FastAPI(
    title=app_config.info.title,
    description=app_config.info.description,
    version=app_config.info.version
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Replace "*" with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Content-Length"],  # Expose necessary headers
)

@app.middleware("http")
async def user_id_middleware(request, call_next):
    return await validate_user_id_middleware(request, call_next)

app.include_router(document_router, prefix="/process")
app.include_router(chat_router, prefix="/chat")
app.include_router(message_router, prefix="/message")
app.include_router(health_router, prefix="/health")
app.include_router(info_router, prefix="/info") # Added prefix "/info"

@app.get("/")
async def root():
    return {
        "content": "Welcome to DSA RAG API, a RAG system for answering questions about Data Structures and Algorithms."
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=app_config.port,
        reload=True,
        log_level="info"
    )