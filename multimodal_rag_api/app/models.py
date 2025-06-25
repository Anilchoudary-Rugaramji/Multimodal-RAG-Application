from pydantic import BaseModel

class RAGQueryRequest(BaseModel):
    question: str
    product: str

class RAGQueryResponse(BaseModel):
    answer: str 