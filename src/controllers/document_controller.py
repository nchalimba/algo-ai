import traceback
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile

from src.services.document_processor import DocumentProcessor
from src.models.request_models import TextRequest, URLsRequest

router = APIRouter()

def get_document_processor() -> DocumentProcessor:
    return DocumentProcessor()

# delete documents with source label from query (/?source_label=...)
@router.delete("/")
async def delete_documents_with_source_label(source_label: str, processor: DocumentProcessor = Depends(get_document_processor)):
    try:
        processor.vector_store.delete_embeddings_by_source_label(source_label)
        return {}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")

@router.post("/text")
async def process_text(request: TextRequest, processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Process raw text by sending it to the document processor.
    """
    try:
        processor.process_text(request.text, request.title)
        return {"message": "Text processed successfully."}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@router.post("/pdf")
async def process_pdf(title: Annotated[str, Form()], file: UploadFile = File(...), processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Process a PDF file by sending it to the document processor.
    """
    try:
        file_bytes = await file.read()
        
        processor.process_pdf(file_bytes, title)
        return {"message": "PDF processed successfully."}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/url")
async def process_urls(request: URLsRequest, processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Process a list of URLs by sending them to the document processor.
    """
    try:
        processor.process_urls(request.urls)
        return {"message": "URLs processed successfully."}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing URLs: {str(e)}")
