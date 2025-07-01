from fastapi import APIRouter, HTTPException, UploadFile, File, Header
import shutil
import os
from .models import RAGQueryRequest, RAGQueryResponse
from .rag_pipeline import store_document_in_vector_db
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

router = APIRouter()

# In-memory product-document mapping (for demo; use DB in production)
product_docs = {}
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin123")

@router.post("/admin/upload")
def admin_upload_pdf(product: str, file: UploadFile = File(...), x_api_key: str = Header(...)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured. Cannot process documents.")
    
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
    dest_dir = f"./data/{product}"
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, file.filename)
    try:
        # Save file first
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store document metadata
        if product not in product_docs:
            product_docs[product] = []
        product_docs[product].append(file.filename)
        
        # Process document with timeout protection
        try:
            print(f"Starting document processing for {file.filename}...")
            num_chunks = store_document_in_vector_db(dest, product, file.filename)
            print(f"Successfully processed {file.filename}: {num_chunks} chunks")
            return {"product": product, "filename": file.filename, "chunks_stored": num_chunks}
        except Exception as process_error:
            print(f"Document processing failed: {process_error}")
            # File was saved but processing failed
            return {
                "product": product, 
                "filename": file.filename, 
                "status": "uploaded but processing failed",
                "error": str(process_error),
                "chunks_stored": 0
            }
    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Old upload endpoint removed - use /admin/upload instead

@router.get("/products")
def list_products():
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return {"error": "OpenAI API key not configured"}
    
    try:
        # Check if vector database directory exists
        if not os.path.exists("./chroma_db"):
            return {}  # No products yet
        
        vectorstore = Chroma(
            collection_name="mm_rag",
            embedding_function=OpenAIEmbeddings(),
            persist_directory="./chroma_db"
        )
        
        # Check if collection has any documents
        try:
            all_docs = vectorstore.get()
            if not all_docs or not all_docs.get('metadatas'):
                return {}  # Empty database
        except Exception as inner_e:
            print(f"Vector DB access error: {inner_e}")
            return {}  # Return empty if DB access fails
        
        products = {}
        
        for metadata in all_docs['metadatas']:
            if metadata and 'product' in metadata and 'document' in metadata:
                product = metadata['product']
                document = metadata['document']
                if product not in products:
                    products[product] = []
                if document not in products[product]:
                    products[product].append(document)
        
        return products
    except Exception as e:
        print(f"Products endpoint error: {e}")
        return {"error": f"Failed to load products: {str(e)}"}

@router.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(request: RAGQueryRequest):
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    product = getattr(request, 'product', None)
    if not product:
        raise HTTPException(status_code=400, detail="Product is required.")
    
    try:
        # Load persistent vector DB
        vectorstore = Chroma(
            collection_name="mm_rag",
            embedding_function=OpenAIEmbeddings(),
            persist_directory="./chroma_db"
        )
        
        # Check if product exists in vector DB by trying to retrieve docs
        test_retriever = vectorstore.as_retriever(search_kwargs={"k": 1, "filter": {"product": product}})
        test_docs = test_retriever.invoke("test")
        
        if not test_docs:
            raise HTTPException(status_code=400, detail=f"No documents found for product '{product}'. Available products: {list(set([doc.get('product', 'unknown') for doc in vectorstore.get()['metadatas'] if doc]))}")
        
        # Retrieve relevant chunks for the product
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5, "filter": {"product": product}})
        docs = retriever.invoke(request.question)
        text_chunks = [doc.page_content for doc in docs]
        print(f"RETRIEVED {len(docs)} CHUNKS for product '{product}':")
        for i, chunk in enumerate(text_chunks):
            print(f"CHUNK {i+1}: {chunk[:200]}...")
        context_text = '\n'.join(text_chunks)
        print(f"CONTEXT LENGTH: {len(context_text)} characters")
        
        if not context_text.strip():
            return RAGQueryResponse(answer="I don't know.")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use only the provided context to answer. If not in context, say 'I don't know.'"},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion:\n{request.question}"}
        ]
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke(messages)
        if isinstance(response.content, str):
            return RAGQueryResponse(answer=response.content)
        else:
            return RAGQueryResponse(answer=str(response.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 