"""Simple cache manager with TTL cleanup."""
from __future__ import annotations

import os
import time
from typing import Optional


class CacheManager:
    def __init__(self, base_dir: str = "data/cache", ttl_seconds: int = 60 * 60 * 24) -> None:
        self.base_dir = base_dir
        self.ttl = ttl_seconds
        os.makedirs(self.base_dir, exist_ok=True)

    def put(self, name: str, data: bytes) -> str:
        path = os.path.join(self.base_dir, name)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def get(self, name: str) -> Optional[bytes]:
        path = os.path.join(self.base_dir, name)
        if not os.path.exists(path):
            return None
        if time.time() - os.path.getmtime(path) > self.ttl:
            os.remove(path)
            return None
        with open(path, "rb") as f:
            return f.read()

