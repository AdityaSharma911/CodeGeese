"""Scraper using TOR network for requests."""
from __future__ import annotations

from typing import Dict, List

import requests
from requests.sessions import Session

from scrapers.base import BaseScraper


class TORScraper(BaseScraper):
    def __init__(self) -> None:
        super().__init__()
        self.session = Session()
        self.session.proxies = {
            "http": "socks5h://localhost:9050",
            "https": "socks5h://localhost:9050",
        }

    def get_problems_list(self, limit: int) -> List[str]:
        url = f"https://leetcode.com/api/problems/all/?limit={limit}"
        resp = self.session.get(url)
        data = resp.json()
        return [item["stat"]["question__title_slug"] for item in data.get("stat_status_pairs", [])]

    def scrape_problem(self, slug: str) -> Dict:
        url = f"https://leetcode.com/problems/{slug}"
        resp = self.session.get(url)
        return {"slug": slug, "description": resp.text}
