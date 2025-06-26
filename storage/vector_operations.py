"""Helpers for embeddings storage."""
from __future__ import annotations

from typing import Any, Dict

from core.mongodb_manager import MongoDBAtlasManager


class VectorOperations:
    def __init__(self, db: MongoDBAtlasManager) -> None:
        self.db = db

    def store_embedding(self, slug: str, embedding: list[float]) -> None:
        self.db.embeddings.update_one({"slug": slug}, {"$set": {"embedding": embedding}}, upsert=True)

    def fetch_embedding(self, slug: str) -> Dict[str, Any] | None:
        return self.db.embeddings.find_one({"slug": slug})
