from pydantic import BaseModel
from typing import List

class TopicTag(BaseModel):
    name: str
    slug: str

class CodeSnippet(BaseModel):
    lang: str
    code: str

class ProblemDetail(BaseModel):
    metadata_id: str
    id: int
    slug: str
    title: str
    difficulty: str
    content: str
    stats: str
    tags: List[TopicTag]
    code_snippets: List[CodeSnippet]
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
