from fastapi import APIRouter, HTTPException, UploadFile, File
import shutil
from .models import RAGQueryRequest, RAGQueryResponse
from .rag_pipeline import RAGPipeline

router = APIRouter()
pipeline = None  # Lazy initialization

@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    dest = "./data/attention_paper.pdf"
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    global pipeline
    pipeline = RAGPipeline()  # Re-initialize after upload
    return {"filename": file.filename}

@router.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(request: RAGQueryRequest):
    if not pipeline:
        raise HTTPException(status_code=400, detail="No PDF uploaded yet.")
    try:
        answer = pipeline.query(request.question)
        return RAGQueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 