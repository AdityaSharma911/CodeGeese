"""CRUD helpers for MongoDB collections."""
from __future__ import annotations

from typing import Any, Dict

from core.mongodb_manager import MongoDBAtlasManager


class AtlasOperations:
    def __init__(self, db: MongoDBAtlasManager) -> None:
        self.db = db

    def upsert_problem(self, doc: Dict[str, Any]) -> None:
        self.db.problems.update_one({"slug": doc["slug"]}, {"$set": doc}, upsert=True)

    def fetch_problem(self, slug: str) -> Dict[str, Any] | None:
        return self.db.problems.find_one({"slug": slug})

    def mark_progress(self, slug: str, error: bool = False) -> None:
        self.db.progress.update_one({"slug": slug}, {"$set": {"error": error}}, upsert=True)
