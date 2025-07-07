# PDF RAG Application

A complete local RAG (Retrieval-Augmented Generation) application with FastAPI backend and Streamlit frontend for PDF document-based question answering.

## Features

- **PDF Document Upload**: Upload and process PDF documents  
- **Intelligent Q&A**: Ask questions about your uploaded documents
- **Vector Search**: ChromaDB-powered semantic search
- **Chat History**: Track and manage conversation history
- **Admin Authentication**: Secure document upload with password protection
- **Modern UI**: Clean Streamlit interface with responsive design

## Architecture

- **Backend**: FastAPI with OpenAI GPT-4 integration
- **Frontend**: Streamlit web application  
- **Vector Database**: ChromaDB for document embeddings
- **Document Processing**: Unstructured library for PDF parsing

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
ADMIN_API_KEY=admin123
```

### 3. Start the Backend
```bash
cd multimodal_rag_api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### 4. Start the Frontend  
```bash
streamlit run streamlit_app.py --server.port 8501
```

### 5. Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8002

## Usage

1. **Admin Login**: Use password `admin123` in the sidebar
2. **Upload Documents**: Upload PDF files with product categories
3. **Ask Questions**: Select a product and ask questions about the documents
4. **View History**: Review previous conversations and manage chat history

## API Endpoints

- `GET /` - Root endpoint
- `POST /admin/upload` - Upload PDF documents (requires admin key)
- `GET /products` - List available products and documents
- `POST /rag/query` - Query documents with questions

## File Structure

```
├── multimodal_rag_api/          # Backend API
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api.py               # API routes
│   │   ├── models.py            # Pydantic models
│   │   ├── config.py            # Configuration
│   │   ├── rag_pipeline.py      # Document processing
│   │   └── utils.py             # Utility functions
│   ├── data/                    # Uploaded documents
│   └── chroma_db/               # Vector database
├── note-books/                  # Research notebooks
│   └── rag-pipeline.ipynb       # RAG development notebook
├── streamlit_app.py             # Frontend application
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Dependencies

Core libraries:
- `fastapi` - Web framework
- `streamlit` - Frontend framework  
- `langchain` - LLM framework
- `langchain-openai` - OpenAI integration
- `langchain-chroma` - ChromaDB integration
- `unstructured[pdf]` - PDF processing
- `python-dotenv` - Environment variables

## Development Notes

- The `note-books/rag-pipeline.ipynb` contains research and development work
- Documents are stored in `data/` directory organized by product
- Vector embeddings are persisted in `chroma_db/` directory
- Admin password can be changed in `.streamlit/secrets.toml`

## Local Development

This application is designed to run completely locally without external dependencies except for OpenAI API calls. All data is stored locally in ChromaDB.

## License

Open source - feel free to modify and use for your projects. 