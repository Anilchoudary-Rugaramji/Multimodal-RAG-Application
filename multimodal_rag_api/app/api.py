from fastapi import APIRouter, HTTPException, UploadFile, File, Header
import shutil
import os
from .models import RAGQueryRequest, RAGQueryResponse
from .rag_pipeline import RAGPipeline, store_document_in_vector_db
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

router = APIRouter()
pipeline = None  # Lazy initialization

# In-memory product-document mapping (for demo; use DB in production)
product_docs = {}
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "secret123")

@router.post("/admin/upload")
def admin_upload_pdf(product: str, file: UploadFile = File(...), x_api_key: str = Header(...)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
    dest_dir = f"./data/{product}"
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, file.filename)
    try:
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Store document metadata
        if product not in product_docs:
            product_docs[product] = []
        product_docs[product].append(file.filename)
        # Partition, embed, and store in persistent vector DB
        num_chunks = store_document_in_vector_db(dest, product, file.filename)
        return {"product": product, "filename": file.filename, "chunks_stored": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    dest_dir = "./data"
    dest = os.path.join(dest_dir, "attention_paper.pdf")
    try:
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        global pipeline
        pipeline = RAGPipeline()  # Re-initialize after upload
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/products")
def list_products():
    try:
        vectorstore = Chroma(
            collection_name="mm_rag",
            embedding_function=OpenAIEmbeddings(),
            persist_directory="./chroma_db"
        )
        
        # Get all documents and organize by product
        all_docs = vectorstore.get()
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
        return {"error": f"Failed to load products: {str(e)}"}

@router.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(request: RAGQueryRequest):
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