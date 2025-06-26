"""Scraper using free proxies."""
from __future__ import annotations

import random
from typing import Dict, List

import requests
from scrapers.base import BaseScraper


PROXIES = [
    "http://1.1.1.1:8080",
    "http://2.2.2.2:8080",
]


class FreeProxyScraper(BaseScraper):
    def __init__(self) -> None:
        super().__init__()

    def _get_proxy(self) -> Dict[str, str]:
        proxy = random.choice(PROXIES)
        return {"http": proxy, "https": proxy}

    def get_problems_list(self, limit: int) -> List[str]:
        url = f"https://leetcode.com/api/problems/all/?limit={limit}"
        resp = requests.get(url, proxies=self._get_proxy())
        data = resp.json()
        return [item["stat"]["question__title_slug"] for item in data.get("stat_status_pairs", [])]

    def scrape_problem(self, slug: str) -> Dict:
        url = f"https://leetcode.com/problems/{slug}"
        resp = requests.get(url, proxies=self._get_proxy())
        return {"slug": slug, "description": resp.text}
