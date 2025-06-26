"""Vector search utilities built on top of MongoDB."""
from __future__ import annotations

from typing import Dict, List

from utils.data_preprocessor import clean_html
from core.embedding_generator import EmbeddingGenerator
from core.mongodb_manager import MongoDBAtlasManager


class AtlasVectorSearchService:
    def __init__(self, db: MongoDBAtlasManager) -> None:
        self.db = db
        self.embedder = EmbeddingGenerator()

    def insert_problem_with_embeddings(self, problem_data: Dict) -> bool:
        description = clean_html(problem_data.get("description", ""))
        problem_data["embedding"] = self.embedder.generate(description)
        self.db.problems.update_one(
            {"slug": problem_data["slug"]},
            {"$set": problem_data},
            upsert=True,
        )
        return True

    def vector_search_problems(self, query_text: str, limit: int = 5) -> List[Dict]:
        query_vec = self.embedder.generate(query_text)
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": query_vec,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                }
            }
        ]
        return list(self.db.problems.aggregate(pipeline))
