# Multimodal RAG API

A production-grade FastAPI service for multimodal retrieval-augmented generation (RAG) over scientific PDFs, supporting both text and image queries.

## Usage

1. Set your environment variables in `.env` (e.g., `OPENAI_API_KEY`).
2. Build and run with Docker, or run locally with Uvicorn.
3. Use the `/rag/query` endpoint to ask questions.

## Example

```bash
curl -X POST "http://localhost:8000/rag/query" -H "Content-Type: application/json" -d '{"question": "What does figure 3-1 show?"}'
``` 