from pydantic import BaseModel
from typing import List

class AskRequest(BaseModel):
    question: str
    top_k: int = 3

class AskAnswer(BaseModel):
    answer: str
    citations: List[str]
