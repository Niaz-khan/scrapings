import asyncio
import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from network import NetworkCollector
from normalizer import normalize
from auth import login, capture_session, restore_session


class UniversalExtractor:

    def __init__(self, url, credentials=None, session=None):
        """
        credentials: dict with keys login_url, username, password
        session: captured session dict from a previous login (reused across pages)
        """
        self.url = url
        self.credentials = credentials
        self.session = session
        self.network = NetworkCollector()

    # =========================================================
    # MAIN EXTRACTION
    # =========================================================

    async def extract(self):

        print("[INFO] Starting extraction")

        async with async_playwright() as p:

            print("[INFO] Launching browser")

            browser = await p.chromium.launch(
                headless=False
            )

            context = await browser.new_context(
                viewport={
                    "width": 1920,
                    "height": 1080
                }
            )

            page = await context.new_page()

            print("[INFO] Browser launched")

            # ============================================
            # EVENT LISTENERS
            # ============================================

            self.network.attach(page)

            # ============================================
            # AUTH: login or restore session
            # ============================================

            if self.credentials and not self.session:
                # first page — do full login and capture session
                success = await login(
                    page,
                    self.credentials["login_url"],
                    self.credentials["username"],
                    self.credentials["password"],
                )
                if success:
                    self.session = await capture_session(context, page)
                else:
                    print("[WARN] Login failed, proceeding anyway")

            elif self.session:
                # subsequent pages — restore captured session
                await restore_session(context, page, self.session)

            # ============================================
            # NAVIGATION
            # ============================================

            try:

                print(
                    f"[INFO] Navigating to: {self.url}"
                )

                await page.goto(
                    self.url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                print("[INFO] Page loaded")

            except Exception as e:

                print(f"[WARN] First attempt failed: {e}")
                print("[INFO] Retrying in 5s...")

                await asyncio.sleep(5)

                try:
                    await page.goto(
                        self.url,
                        wait_until="domcontentloaded",
                        timeout=60000
                    )
                    print("[INFO] Page loaded on retry")
                except Exception as e2:
                    print(f"[ERROR] Navigation failed: {e2}")
                    await browser.close()
                    return {}

            # ============================================
            # WAIT FOR JS
            # ============================================

            print(
                "[INFO] Waiting for JavaScript rendering"
            )

            await page.wait_for_timeout(5000)

            # ============================================
            # SCREENSHOT
            # ============================================

            print("[INFO] Capturing screenshot")

            await page.screenshot(
                path="debug.png",
                full_page=True
            )

            # ============================================
            # AUTO SCROLL
            # ============================================

            print("[INFO] Starting auto scroll")

            await self.auto_scroll(page)

            print("[INFO] Auto scroll complete")

            # ============================================
            # EXTRACT HTML
            # ============================================

            print("[INFO] Extracting HTML")

            html = await page.content()

            print(
                f"[INFO] HTML size: "
                f"{len(html)} characters"
            )

            # ============================================
            # SAVE RAW HTML
            # ============================================

            with open(
                "debug.html",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(html)

            print("[INFO] Raw HTML saved")

            # ============================================
            # PARSE HTML
            # ============================================

            print(
                "[INFO] Parsing HTML with BeautifulSoup"
            )

            soup = BeautifulSoup(
                html,
                "lxml"
            )

            # ============================================
            # EXTRACT DATA
            # ============================================

            print(
                "[INFO] Extracting structured data"
            )

            data = {
                "url": self.url,
                "title": self.extract_title(soup),
                "metadata": self.extract_metadata(soup),
                "headings": self.extract_headings(soup),
                "text": self.extract_text(soup),
                "links": self.extract_links(soup),
                "images": self.extract_images(soup),
                "videos": self.extract_videos(soup),
                "scripts": self.extract_scripts(soup),
                "inline_scripts": self.extract_inline_scripts(soup),
                "stylesheets": self.extract_stylesheets(soup),
                "forms": self.extract_forms(soup),
                "emails": self.extract_emails(html),
                "phones": self.extract_phones(html),
                "json_ld": self.extract_json_ld(soup),
                "nextjs_data": self.extract_nextjs_data(soup),
                "network": self.network.summary(),
                "html": html,
            }

            data["normalized"] = normalize(data)

            # ============================================
            # FINAL LOGS
            # ============================================

            print("[INFO] Extraction completed")

            print(
                f"[INFO] Links found: "
                f"{len(data['links'])}"
            )

            print(
                f"[INFO] Images found: "
                f"{len(data['images'])}"
            )

            net = data["network"]
            print(f"[INFO] APIs found: {len(net['api_endpoints'])}")
            print(f"[INFO] GraphQL found: {len(net['graphql_calls'])}")
            print(f"[INFO] Failed requests: {len(net['failed_requests'])}")

            print(
                f"[INFO] Forms found: "
                f"{len(data['forms'])}"
            )

            await browser.close()

            print("[INFO] Browser closed")

            return data

    # =========================================================
    # AUTO SCROLL
    # =========================================================

    async def auto_scroll(self, page):

        scroll_count = 0
        step = 300  # pixels per scroll step

        while True:

            current_pos = await page.evaluate("window.scrollY + window.innerHeight")
            total_height = await page.evaluate("document.body.scrollHeight")

            print(f"[SCROLL] {current_pos}/{total_height}")

            if current_pos >= total_height:
                print("[SCROLL] Reached page end")
                break

            scroll_count += 1
            print(f"[SCROLL] Iteration: {scroll_count}")

            await page.evaluate(f"window.scrollBy(0, {step})")

            await page.wait_for_timeout(3000)

    # =========================================================
    # EXTRACTION HELPERS
    # =========================================================

    def extract_title(self, soup):

        return (
            soup.title.text.strip()
            if soup.title
            else ""
        )

    def extract_metadata(self, soup):

        metadata = {}

        for meta in soup.find_all("meta"):

            name = (
                meta.get("name")
                or meta.get("property")
                or meta.get("charset")
            )

            content = meta.get("content")

            if name and content:

                metadata[name] = content

        return metadata

    def extract_headings(self, soup):

        headings = {}

        for i in range(1, 7):

            tag = f"h{i}"

            headings[tag] = [
                h.get_text(strip=True)
                for h in soup.find_all(tag)
            ]

        return headings

    def extract_text(self, soup):

        return soup.get_text(
            separator="\n",
            strip=True
        )

    def extract_links(self, soup):

        links = []

        for a in soup.find_all(
            "a",
            href=True
        ):

            links.append(
                urljoin(
                    self.url,
                    a["href"]
                )
            )

        return list(set(links))

    def extract_images(self, soup):

        images = []

        for img in soup.find_all("img"):

            src = (
                img.get("src")
                or img.get("data-src")
                or img.get("lazy-src")
            )

            if src:

                images.append(
                    urljoin(
                        self.url,
                        src
                    )
                )

        return list(set(images))

    def extract_videos(self, soup):

        videos = []

        for video in soup.find_all("video"):

            src = video.get("src")

            if src:

                videos.append(
                    urljoin(
                        self.url,
                        src
                    )
                )

        return list(set(videos))

    def extract_scripts(self, soup):

        scripts = []

        for script in soup.find_all("script"):

            src = script.get("src")

            if src:

                scripts.append(
                    urljoin(
                        self.url,
                        src
                    )
                )

        return list(set(scripts))

    def extract_inline_scripts(self, soup):

        scripts = []

        for script in soup.find_all("script"):

            if not script.get("src"):

                content = script.string

                if content:

                    scripts.append(content)

        return scripts

    def extract_stylesheets(self, soup):

        stylesheets = []

        for link in soup.find_all(
            "link",
            rel="stylesheet"
        ):

            href = link.get("href")

            if href:

                stylesheets.append(
                    urljoin(
                        self.url,
                        href
                    )
                )

        return list(set(stylesheets))

    def extract_forms(self, soup):

        forms = []

        for form in soup.find_all("form"):

            forms.append({
                "action": form.get("action"),
                "method": form.get("method"),
                "inputs": [
                    {
                        "name": inp.get("name"),
                        "type": inp.get("type"),
                    }
                    for inp in form.find_all("input")
                ]
            })

        return forms

    def extract_emails(self, html):

        return list(set(
            re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+",
                html
            )
        ))

    def extract_phones(self, html):

        return list(set(
            re.findall(
                r'(?<![a-zA-Z0-9"\-])\+?1?[\s\-.]?\(?[2-9]\d{2}\)?[\s\-.]?[2-9]\d{2}[\s\-.]\d{4}(?![a-zA-Z0-9])',
                html
            )
        ))

    def extract_json_ld(self, soup):

        data = []

        scripts = soup.find_all(
            "script",
            type="application/ld+json"
        )

        for script in scripts:

            try:

                data.append(
                    json.loads(script.string)
                )

            except Exception:
                pass

        return data

    def extract_nextjs_data(self, soup):

        script = soup.find(
            "script",
            id="__NEXT_DATA__"
        )

        if not script:

            return None

        try:

            return json.loads(script.string)

        except Exception:

            return None


# =============================================================
# MAIN
# =============================================================

from crawler import Crawler


async def main():

    url = input("Enter URL: ")
    mode = input("Mode [extract/crawl] (default: extract): ").strip() or "extract"

    # optional auth
    needs_auth = input("Requires login? [y/N]: ").strip().lower() == "y"
    credentials = None
    if needs_auth:
        login_url = input("Login page URL (leave blank to use same URL): ").strip() or url
        username = input("Username/Email: ").strip()
        import getpass
        password = getpass.getpass("Password: ")
        credentials = {
            "login_url": login_url,
            "username": username,
            "password": password,
        }

    if mode == "crawl":

        max_depth = int(input("Max depth (default 2): ").strip() or 2)
        max_pages = int(input("Max pages (default 20): ").strip() or 20)
        concurrency = int(input("Concurrency (default 3): ").strip() or 3)

        crawler = Crawler(
            url,
            UniversalExtractor,
            max_depth=max_depth,
            max_pages=max_pages,
            concurrency=concurrency,
            credentials=credentials,
        )

        results = await crawler.crawl()

        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        print(f"[INFO] Crawl saved {len(results)} pages to output.json")

    else:

        extractor = UniversalExtractor(url, credentials=credentials)
        data = await extractor.extract()

        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("[INFO] Extraction saved to output.json")


if __name__ == "__main__":

    asyncio.run(main())