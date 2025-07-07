from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router
import os

app = FastAPI(
    title="PDF RAG API",
    description="API for PDF document retrieval-augmented generation (RAG).",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "PDF RAG API is running."}



app.include_router(router) 