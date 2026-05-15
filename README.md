# scrapings

Universal web extractor + simple async crawler built on **Playwright** and **BeautifulSoup**.

## What’s here

- `my_scrapy_playwright.py` — interactive runner:
  - **extract**: extract one page to `output.json`
  - **crawl**: BFS crawl + extract multiple pages to `output.json`
- `crawler.py` — async BFS crawler (concurrency-limited, optional same-domain restriction)
- `auth.py` — optional “human-like” login + capture/restore session (cookies + storage)
- `network.py` — Playwright network collector (API + GraphQL detection)
- `normalizer.py` — output normalization helpers

## Setup

1) Create/activate a virtualenv (optional, recommended).
2) Install deps:

```bash
pip install -r requirements.txt
```

3) Install Playwright browsers:

```bash
python -m playwright install chromium
```

## Run

```bash
python my_scrapy_playwright.py
```

You’ll be prompted for:
- URL
- Mode: `extract` (default) or `crawl`
- Optional login (y/N). If enabled, you’ll enter `login_url`, `username`, and `password`.

## Outputs

- `output.json` — extracted data (single page) or list of extracted pages (crawl mode)
- `debug.html` — raw HTML saved from Playwright page content
- `debug.png` — full-page screenshot

## Notes

- Playwright is currently launched with `headless=False` in `my_scrapy_playwright.py`.
- Crawl settings (`max_depth`, `max_pages`, `concurrency`) are prompted in `crawl` mode.
