````markdown
# 🌐 Universal Web Extraction Engine (UWEE)

# 📘 PLAN.md

---

# 🎯 Objective

Build a production-grade, universal web extraction system capable of:

- Extracting data from static HTML sites
- Handling JavaScript-heavy SPAs (React, Vue, Next.js)
- Capturing backend API traffic (XHR / Fetch / GraphQL)
- Supporting infinite scroll and lazy-loaded content
- Performing recursive crawling
- Producing structured, machine-readable datasets
- Supporting semantic and AI-assisted extraction
- Scaling into a distributed extraction platform
- Eventually exposing functionality via a DRF API

---

# 🧠 Core Design Philosophy

This system is NOT a traditional scraper.

It is a:

> Browser Intelligence + API Discovery + Structured Data Extraction Platform

---

# 🔑 Core Principle

> Prefer API extraction over HTML parsing whenever possible.

Extraction priority:

```text
1. Captured APIs
2. JSON payloads
3. JSON-LD
4. Hydration state
5. Embedded configs
6. HTML parsing
7. AI extraction fallback
```

---

# 🏗️ High-Level Architecture

```text
Browser Rendering
        ↓
Network Intelligence
        ↓
Raw HTML Parsing
        ↓
Structured Parsing
        ↓
Data Normalization
        ↓
Data Classification
        ↓
Storage Layer
        ↓
DRF API Layer
        ↓
Distributed Workers
        ↓
AI Extraction
```

---

# ❌ Anti-Pattern (Avoid)

```text
Browser
    ↓
DRF
    ↓
Parsing
```

This tightly couples:

- rendering
- parsing
- business logic
- orchestration

and becomes difficult to scale or maintain.

---

# ✅ Correct Architectural Separation

| Layer | Responsibility |
|---|---|
| Browser Layer | Rendering |
| Network Layer | Traffic Intelligence |
| Parsing Layer | Raw Extraction |
| Intelligence Layer | Semantic Understanding |
| Normalization Layer | Unified Schemas |
| Crawl Layer | Traversal |
| Storage Layer | Persistence |
| API Layer | Orchestration |
| AI Layer | Semantic Reasoning |

---

# 🧱 Engineering Principles

## Core Rules

- Async-first architecture
- Modular services
- Config-driven behavior
- Structured logging
- Retry-safe operations
- Isolated extraction components
- Minimal coupling between layers

---

## Important Rules

- Never rely solely on HTML parsing
- Prefer APIs over DOM extraction
- Never place extraction logic inside DRF views
- Never tightly couple crawler and parser
- All extraction failures must be recoverable
- Browser failures must trigger cleanup
- All modules must be independently testable

---

# ⚙️ Phase 1 — Browser Extraction Layer

## Responsibilities

- JavaScript rendering
- SPA hydration
- DOM rendering
- Infinite scrolling
- Lazy-load triggering
- Screenshot generation
- Session persistence
- Authenticated browsing

---

## Technologies

- Playwright
- Chromium

---

## Features

- Auto-scroll
- Wait strategies
- Cookie/session capture
- Login flows
- Browser context isolation
- Retry navigation

---

## Output

```json
{
  "html": "...",
  "screenshot": "...",
  "cookies": [],
  "local_storage": {},
  "session_storage": {}
}
```

---

# 🌐 Phase 2 — Network Intelligence Layer

## Responsibilities

- Capture requests
- Capture responses
- Detect APIs
- Detect GraphQL
- Extract JSON payloads
- Detect failed requests
- Filter noisy assets

---

## Captured Traffic

- XHR
- Fetch
- GraphQL
- JSON APIs
- WebSocket candidates
- Internal APIs

---

## Features

- Full request/response logging
- Payload extraction
- API discovery
- Header collection
- Retry tracking

---

## Output

```json
{
  "requests": [],
  "responses": [],
  "api_calls": [],
  "graphql_calls": [],
  "json_payloads": [],
  "failed_requests": []
}
```

---

# 🧾 Phase 3 — Raw HTML Parsing Layer

## Responsibilities

Extract raw content from rendered DOM.

---

## Technologies

- BeautifulSoup
- lxml

---

## Extracted Data

### Structural Content

- title
- headings
- paragraphs
- tables
- metadata

### Navigation

- internal links
- external links
- canonical URLs

### Assets

- images
- videos
- scripts
- stylesheets

### Forms

- forms
- inputs
- buttons
- actions

### Embedded Data

- JSON-LD
- OpenGraph
- Twitter Cards
- Next.js `__NEXT_DATA__`
- inline scripts

### Contact Data

- emails
- phone numbers

---

## Output

```json
{
  "links": [],
  "images": [],
  "forms": [],
  "metadata": {},
  "headings": {},
  "scripts": []
}
```

---

# 🧠 Phase 4 — Structured Parsing & Content Intelligence Layer

## Purpose

Transform raw extraction into meaningful structured intelligence.

Without this layer:

```text
raw web garbage
```

With this layer:

```text
usable structured intelligence
```

---

# Responsibilities

## Platform Detection

Detect:

- Shopify
- WordPress
- Wix
- Magento
- Next.js
- React
- Vue
- Webflow

---

## Page Type Detection

Classify pages as:

- product pages
- articles
- category pages
- documentation
- landing pages
- login pages
- pricing pages

---

## Semantic Extraction

Extract:

- product names
- prices
- SKUs
- authors
- publish dates
- breadcrumbs
- reviews
- ratings
- descriptions

---

## Structured Source Extraction

Prioritize:

- JSON-LD
- hydration state
- embedded configs
- API payloads

---

## Schema Normalization

Normalize inconsistent structures.

Example:

```json
{
  "product_title": "Laptop"
}
```

and:

```json
{
  "name": "Laptop"
}
```

become:

```json
{
  "title": "Laptop"
}
```

---

# 🔄 Phase 5 — Recursive Crawling Layer

## Responsibilities

- recursive crawling
- URL discovery
- queue management
- depth control
- deduplication
- crawl policies

---

## Features

- BFS crawling
- DFS crawling
- domain restriction
- robots.txt support (optional)
- crawl delay handling
- retry scheduling

---

## Crawl Rules

- stay within domain by default
- normalize URLs before deduplication
- avoid infinite loops
- configurable depth/page limits

---

# 🧹 Phase 6 — Data Normalization Layer

## Purpose

Ensure all extracted data conforms to consistent schemas.

---

## Responsibilities

- schema normalization
- malformed data cleanup
- duplicate removal
- validation
- field standardization
- canonicalization

---

## Example

Normalize:

```json
{
  "cost": "$100"
}
```

into:

```json
{
  "price": 100,
  "currency": "USD"
}
```

---

# 🗄️ Phase 7 — Storage Layer

## Purpose

Persistent storage and infrastructure backbone.

---

# Core Infrastructure

| Component | Purpose |
|---|---|
| PostgreSQL | Structured persistence |
| Redis | Queues/cache |
| Celery | Distributed tasks |
| MinIO/S3 | Asset storage |
| Elasticsearch/OpenSearch | Search/indexing |

---

# PostgreSQL Entities

## CrawlJob

```text
id
status
start_time
end_time
depth
total_pages
```

---

## Page

```text
id
url
title
html
text
status_code
crawl_job_id
```

---

## APIRequest

```text
id
url
method
status
headers
payload
response
```

---

## ExtractionResult

```text
id
page_id
normalized_data
classification
confidence
```

---

## Asset

```text
id
page_id
type
source_url
local_path
```

---

# Storage Responsibilities

- JSON export
- database persistence
- screenshot storage
- raw HTML storage
- asset management
- indexing

---

# ⚡ Browser Pooling

## Goal

Avoid launching browsers per request.

---

## Required Features

- persistent Chromium instances
- reusable browser contexts
- worker-safe allocation
- automatic cleanup
- browser health checks

---

# 🔌 Distributed Task Architecture

```text
Input URLs
      ↓
Redis Queue
      ↓
Celery Workers
      ↓
Browser Pool
      ↓
Extraction Pipeline
      ↓
PostgreSQL + MinIO
```

---

# 🤖 Phase 8 — AI Extraction Layer

## Goal

Use LLMs for semantic extraction when deterministic extraction fails.

---

# Recommended AI Hierarchy

```text
1. APIs
2. JSON-LD
3. Hydration state
4. HTML parsing
5. AI extraction fallback
```

AI should NEVER replace deterministic extraction.

---

# Recommended AI Stack

## Local Models (Preferred Initially)

Use:

- Ollama
- llama3
- qwen
- mistral

---

# AI Responsibilities

## Semantic Extraction

Extract:

- product summaries
- article summaries
- semantic entities
- structured knowledge

---

## Classification

Classify:

- product page
- blog
- docs
- pricing
- support page

---

## Messy HTML Parsing

Recover structured data from inconsistent layouts.

---

# 🌐 Phase 9 — DRF API Layer

## Purpose

Expose orchestration APIs.

DRF should orchestrate extraction — not perform extraction.

---

# Responsibilities

- authentication
- job submission
- crawl monitoring
- result retrieval
- permissions
- quotas
- webhooks

---

# Example Endpoints

```http
POST /extract/
POST /crawl/
GET  /jobs/
GET  /jobs/{id}/
GET  /results/{id}/
```

---

# ❌ DRF Must NOT Handle

- Playwright rendering
- parsing logic
- crawling logic
- browser lifecycle
- extraction intelligence

---

# 🐳 Infrastructure Strategy

## Containerized Environment

Use Docker Compose for all local infrastructure.

---

# Services

```yaml
services:
  postgres:
  redis:
  minio:
  celery_worker:
  celery_beat:
  scraper_api:
```

Later:

```yaml
elasticsearch:
kibana:
```

---

# 📊 Observability

## Logging

Structured logs for:

- requests
- responses
- retries
- failures
- crawl status
- browser lifecycle

---

## Metrics

Track:

- extraction success rate
- crawl speed
- API discovery rate
- average render time
- failure percentage

---

## Debug Artifacts

Store optionally:

- screenshots
- HTML snapshots
- network traces
- console logs

---

# 🧪 Testing Strategy

## Unit Tests

Test:

- parsers
- URL normalization
- deduplication
- extractors

---

## Integration Tests

Test:

- Playwright rendering
- network interception
- scrolling
- authentication

---

## End-to-End Tests

Validate against:

- static HTML sites
- React apps
- Next.js apps
- infinite-scroll sites

---

## Failure Tests

Validate:

- browser crashes
- timeouts
- malformed HTML
- blocked requests

---

# 🛡️ Anti-Bot Strategy

## Threats

- Cloudflare
- Akamai
- DataDome
- rate limiting
- fingerprinting

---

## Planned Mitigations

- rotating proxies
- stealth browser contexts
- randomized user agents
- session persistence
- viewport randomization
- request pacing

---

# ⚡ Performance Goals

## MVP Goals

- render under 10s
- extraction under 15s
- 100+ pages/hour

---

## Scaling Goals

- browser pooling
- async workers
- distributed queues
- parallel crawling

---

# 📁 Recommended Project Structure

```text
universal_scraper/
│
├── browser/
├── network/
├── parser/
├── intelligence/
├── normalization/
├── crawler/
├── storage/
├── ai/
├── api/
├── infrastructure/
│
├── output/
├── tests/
├── configs/
│
└── docker/
```

---

# 🚀 Execution Roadmap

```text
1. Browser Engine
2. Network Intelligence
3. Raw Parsing
4. Structured Parsing
5. Crawling Engine
6. Data Normalization
7. Storage Layer
8. DRF API Layer
9. Distributed Workers
10. AI Extraction
```

---

# 🧭 Long-Term Vision

This evolves into:

- Firecrawl-like extraction engine
- Apify-style crawler platform
- AI-ready data pipeline
- Distributed browser intelligence infrastructure

Eventually:

> A universal web-to-structured-data platform.

---

# 📌 Final Rules

- Prefer APIs over HTML
- Prefer structured data over raw parsing
- AI is fallback — not primary extraction
- Keep layers isolated
- Build infrastructure before DRF
- Never tightly couple extraction and orchestration
- Everything must be retry-safe
- Everything must be observable
- Everything must scale horizontally
````
