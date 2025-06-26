"""Base scraper with basic request handling."""
from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List

import requests
from utils.config_loader import get_config


class BaseScraper(ABC):
    def __init__(self) -> None:
        cfg = get_config("free_settings")
        self.delay = cfg["scraper"].get("request_delay_seconds", 2)
        self.max_retries = cfg["scraper"].get("max_retries", 3)

    def _request(self, url: str, headers: Dict | None = None, retries: int | None = None) -> requests.Response:
        retries = self.max_retries if retries is None else retries
        for attempt in range(retries):
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 429:
                    time.sleep(self.delay * (attempt + 1))
                    continue
                resp.raise_for_status()
                time.sleep(self.delay + random.random())
                return resp
            except requests.RequestException:
                time.sleep(self.delay * (attempt + 1))
        raise RuntimeError(f"Failed request for {url}")

    @abstractmethod
    def get_problems_list(self, limit: int) -> List[str]:
        pass

    @abstractmethod
    def scrape_problem(self, slug: str) -> Dict:
        pass
