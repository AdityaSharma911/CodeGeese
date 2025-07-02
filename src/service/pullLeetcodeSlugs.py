import httpx
from src.service.mongo_service import insert_one
from src.model.problemMetadata import ProblemMeta
from src.service.mongo_service import init_mongo

DIFFICULTY_MAP = {1: "Easy", 2: "Medium", 3: "Hard"}

def fetch_all_problem_metadata(collection_name: str = "problems_metadata"):
    url = "https://leetcode.com/api/problems/all/"
    response = httpx.get(url)
    data = response.json()

    for entry in data["stat_status_pairs"]:
        stat = entry["stat"]
        difficulty = entry["difficulty"]["level"]

        doc = ProblemMeta(
            id=stat["frontend_question_id"],
            slug=stat["question__title_slug"],
            title=stat["question__title"],
            difficulty=DIFFICULTY_MAP.get(difficulty, "Unknown"),
            paid_only=entry["paid_only"],
            status=entry.get("status", None),
        )

        insert_one(doc, collection_name)
        print(f"✅ Inserted {doc.slug}")

if __name__ == "__main__":
    init_mongo()
    fetch_all_problem_metadata()
