import asyncio
from urllib.parse import urlparse


def same_domain(url, base):
    return urlparse(url).netloc == urlparse(base).netloc


def normalize(url):
    p = urlparse(url)
    return p._replace(fragment="").geturl().rstrip("/")


class Crawler:

    def __init__(
        self,
        start_url,
        extractor_class,
        max_depth=2,
        max_pages=20,
        restrict_domain=True,
        concurrency=3,
        page_delay=2,
        credentials=None,
    ):
        self.start_url = start_url
        self.extractor_class = extractor_class
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.restrict_domain = restrict_domain
        self.page_delay = page_delay
        self.credentials = credentials
        self._sem = asyncio.Semaphore(concurrency)

        self.visited = set()
        self.results = []
        self._lock = asyncio.Lock()
        self._session = None  # shared auth session across pages

    # =========================================================
    # BFS CRAWL — level by level, each level runs in parallel
    # =========================================================

    async def crawl(self):

        current_level = [(self.start_url, 0)]
        self.visited.add(normalize(self.start_url))

        while current_level:

            # stop if page limit reached
            if len(self.results) >= self.max_pages:
                break

            # cap current level to remaining page budget
            remaining = self.max_pages - len(self.results)
            batch = current_level[:remaining]

            print(
                f"[CRAWLER] Processing {len(batch)} URLs "
                f"at depth {batch[0][1]}"
            )

            # run batch in parallel, semaphore limits concurrency
            tasks = [self._fetch(url, depth) for url, depth in batch]
            batch_results = await asyncio.gather(*tasks)

            next_level = []

            for data in batch_results:
                if not data:
                    continue

                async with self._lock:
                    self.results.append(data)

                depth = data.get("_depth", 0)

                if depth >= self.max_depth:
                    continue

                for link in data.get("links", []):
                    norm = normalize(link)

                    async with self._lock:
                        if norm in self.visited:
                            continue
                        if self.restrict_domain and not same_domain(
                            link, self.start_url
                        ):
                            continue
                        parsed = urlparse(link)
                        if parsed.scheme not in ("http", "https"):
                            continue
                        self.visited.add(norm)

                    next_level.append((link, depth + 1))

            current_level = next_level

        # strip internal _depth key from results
        for r in self.results:
            r.pop("_depth", None)

        print(f"[CRAWLER] Done. Pages crawled: {len(self.results)}")
        return self.results

    # =========================================================
    # FETCH ONE PAGE (semaphore-controlled)
    # =========================================================

    async def _fetch(self, url, depth):
        async with self._sem:
            print(f"[CRAWLER] depth={depth} {url}")
            if self.page_delay:
                await asyncio.sleep(self.page_delay)
            data = await self._extract(url)
            if data:
                data["_depth"] = depth
            return data

    async def _extract(self, url):
        try:
            extractor = self.extractor_class(
                url,
                credentials=self.credentials if not self._session else None,
                session=self._session,
            )
            data = await extractor.extract()
            # capture session from first successful login
            if not self._session and extractor.session:
                self._session = extractor.session
                print("[CRAWLER] Session captured, will reuse for remaining pages")
            return data
        except Exception as e:
            print(f"[CRAWLER] Failed {url}: {e}")
            return None
