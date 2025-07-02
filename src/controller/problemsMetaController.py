# src/controllers/problem_controller.py

from fastapi import APIRouter
from src.service.pullLeetcodeSlugs import fetch_all_problem_metadata

router = APIRouter(prefix="/problems", tags=["Problems"])

@router.post("/sync")
def sync_problems():
    count = fetch_all_problem_metadata()
    return {"message": f"✅ Synced {count} problems from LeetCode."}

