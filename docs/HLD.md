# High-Level Design: Zero-Cost LeetCode Scraper

This document outlines the architecture for a LeetCode scraping system designed to operate at zero cost while providing vector search capabilities. It summarizes the overall components and their interactions.

## 1. Goals
- Collect LeetCode problems and metadata for training an AI agent.
- Store problems and embeddings in a free or open-source vector database (MongoDB Atlas Free Tier recommended).
- Support rate-limited scraping with proxy rotation and fault tolerance.

## 2. System Overview
The scraper is composed of multiple modules grouped by responsibility:

1. **Scrapers** – Retrieve problem listings and details from LeetCode using HTTP requests. Different implementations (TOR, free proxies, stealth browser) handle rate limits and anti-bot measures.
2. **Core Services** – Manage database connections and vector operations. Includes the MongoDB manager and vector search service.
3. **Storage Helpers** – Provide CRUD utilities and caching to reduce network calls and database writes.
4. **Utilities** – Embedding generation, configuration loading, and query optimization helpers.
5. **Data Store** – MongoDB Atlas (M0) cluster storing problem documents and embeddings with vector search indexes. Optionally, a local Chroma DB can be used for offline deployments.

## 3. Component Responsibilities
### 3.1 Request Manager
- Handles HTTP requests with rotating headers and optional proxy usage.
- Implements exponential backoff when rate-limited.

### 3.2 Scraper Logic
- Fetches problem lists and individual problem pages via LeetCode APIs or HTML.
- Parses metadata (title, difficulty, tags) and problem descriptions.
- Invokes the Solution Collector to attach various solution approaches.

### 3.3 Solution Collector
- Stores brute-force, intermediate, and optimized solutions.
- Allows future integration of community or self-generated solutions.

### 3.4 Vector and Database Layer
- `MongoDBAtlasManager` connects to an Atlas cluster and ensures vector indexes exist.
- `AtlasVectorSearchService` generates embeddings with `sentence-transformers`, caches them locally, and provides search utilities.

### 3.5 Rate-Limit Handler
- Centralized logic to track request counts and wait times.
- Supports random delays and proxy rotation to avoid detection.

## 4. Data Flow
1. The scraper fetches a list of problem slugs.
2. For each slug, it retrieves the problem detail page and solutions.
3. Text data is preprocessed and converted into embeddings.
4. The combined document (metadata, text, embeddings) is inserted into MongoDB Atlas.
5. Users query the data using vector search or hybrid metadata filters.

## 5. Deployment
- Delivered as a Python package with a CLI entry point (e.g., `mongodb_leetcode_scraper.py`).
- Dockerfile provided for consistent environment setup.
- Configuration files (`.env`, YAML) define connection strings and scraping options.

## 6. Scalability and Cost Control
- The Atlas Free Tier limits storage to 512MB; scraping tasks monitor usage and pause when nearing the cap.
- Embedding caching minimizes compute and network overhead.
- Local Chroma DB is available for unlimited storage when needed, mirroring the Atlas interfaces.

---
This HLD complements the accompanying low-level design and serves as a roadmap for implementing a zero-cost LeetCode scraper with built-in vector search.
