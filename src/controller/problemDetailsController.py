from fastapi import APIRouter
from src.service.pullProblems import pull_problem_dets

router = APIRouter(prefix="/problems", tags=["Problems"])

@router.post("/scrape")
def scrape_problem_details():
    print("Scraping problem details...")
    pull_problem_dets()
    return {"message": "✅ Problem details scraping initiated."}
