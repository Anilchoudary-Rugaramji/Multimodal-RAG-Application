from .config import settings
from .utils import encode_image

from unstructured.partition.pdf import partition_pdf
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.docstore import InMemoryDocstore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
import uuid
import os

# --- PDF Partitioning and Element Categorization ---
def load_and_categorize_pdf(pdf_path: str):
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir=settings.EXTRACTED_DOCS_DIR
    )
    types = {
        'Header': [], 'Footer': [], 'Title': [],
        'NarrativeText': [], 'Text': [], 'ListItem': [],
        'Image': [], 'Table': []
    }
    for el in elements:
        t = str(type(el))
        for key in types:
            if key in t:
                types[key].append(str(el))
    return types

# --- Image Summarization ---
def image_summarize(img_b64, prompt):
    model = ChatOpenAI(model="gpt-4o")
    response = model.invoke([
        HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
        ])
    ])
    return response.content

def generate_image_based_summaries(image_paths, prompt):
    b64_list, summaries = [], []
    for path in image_paths:
        b64 = encode_image(path)
        b64_list.append(b64)
        summaries.append(image_summarize(b64, prompt))
    return b64_list, summaries

# --- Multi-Vector Retriever Setup ---
def create_multi_vector_retriever(vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, images):
    store = InMemoryStore()
    id_key = 'doc_id'
    retriever = MultiVectorRetriever(vectorstore=vectorstore, docstore=store, id_key=id_key)
    def add_documents(summaries, contents):
        ids = [str(uuid.uuid4()) for _ in contents]
        summary_docs = [Document(page_content=s, metadata={id_key: ids[i]}) for i, s in enumerate(summaries)]
        retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(ids, contents)))
    if text_summaries:
        add_documents(text_summaries, texts)
    if table_summaries:
        add_documents(table_summaries, tables)
    if image_summaries:
        add_documents(image_summaries, images)
    return retriever

def separate_text_and_images(docs):
    text_chunks, image_chunks = [], []
    for doc in docs:
        content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
        if len(content) > 1000 and content[:5] in ['/9j/4', 'iVBOR']:
            image_chunks.append(content)
        elif 'base64' in content.lower() and len(content) > 500:
            image_chunks.append(content)
        else:
            text_chunks.append(content)
    return text_chunks, image_chunks

# --- RAG Prompt ---
rag_prompt = ChatPromptTemplate.from_messages([
    ('system', 'You are a multi-modal assistant answering user queries using both text and images.'),
    ('human', """
Answer the user's question based on the following retrieved content.

## Text:
{context}

## Question:
{input}
""")
])

# --- Main RAG Pipeline Entrypoint ---
class RAGPipeline:
    def __init__(self, pdf_path=None):
        if pdf_path is None:
            pdf_path = settings.PDF_PATH
        self.element_types = load_and_categorize_pdf(pdf_path)
        # For demo, you may want to scan extracted_docs for images/tables
        image_paths = [
            os.path.join(settings.EXTRACTED_DOCS_DIR, f)
            for f in os.listdir(settings.EXTRACTED_DOCS_DIR)
            if f.startswith('figure') and f.endswith('.jpg')
        ]
        table_image_paths = [
            os.path.join(settings.EXTRACTED_DOCS_DIR, f)
            for f in os.listdir(settings.EXTRACTED_DOCS_DIR)
            if f.startswith('table') and f.endswith('.jpg')
        ]
        IMAGE_PROMPT = (
            'You are an assistant tasked with summarizing images for retrieval. Describe the content of this image in detail.'
        )
        TABLE_PROMPT = (
            'You are an assistant tasked with summarizing tables from images for retrieval. Describe the data, key insights, and structure in detail.'
        )
        self.image_b64_list, self.image_summaries = generate_image_based_summaries(image_paths, IMAGE_PROMPT)
        self.table_b64_list, self.table_summaries = generate_image_based_summaries(table_image_paths, TABLE_PROMPT)
        self.vectorstore = Chroma(collection_name='mm_rag', embedding_function=OpenAIEmbeddings())
        self.retriever_multi_vector = create_multi_vector_retriever(
            self.vectorstore,
            text_summaries=None,
            texts=self.element_types['Text'],
            table_summaries=self.table_summaries,
            tables=self.element_types['Table'],
            image_summaries=self.image_summaries,
            images=self.image_b64_list
        )
        self.vision_llm = ChatOpenAI(model='gpt-4o')

    def query(self, question: str) -> str:
        retrieved = self.retriever_multi_vector.invoke(question)
        text_chunks, image_chunks = separate_text_and_images(retrieved)
        messages = [
            {"role": "system", "content": "You are a helpful assistant using both text and image context."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": rag_prompt.format_messages(context='\n'.join(text_chunks), input=question)[0].content}
                ]
            }
        ]
        for img_b64 in image_chunks:
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })
        response = self.vision_llm.invoke(messages)
        if isinstance(response.content, str):
            return response.content
        else:
            return str(response.content)

# --- New: Store document in persistent Chroma vector DB ---
def store_document_in_vector_db(pdf_path: str, product: str, document: str, persist_directory: str = "./chroma_db"):
    # Partition
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir=settings.EXTRACTED_DOCS_DIR
    )
    # For simplicity, treat all text as one type
    texts = [str(el) for el in elements]
    # Embed and store
    vectorstore = Chroma(
        collection_name="mm_rag",
        embedding_function=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    metadatas = [{"product": product, "document": document, "chunk_id": i} for i in range(len(texts))]
    vectorstore.add_texts(texts, metadatas=metadatas)
    return len(texts) 