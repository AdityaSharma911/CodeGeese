from fastapi import APIRouter
from src.service.batch_problem_solutions import batch_process_problem_solutions

router = APIRouter(prefix="/problem-solutions", tags=["ProblemSolutions"])

@router.post("/batch-process")
def batch_process_solutions():
    batch_process_problem_solutions()
    return {"message": "✅ Batch processing of problem solutions initiated."}
