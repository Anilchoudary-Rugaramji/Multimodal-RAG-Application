from fastapi import APIRouter, HTTPException, UploadFile, File, Header
import shutil
import os
from .models import RAGQueryRequest, RAGQueryResponse
from .rag_pipeline import store_document_in_vector_db
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

router = APIRouter()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin123")

@router.post("/admin/upload")
def admin_upload_pdf(product: str, file: UploadFile = File(...), x_api_key: str = Header(...)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured. Cannot process documents.")
    
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
    
    safe_product = "".join(c for c in product if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_product = safe_product.replace(' ', '_')
    
    data_dir = os.path.abspath("./data")
    dest_dir = os.path.join(data_dir, safe_product)
    os.makedirs(dest_dir, exist_ok=True)
    
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (' ', '-', '_', '.')).strip()
    dest = os.path.join(dest_dir, safe_filename)
    try:
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            num_chunks = store_document_in_vector_db(dest, product, file.filename)
            return {"product": product, "filename": file.filename, "chunks_stored": num_chunks}
        except Exception as process_error:
            return {
                "product": product, 
                "filename": file.filename, 
                "status": "uploaded but processing failed",
                "error": str(process_error),
                "chunks_stored": 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/products")
def list_products():
    if not os.getenv("OPENAI_API_KEY"):
        return {"error": "OpenAI API key not configured"}
    
    try:
        if not os.path.exists("./chroma_db"):
            return {}
        
        vectorstore = Chroma(
            collection_name="mm_rag",
            embedding_function=OpenAIEmbeddings(),
            persist_directory="./chroma_db"
        )
        
        try:
            all_docs = vectorstore.get()
            if not all_docs or not all_docs.get('metadatas'):
                return {}
        except Exception as inner_e:
            return {}
        
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
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    product = getattr(request, 'product', None)
    if not product:
        raise HTTPException(status_code=400, detail="Product is required.")
    
    try:
        vectorstore = Chroma(
            collection_name="mm_rag",
            embedding_function=OpenAIEmbeddings(),
            persist_directory="./chroma_db"
        )
        
        test_retriever = vectorstore.as_retriever(search_kwargs={"k": 1, "filter": {"product": product}})
        test_docs = test_retriever.invoke("test")
        
        if not test_docs:
            raise HTTPException(status_code=400, detail=f"No documents found for product '{product}'. Available products: {list(set([doc.get('product', 'unknown') for doc in vectorstore.get()['metadatas'] if doc]))}")
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5, "filter": {"product": product}})
        docs = retriever.invoke(request.question)
        text_chunks = [doc.page_content for doc in docs]
        context_text = '\n'.join(text_chunks)
        
        if not context_text.strip():
            return RAGQueryResponse(answer="I don't know.")
        
        context_length = len(context_text)
        
        if context_length > 1000:
            system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
            
            Instructions:
            - Give comprehensive and detailed answers when you have sufficient information
            - Include specific details, examples, and elaborations from the context
            - Structure your response clearly with relevant points
            - Use only information from the provided context"""
        elif context_length > 300:
            system_prompt = """You are a helpful assistant that answers questions based on the provided context.
            
            Instructions:
            - Provide clear and informative answers using the available context
            - Include key details but keep responses focused
            - Use only information from the provided context"""
        else:
            system_prompt = """You are a helpful assistant that answers questions based on the provided context.
            
            Instructions:
            - Give concise, direct answers based on the limited information available
            - If context is insufficient for a detailed answer, provide what you can briefly
            - Use only information from the provided context"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {request.question}\n\nAnswer:"}
        ]
        llm = ChatOpenAI(model="gpt-4o")
        response = llm.invoke(messages)
        if isinstance(response.content, str):
            return RAGQueryResponse(answer=response.content)
        else:
            return RAGQueryResponse(answer=str(response.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

 