# Low-Level Design: Zero-Cost LeetCode Scraper

This document describes the low-level design of the **LeetCode Scraper** that integrates with MongoDB Atlas Free Tier (M0) for vector search and storage. The design aligns with the team lead's revised HLD and emphasizes zero-cost operation.

## 1. Technology Stack
- **Language:** Python 3.9+
- **Database:** MongoDB Atlas Free Tier (M0) with Vector Search
- **Vector Embeddings:** `sentence-transformers` (e.g., `all-MiniLM-L6-v2`)
- **Web Scraping:** Requests + BeautifulSoup, optional TOR/proxy rotation
- **Containerization:** Docker (for local or server deployment)

Directory structure (simplified):
```
leetcode-scraper-mongodb/
├── config/
├── core/
├── scrapers/
├── storage/
├── utils/
└── data/
```

## 2. Configuration Files
- `config/free_settings.yaml` – global options for zero-cost mode.
- `config/mongodb_config.yaml` – connection string, database/collection names, index definitions.
- `config/embedding_config.yaml` – embedding model parameters and caching settings.

These YAML files are loaded on startup via a helper function (`utils/config_loader.py`).

## 3. Core Modules
### 3.1 MongoDBAtlasManager (`core/mongodb_manager.py`)
Responsible for connecting to MongoDB Atlas and providing access to collections.

Key methods:
- `__init__(connection_string: str)` – establish client, set up collections.
- `_ensure_vector_indexes()` – create or validate vector indexes (description and solution embeddings).
- `test_connection() -> bool` – verify the connection by issuing a `ping` command.
- `get_database_stats() -> Dict` – return `dbStats` output for monitoring usage.

Collections:
- `problems_collection` – stores problem metadata and embeddings.
- `embeddings_collection` – optional separate collection for embeddings if needed.
- `scraping_progress` – tracks completed slugs for resumable scraping.

### 3.2 AtlasVectorSearchService (`core/vector_search_service.py`)
Wraps embedding generation and MongoDB Atlas vector search.

Important functions:
- `generate_embedding(text: str) -> List[float]` – produce embeddings with local cache (pickle files under `data/cache/embeddings`).
- `insert_problem_with_embeddings(problem_data: Dict) -> bool` – attach embeddings to `problem_data` then insert into `problems_collection`.
- `vector_search_problems(query_text: str, filters: Dict, limit: int) -> List[Dict]` – execute `$vectorSearch` pipeline with optional filters.
- `hybrid_search(...)` – convenience method to search by text plus metadata filters.
- `find_similar_problems(problem_slug: str, limit: int)` – get problems with embeddings similar to a specified slug.

### 3.3 EmbeddingGenerator (`core/embedding_generator.py`)
Standalone utility that exposes a single function `generate(text: str)` for use in other modules. Utilizes `sentence-transformers` and caches results. This is separated to allow alternative embedding models (e.g., open-source models) without changes to the rest of the code base.

### 3.4 HybridQueryEngine (`core/hybrid_query_engine.py`)
Combines metadata filtering with vector search. Provides query composition helpers and supports pagination. Utilizes methods from `AtlasVectorSearchService` internally.

## 4. Scrapers
### 4.1 BaseScraper (`scrapers/base.py`)
Defines common logic for sending HTTP requests, handling rate limits, and parsing HTML/JSON. Implements headers rotation, exponential backoff, and minimal caching.

Key methods:
- `_request(url, headers=None, retries=3)` – handles HTTP requests with delays and error handling.
- `scrape_problem(slug: str) -> Dict` – abstract method to retrieve a single problem.
- `get_problems_list(limit: int) -> List[str]` – abstract method to fetch a list of problem slugs.

### 4.2 TORScraper (`scrapers/tor_scraper.py`)
Inherits from `BaseScraper` and routes requests through the TOR network using `stem` or preconfigured SOCKS proxy. Provides additional delay to avoid triggering LeetCode rate limits.

### 4.3 FreeProxyScraper (`scrapers/free_proxy_scraper.py`)
Similar to `TORScraper` but uses a pool of free proxies. Includes proxy health checks and rotation logic.

### 4.4 StealthScraper (`scrapers/stealth_scraper.py`)
Implements browser automation (e.g., Selenium with undetected Chrome) for pages that require JavaScript. Utilized only when necessary due to higher overhead.

### 4.5 MongoDBLeetCodeScraper (`scrapers/mongodb_leetcode_scraper.py`)
Main entry point coordinating all components.

Functions:
- `scrape_and_store_problem(slug: str) -> bool` – orchestrates scraping, embedding generation, and insertion into MongoDB.
- `bulk_scrape_problems(problem_limit: int)` – loops through problem slugs and calls `scrape_and_store_problem` with progress logging and storage checks.
- `test_vector_search()` – quick test to validate stored embeddings and vector search queries.

## 5. Storage Helpers
### 5.1 AtlasOperations (`storage/atlas_operations.py`)
Wraps CRUD operations for the MongoDB collections. Provides methods to upsert documents, fetch by slug, or mark scraping progress.

### 5.2 VectorOperations (`storage/vector_operations.py`)
Utility functions for storing and retrieving embeddings outside of the main problem collection. Useful if embeddings are large and need separate management.

### 5.3 CacheManager (`storage/cache_manager.py`)
Controls local caching of raw HTML, JSON, or embeddings. Implements TTL-based cleanup to stay within disk space limits.

## 6. Utility Modules
- `utils/free_embedding_models.py` – exposes available open-source embedding models and downloads them if missing.
- `utils/data_preprocessor.py` – cleans HTML to plain text, normalizes whitespace, and removes code blocks before embedding.
- `utils/query_optimizer.py` – houses functions to tune MongoDB queries (projection, index hints, etc.).
- `utils/config_loader.py` – small helper that loads YAML configs and environment variables.

## 7. Data Flow
1. **Initialization**
   - Load configs and environment variables.
   - Instantiate `MongoDBAtlasManager` and verify connection.
   - Create `AtlasVectorSearchService` and designated scraper (TOR, proxy, or stealth).
2. **Problem List Retrieval**
   - `get_problems_list()` fetches a paginated list of slugs from LeetCode API or HTML. Each slug is queued for scraping.
3. **Problem Scraping**
   - For each slug:
     - Call `scrape_problem(slug)` to fetch the problem statement, difficulty, tags, etc.
     - Save raw HTML to `data/temp/` (optional) then parse to clean text.
4. **Embedding Generation**
   - Description and solution texts are passed through `EmbeddingGenerator`.
   - Embeddings are cached locally and attached to `problem_data`.
5. **Data Storage**
   - Use `AtlasOperations` to insert/update the problem document in MongoDB.
   - Optionally store embeddings separately via `VectorOperations`.
6. **Rate Limiting**
   - Between requests, apply a random delay (`2–5s` by default) and adjust via exponential backoff on errors or HTTP 429 responses.
7. **Progress Tracking**
   - After each successful insertion, record the slug in `scraping_progress` to allow resuming after interruptions.
8. **Vector Search**
   - Users can query scraped problems using `AtlasVectorSearchService.vector_search_problems()` or `hybrid_search()`.

## 8. Error Handling
- Network and HTTP errors are retried with exponential backoff up to a maximum threshold.
- All exceptions are logged to `data/logs/scraper.log` with timestamps and stack traces.
- Failed slugs are stored in `scraping_progress` with an error flag for later retry.

## 9. Deployment Notes
- Provide a Dockerfile that installs Python dependencies and sets the entrypoint to `scrapers/mongodb_leetcode_scraper.py`.
- Use `.env` file for `MONGODB_ATLAS_URI`. The file is excluded by `.gitignore`.
- Recommended to run the scraper in batches (e.g., 50 problems) to stay within the free tier storage cap (512MB).

## 10. Future Extensions
- Add `chroma_manager.py` for local Chroma DB support with the same interfaces (`add_problem`, `search_problems`).
- Integrate other problem sources (e.g., GeeksforGeeks, Codeforces) via new scraper classes.
- Build a simple CLI or REST API to expose search functionality to the training pipeline.

---
This LLD provides detailed implementation guidance for building the LeetCode scraper with MongoDB Atlas integration, caching, rate limiting, and vector search. It can serve as a blueprint for developers to implement the individual modules and ensure consistent structure across the project.

