from pydantic import BaseModel
from typing import List, Any

class ChatRequest(BaseModel):
    dataset_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    sql: str
    columns: List[str]
    rows: List[List[Any]]
