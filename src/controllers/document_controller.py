import traceback
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile

from src.services.document_processor import DocumentProcessor
from src.models.request_models import TextRequest, URLsRequest

router = APIRouter()

# Dependency Injection: Use FastAPI's dependency injection to provide DocumentProcessor instance
def get_document_processor() -> DocumentProcessor:
    return DocumentProcessor()

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
async def process_pdf(file: UploadFile = File(...), title: str = None, processor: DocumentProcessor = Depends(get_document_processor)):
    """
    Process a PDF file by sending it to the document processor.
    """
    try:

        file_bytes = await file.read()
        if not title:
            title = file.filename
        
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
