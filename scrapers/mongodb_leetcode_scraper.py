"""Entry point coordinating scrapers and storage."""
from __future__ import annotations

import logging
from typing import List

from core.mongodb_manager import MongoDBAtlasManager
from core.vector_search_service import AtlasVectorSearchService
from scrapers.base import BaseScraper
from scrapers.tor_scraper import TORScraper

logging.basicConfig(filename="data/logs/scraper.log", level=logging.INFO)


class MongoDBLeetCodeScraper:
    def __init__(self, scraper: BaseScraper | None = None) -> None:
        self.db = MongoDBAtlasManager()
        self.search = AtlasVectorSearchService(self.db)
        self.scraper = scraper or TORScraper()

    def scrape_and_store_problem(self, slug: str) -> bool:
        problem = self.scraper.scrape_problem(slug)
        logging.info("Scraped %s", slug)
        return self.search.insert_problem_with_embeddings(problem)

    def bulk_scrape_problems(self, problem_limit: int) -> None:
        slugs = self.scraper.get_problems_list(problem_limit)
        for slug in slugs:
            try:
                self.scrape_and_store_problem(slug)
            except Exception as exc:
                logging.exception("Failed to scrape %s: %s", slug, exc)

    def test_vector_search(self) -> List[str]:
        results = self.search.vector_search_problems("array")
        return [doc["slug"] for doc in results]


def main() -> None:
    scraper = MongoDBLeetCodeScraper()
    print(scraper.test_vector_search())


if __name__ == "__main__":
    main()
