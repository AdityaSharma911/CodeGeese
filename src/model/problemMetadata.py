from pydantic import BaseModel

class ProblemMeta(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: str
    paid_only: bool
    status: str | None = None
