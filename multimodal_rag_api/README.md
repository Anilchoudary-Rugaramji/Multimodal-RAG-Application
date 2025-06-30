# Multimodal RAG API

A FastAPI backend for document-based question answering using RAG (Retrieval-Augmented Generation).

## Features

- PDF document upload and processing
- Vector-based document search using ChromaDB
- OpenAI GPT-4 integration for answer generation
- RESTful API endpoints

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export OPENAI_API_KEY=your_openai_key
export ADMIN_API_KEY=your_admin_key
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /admin/upload` - Upload PDF documents
- `POST /rag/query` - Query documents  
- `GET /products` - List uploaded documents

## Deployment

Built with Docker for easy deployment to any cloud platform.

```bash
docker build -t rag-api .
docker run -p 8000:8000 rag-api
``` 