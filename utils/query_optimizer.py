"""Placeholder for MongoDB query optimization utilities."""
from __future__ import annotations

from typing import Dict


def add_projection(query: Dict, projection: Dict) -> Dict:
    """Return a new query with a projection."""
    new_query = query.copy()
    new_query["projection"] = projection
    return new_query
