from typing import Dict, List, Optional
from pydantic import BaseModel

class ProblemSolution(BaseModel):
    metadata_id: str
    slug: str
    title: str
    difficulty: str
    content: str
    pattern: Optional[str]
    tags: List[str]
    solutions: Dict[str, str]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True