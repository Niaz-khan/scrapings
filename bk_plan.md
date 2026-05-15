Here is a clean, production-oriented **`PLAN.md`** for your project. It is structured so you can directly use it in a repo and evolve it into a real scraping system (later DRF-ready).

---

````markdown
# PLAN.md

# 🌐 Universal Web Extraction Engine (UWEE)

## 🎯 Objective

Build a production-grade, universal web extraction system capable of:

- Extracting data from static HTML sites
- Handling JavaScript-heavy SPAs (React, Vue, Next.js)
- Capturing backend API traffic (XHR / Fetch / GraphQL)
- Supporting infinite scroll and lazy-loaded content
- Performing recursive crawling
- Producing structured, machine-readable datasets
- Eventually exposing functionality via a DRF API

---

# 🧠 Core Design Philosophy

This system is NOT a traditional scraper.

It is a **browser intelligence + API discovery engine**.

Key principle:

> Prefer API extraction over HTML parsing whenever possible.

---

# 🏗️ System Architecture

## Phase 1: Browser Extraction Layer

- Tooling: Playwright (Chromium)
- Responsibilities:
  - Load full page (JS execution enabled)
  - Render SPA applications
  - Handle redirects and hydration
  - Simulate user interactions

### Output:
- Fully rendered DOM
- HTML snapshot
- Screenshots

---

## Phase 2: Network Intelligence Layer

- Capture all network traffic:
  - HTTP requests
  - HTTP responses
  - XHR / Fetch calls
  - GraphQL endpoints
  - JSON API payloads

### Responsibilities:
- Log all requests/responses
- Identify API endpoints
- Store JSON responses
- Detect failed requests
- Classify traffic types

### Output:
```json
{
  "api_endpoints": [],
  "graphql_calls": [],
  "json_payloads": [],
  "failed_requests": []
}
````

---

## Phase 3: HTML Parsing Layer

* Tooling:

  * BeautifulSoup
  * lxml

### Responsibilities:

* Extract:

  * Titles
  * Headings
  * Paragraphs
  * Links
  * Images
  * Forms
  * Metadata
* Extract embedded data:

  * JSON-LD
  * Next.js `__NEXT_DATA__`
  * Inline scripts

---

## Phase 4: Smart Data Extraction Layer

* Detect structured data sources:

  * Schema.org
  * JSON-LD
  * Embedded application state
  * API payload patterns

### Goal:

Minimize reliance on HTML parsing.

---

## Phase 5: Crawling Engine

* Recursive crawling system
* Domain-aware navigation
* URL deduplication
* Depth control
* Rate limiting

### Features:

* BFS/DFS crawling modes
* Domain restriction
* Crawl queue system

---

## Phase 6: Storage Layer

* JSON output (MVP)
* Future:

  * PostgreSQL (structured data)
  * Redis (queue/cache)
  * S3/MinIO (assets)
  * Elasticsearch (search indexing)

---

## Phase 7: AI Extraction Layer (Optional Upgrade)

* Use LLM-based parsing for:

  * messy HTML
  * inconsistent layouts
  * content summarization
  * semantic extraction

---

## Phase 8: API Layer (DRF)

Expose system via REST API:

### Endpoints:

```
POST /extract/
POST /crawl/
GET  /status/
GET  /result/{id}/
```

### Features:

* Async task execution (Celery)
* Job tracking system
* Result caching

---

# ⚙️ Core Modules (Python)

```
universal_scraper/
│
├── extractor.py          # Main orchestrator
├── browser.py           # Playwright engine
├── network.py           # request/response collector
├── parser.py            # BeautifulSoup extraction
├── crawler.py           # recursive crawling engine
├── storage.py           # output handling
├── utils.py             # helpers
├── config.py            # settings
│
└── output/
```

---

# 🔄 Execution Flow

```text
Input URL
    ↓
Playwright Browser Loads Page
    ↓
Network Traffic Captured
    ↓
DOM Fully Rendered
    ↓
HTML Snapshot Taken
    ↓
API Calls Extracted
    ↓
Structured Data Parsed
    ↓
Assets Extracted
    ↓
Output Stored (JSON)
```

---

# 🚀 MVP MILESTONES

## Milestone 1 (CURRENT)

* Playwright browser extraction
* HTML parsing
* Auto-scroll
* Basic logging

---
<!--  -->
## Milestone 2 (NEXT)

* Full network interception system
* API discovery engine
* JSON payload storage
* Request/response classification

---

## Milestone 3

* Recursive crawler
* URL deduplication
* Crawl depth control

---

## Milestone 4

* Structured data normalization
* JSON-LD + Next.js extraction

---

## Milestone 5

* Performance optimization
* Parallel crawling (async workers)

---

## Milestone 6

* DRF API wrapper
* Async job system (Celery)

---

# 🧪 Success Criteria

System is considered successful when:

* Can extract data from React/Next.js sites
* Can bypass reliance on HTML parsing
* Can detect hidden API endpoints
* Can recursively crawl a domain
* Outputs structured JSON consistently

---

# ⚠️ Known Challenges

* Anti-bot protection (Cloudflare, Akamai)
* Infinite network activity blocking `networkidle`
* SPA hydration timing issues
* Dynamic API token authentication
* Rate limiting / IP bans

---

# 🧭 Long-Term Vision

This system evolves into:

* Firecrawl-like extractor
* Apify-style crawler
* AI-ready web data pipeline
* Backend data intelligence engine

Eventually:

> A universal web-to-structured-data infrastructure layer.

---

# 📌 Rules

* Always prefer API extraction over HTML parsing
* Never rely solely on static HTML
* Always log network activity
* Always assume JS rendering is required
* Build incrementally (never over-engineer early)

```

---

If you want next step, I can help you build:

- :contentReference[oaicite:0]{index=0}
- OR :contentReference[oaicite:1]{index=1}
- OR :contentReference[oaicite:2]{index=2}

Just say what you want next.
```
