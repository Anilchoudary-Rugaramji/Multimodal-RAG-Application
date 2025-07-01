from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router

app = FastAPI(
    title="Multimodal RAG API",
    description="API for multimodal retrieval-augmented generation (RAG) with text and images.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://192.168.2.112:8501",  # Your main network IP
        "http://192.168.27.1:8501",
        "http://192.168.32.1:8501", 
        "*"  # Allow all origins for deployed version
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Multimodal RAG API is running."}

@app.get("/health")
def health():
    import os
    return {
        "status": "healthy",
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "port": os.getenv("PORT", "not set")
    }

app.include_router(router) 