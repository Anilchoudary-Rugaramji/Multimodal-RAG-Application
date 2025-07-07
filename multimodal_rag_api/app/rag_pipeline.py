from .config import settings
from unstructured.partition.pdf import partition_pdf
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def store_document_in_vector_db(pdf_path: str, product: str, document: str, persist_directory: str = "./chroma_db"):
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir=settings.EXTRACTED_DOCS_DIR
    )
    texts = []
    current_chunk = ""
    
    for el in elements:
        text = str(el).strip()
        if len(text) < 10:
            continue
            
        current_chunk += text + " "
        
        if len(current_chunk) > 500 or text.endswith('.') and len(current_chunk) > 200:
            if current_chunk.strip():
                texts.append(current_chunk.strip())
            current_chunk = ""
    
    if current_chunk.strip():
        texts.append(current_chunk.strip())
    
    texts = [t for t in texts if len(t) > 50]
    vectorstore = Chroma(
        collection_name="mm_rag",
        embedding_function=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    metadatas = [{"product": product, "document": document, "chunk_id": i} for i in range(len(texts))]
    vectorstore.add_texts(texts, metadatas=metadatas)
    return len(texts) 