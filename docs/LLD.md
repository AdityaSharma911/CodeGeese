# CodeGeese - LeetCode Scraper (Custom LLD)

This document provides a low-level design (LLD) for the CodeGeese project, a zero-cost AI-powered LeetCode scraping and vector search agent using MongoDB Atlas and Qdrant. The goal is to structure the project for long-term maintainability and scalability while keeping it budget-friendly.

---

## Technology Stack

| Component      | Technology                    |
| -------------- | ----------------------------- |
| Language       | Python 3.11+                  |
| API Framework  | FastAPI                       |
| DB (Metadata)  | MongoDB Atlas Free Tier (M0)  |
| DB (Vectors)   | Qdrant Cloud Free Tier        |
| Embeddings     | SentenceTransformers (MiniLM) |
| Task Runner    | CLI/Script-driven             |
| Proxy Handling | Free Proxy Rotation (httpx)   |
| Environment    | Python Virtualenv + `.env`    |

---

## Directory Structure

```
CodeGeese/
├── src/
│   ├── controller/            # FastAPI endpoints
│   ├── service/               # DB connectors, vector ops
│   ├── scrapers/              # LeetCode metadata + problem scrapers
│   ├── utils/                 # config, settings, rate limiters
│   ├── model/                 # Pydantic schemas
│   └── main.py                # FastAPI entrypoint
├── .env
├── requirements.txt
└── README.md
```

---

## Modules Breakdown

### 1. `main.py`

* Sets up FastAPI app lifecycle
* Initializes Mongo and Qdrant connections on startup
* Mounts all routers (e.g., LeetCode sync)

### 2. `controller/leetCodeProbListController.py`

* Endpoint: `GET /leetcode/sync`
* Triggers fetch from LeetCode API `/api/problems/all/`
* Stores metadata in MongoDB with optional collection override

### 3. `service/mongo_service.py`

* Initializes Mongo connection (singleton)
* CRUD operations (`insert_one`, `find_one`, `update_one`, `delete_one`) with dynamic collection names
* Accepts Pydantic model instances or dicts

### 4. `service/vector_service.py`

* Initializes Qdrant collection
* Inserts vectors with payload (question metadata)
* Performs vector search with similarity cutoff and top-K results

### 5. `scrapers/problem_metadata_scraper.py`

* Fetches all LeetCode problems with basic info via public API
* Converts entries into `ProblemMeta` Pydantic model
* Persists in MongoDB

### 6. `model/problem.py`

* Pydantic schema: `ProblemMeta`

  ```python
  class ProblemMeta(BaseModel):
      id: int
      slug: str
      title: str
      difficulty: str
      paid_only: bool
      status: Optional[str] = None
  ```

---

## Data Flow (Metadata Ingestion)

1. **Trigger** via `curl` or browser: `GET /leetcode/sync`
2. `controller` calls `fetch_all_problem_metadata()` from scraper
3. Scraper pulls `https://leetcode.com/api/problems/all/`
4. Each problem is transformed into a `ProblemMeta` model
5. Each entry is inserted to Mongo via `insert_one()` if not already present

---

## Future Plan (Scraping Full Problem Statements)

* Each slug will be scraped individually from its LeetCode problem page
* Rate-limited with proxy rotation
* Extracted content will be embedded using MiniLM
* Both statement and embedding stored in vector DB (Qdrant)

---

## Rate Limiting Strategy (To Be Implemented)

* Retry wrapper with exponential backoff
* Free proxy list rotation for requests
* HTTP 429/403 detectors
* Optional TOR-based `httpx` client

---

##  Vector Search (Planned)

* Input: Free text or existing question slug
* Transform query into vector using `MiniLM`
* Search top-K similar vectors using cosine similarity in Qdrant
* Return matched problem metadata from Mongo

---

## Completed So Far

* [x] MongoDB integration with dynamic collections
* [x] Pydantic modeling for clean validation
* [x] Metadata scraper from `/api/problems/all/`
* [x] FastAPI-based controller and server lifecycle
* [x] Qdrant client connection and collection bootstrapping

---

## In Progress

* [ ] Full problem scraper per slug
* [ ] Embedding generation & vector storage
* [ ] Rate limiter with rotating proxies
* [ ] REST API for vector search and hybrid metadata filters

---

## Next Steps

1. Create `problem_scraper.py` for HTML scraping of LeetCode statements
2. Add sentence embedding generation
3. Index embeddings in Qdrant and link by problem slug
4. Add API to query by natural language ("Find 2-pointer array problems")

---

This custom LLD reflects the current architecture of CodeGeese, designed for low-cost scraping, flexible Mongo + vector DB support, and clean separation of concerns.
