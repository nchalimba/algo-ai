import traceback
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, File, Header, UploadFile

from src.models.response_models import DocumentResponse, EmptyResponse
from src.services.auth_service import verify_jwt
from src.services.document_processor import DocumentProcessor
from src.models.request_models import TextRequest, URLsRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_document_processor() -> DocumentProcessor:
    return DocumentProcessor()

# delete documents with source label from query (/?source_label=...)
@router.delete("/", response_model=EmptyResponse)
async def delete_documents_with_source_label(authorization: Annotated[str, Header()], source_label: str, processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Delete documents with a specific source label.
    """
    if not verify_jwt(authorization.split(' ')[-1]):
        raise HTTPException(status_code=401, detail='Unauthorized: Invalid API key')
    try:
        processor.vector_store.delete_embeddings_by_source_label(source_label)
        return {}
    except Exception as e:
        traceback.print_exc()
        logger.error("Error deleting documents: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")

@router.post("/text", response_model=DocumentResponse)
async def process_text(authorization: Annotated[str, Header()], request: TextRequest, processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Process raw text by sending it to the document processor.
    """
    if not verify_jwt(authorization.split(' ')[-1]):
        raise HTTPException(status_code=401, detail='Unauthorized: Invalid API key')
    try:
        processor.process_text(request.text, request.title)
        return {"message": "Text processed successfully."}
    except Exception as e:
        traceback.print_exc()
        logger.error("Error processing text: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@router.post("/pdf", response_model=DocumentResponse)
async def process_pdf(authorization: Annotated[str, Header()], title: Annotated[str, Form()], file: UploadFile = File(...), processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Process a PDF file by sending it to the document processor.
    """
    if not verify_jwt(authorization.split(' ')[-1]):
        raise HTTPException(status_code=401, detail='Unauthorized: Invalid API key')
    try:
        file_bytes = await file.read()
        
        processor.process_pdf(file_bytes, title)
        return {"message": "PDF processed successfully."}
    except Exception as e:
        traceback.print_exc()
        logger.error("Error processing PDF: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/url", response_model=DocumentResponse)
async def process_urls(authorization: Annotated[str, Header()], request: URLsRequest, processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Process a list of URLs by sending them to the document processor.
    """
    if not verify_jwt(authorization.split(' ')[-1]):
        raise HTTPException(status_code=401, detail='Unauthorized: Invalid API key')
    try:
        processor.process_urls(request.urls)
        return {"message": "URLs processed successfully."}
    except Exception as e:
        traceback.print_exc()
        logger.error("Error processing URLs: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing URLs: {str(e)}")
