# Multimodal RAG Assistant - Streamlit Frontend

A simple Streamlit-based frontend for the multimodal RAG (Retrieval-Augmented Generation) application.

## Features

- 📄 **PDF Upload**: Upload PDF documents through a simple file uploader
- 💬 **Question & Answer**: Ask questions about your uploaded document
- 📝 **Chat History**: View and manage your conversation history
- 🎨 **Clean UI**: Simple, intuitive interface built with Streamlit

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements_streamlit.txt
```

### 2. Start the Backend
Make sure your FastAPI backend is running:
```bash
cd multimodal_rag_api
uvicorn app.main:app --reload
```

### 3. Start the Streamlit Frontend
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Upload Document**: Use the sidebar to upload a PDF file
2. **Ask Questions**: Type your question in the text input and click "Ask Question"
3. **View History**: See all your previous questions and answers in the chat history
4. **Manage History**: Delete individual conversations or clear all history

## Architecture

- **Frontend**: Streamlit (Python-based web app)
- **Backend**: FastAPI (REST API)
- **Communication**: HTTP requests between frontend and backend
- **Storage**: In-memory storage for chat history (resets on app restart)

## Troubleshooting

- **Backend Connection**: Ensure the FastAPI backend is running on `http://localhost:8000`
- **File Upload**: Make sure you're uploading valid PDF files
- **CORS Issues**: The backend should have CORS configured to allow Streamlit requests

## Next Steps

For production use, consider:
- Persistent storage for chat history
- User authentication
- Multiple document support
- Advanced UI features 