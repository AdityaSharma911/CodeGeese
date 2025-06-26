"""MongoDB Atlas connection manager."""
from __future__ import annotations

import os
from typing import Any, Dict

from pymongo import MongoClient


class MongoDBAtlasManager:
    """Simple wrapper around MongoClient."""

    def __init__(self, connection_string: str | None = None) -> None:
        self.connection_string = connection_string or os.getenv("MONGODB_ATLAS_URI")
        if not self.connection_string:
            raise ValueError("MongoDB connection string not provided")
        self.client = MongoClient(self.connection_string)
        cfg = get_config("mongodb_config")
        self.db = self.client[cfg["database"]]
        self.problems = self.db[cfg["problems_collection"]]
        self.embeddings = self.db[cfg["embeddings_collection"]]
        self.progress = self.db[cfg["scraping_progress_collection"]]
        self._ensure_vector_indexes()

    def _ensure_vector_indexes(self) -> None:
        """Create vector indexes if they do not exist."""
        # Placeholder for actual index creation
        self.problems.create_index("slug", unique=True)

    def test_connection(self) -> bool:
        """Return True if the server is reachable."""
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """Return basic DB stats."""
        return self.db.command("dbstats")


from utils.config_loader import get_config
