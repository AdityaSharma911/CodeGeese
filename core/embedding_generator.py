"""Wrapper around sentence-transformers to generate embeddings."""
from __future__ import annotations

import os
from typing import List

from sentence_transformers import SentenceTransformer

from utils.config_loader import get_config


class EmbeddingGenerator:
    """Generate and cache text embeddings."""

    def __init__(self) -> None:
        cfg = get_config("embedding_config")
        model_name = cfg.get("model", "all-MiniLM-L6-v2")
        cache_dir = cfg.get("cache_dir", "data/cache/embeddings")
        os.makedirs(cache_dir, exist_ok=True)
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)

    def generate(self, text: str) -> List[float]:
        return self.model.encode(text, show_progress_bar=False).tolist()
