"""Combine metadata filters with vector search."""
from __future__ import annotations

from typing import Dict, List

from core.vector_search_service import AtlasVectorSearchService


class HybridQueryEngine:
    def __init__(self, search_service: AtlasVectorSearchService) -> None:
        self.search = search_service

    def search(self, query_text: str, filters: Dict | None = None, limit: int = 5) -> List[Dict]:
        results = self.search.vector_search_problems(query_text, limit=limit)
        if filters:
            results = [doc for doc in results if all(doc.get(k) == v for k, v in filters.items())]
        return results
