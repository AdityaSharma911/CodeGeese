```
# CodeGeese - LeetCode Scraper & AI Agent (LLD)

CodeGeese is a zero-cost AI-powered LeetCode scraping and semantic search system built using Python, MongoDB, and Qdrant. It focuses on scalable ingestion of DSA problems and vector-powered retrieval via custom FastAPI endpoints. Designed for long-term extensibility and free-tier usage.

---

## Technology Stack

| Component      | Technology                    |
| -------------- | ----------------------------- |
| Language       | Python 3.11+                  |
| API Framework  | FastAPI                       |
| DB (Metadata)  | MongoDB Atlas (Free Tier - M0)|
| DB (Vectors)   | Qdrant Cloud (Free Tier)      |
| Embeddings     | SentenceTransformers (MiniLM) |
| Task Runner    | CLI Script/Async Worker       |
| Proxy Handling | TOR via `stem` + `httpx`      |
| Environment    | Python Virtualenv + `.env`    |

---

## Directory Structure

```

CodeGeese/
├── src/
│   ├── controller/            # FastAPI route handlers
│   ├── service/               # Mongo + Qdrant logic
│   ├── scrapers/              # LeetCode scraping modules
│   ├── utils/                 # config, rate limiters, proxies
│   ├── model/                 # Pydantic models
│   └── main.py                # API server entry
├── .env
├── requirements.txt
└── README.md

````

---

## Modules Breakdown

### `main.py`

- Initializes FastAPI app
- Bootstraps Mongo and Qdrant on startup
- Registers API routers

### `controller/leetCodeProbListController.py`

- `GET /leetcode/sync`
- Triggers full problem metadata ingestion from `https://leetcode.com/api/problems/all/`
- Stores in MongoDB if not already present

### `service/mongo_service.py`

- Handles MongoDB connection (singleton pattern)
- Abstracted methods: `insert_one`, `find`, `update`, etc.
- Dynamic collection support
- Pydantic model compatibility

### `service/vector_service.py`

- Initializes Qdrant collections
- Stores MiniLM-embedded vectors with slug-based payloads
- Performs similarity search (cosine)

### `scrapers/problem_metadata_scraper.py`

- Fetches problems from public LeetCode API
- Converts entries into `ProblemMeta` schema
- Inserts new entries to MongoDB

### `scrapers/problem_statement_scraper.py` (WIP)

- Scrapes individual problem pages via GraphQL + HTML fallback
- Uses rotating proxies and TOR IP switching
- Plans to extract content + editorial (if available)

### `model/problem.py`

```python
class ProblemMeta(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: str
    paid_only: bool
    status: Optional[str] = None
````

---

## Proxy and Rate Limiting Strategy

### Proxy Setup

* Utilizes `stem` to control the TOR daemon via `9051` port
* Automatically rotates IP using `NEWNYM` signal
* `httpx` client is routed through the TOR proxy (`socks5h://127.0.0.1:9050`)
* Requests are anonymous and bypass rate-based bans

### Rate Limiter

* Manual sleep interval between requests
* Future implementation:

  * Exponential backoff on 403/429
  * Retry logic with max attempts
  * Queue for controlled concurrency

---

## Current Data Flow

### Problem Metadata Sync

1. Client hits `GET /leetcode/sync`
2. Controller invokes `fetch_all_problem_metadata()`
3. Data pulled from LeetCode's public API
4. Each problem is checked and inserted into Mongo if new

### Problem Detail Fetch (Planned)

1. Slug-based GraphQL query to fetch full problem
2. HTML fallback scraper with headless browser (optional)
3. Content embedded using `MiniLM`
4. Vector stored in Qdrant
5. Problem metadata stored in Mongo (if missing)

---

## Completed

* [x] FastAPI app with startup hooks
* [x] MongoDB integration and schema validation
* [x] Public API ingestion of all problem metadata
* [x] TOR-based proxy routing via `stem`
* [x] Verified LeetCode GraphQL scraping using rotating IP

---

## In Progress

* [ ] Problem statement + editorial fetch
* [ ] Embedding generation with `MiniLM-L6-v2`
* [ ] Vector insertion with `slug` mapping
* [ ] REST endpoint for semantic search

---

## Next Steps

1. Complete `problem_scraper.py` for slug-based GraphQL fetch
2. Add embeddings and vector indexing
3. Build `GET /search?query=...` API
4. Add community solution support (via Discuss)

---

## Notes

* Official editorial content is only accessible via Premium. We fallback to community solutions where possible.
* Proxy routing via TOR significantly improves reliability and avoids IP bans when querying GraphQL.

```