import json


class NetworkCollector:

    def __init__(self):
        self.requests = []
        self.responses = []
        self.api_calls = []
        self.failed_requests = []
        self.graphql_calls = []
        self._seen_urls = {}  # url -> list of statuses

    # =========================================================
    # CLASSIFICATION
    # =========================================================

    def _is_api(self, url, content_type=""):
        return (
            "application/json" in content_type
            or "/api/" in url
            or "/graphql" in url.lower()
            or "graphql" in url.lower()
        )

    def _is_graphql(self, url, body=None):
        if "/graphql" in url.lower():
            return True
        if body and isinstance(body, dict) and "query" in body:
            return True
        return False

    # =========================================================
    # HANDLERS
    # =========================================================

    def on_request(self, request):
        important = {"document", "xhr", "fetch", "script"}
        if request.resource_type not in important:
            return

        print(
            f"[REQUEST] {request.method} "
            f"{request.resource_type.upper()} {request.url}"
        )

        self.requests.append({
            "method": request.method,
            "url": request.url,
            "resource_type": request.resource_type,
            "headers": dict(request.headers),
            "post_data": request.post_data,
        })

    async def on_response(self, response):
        important = {"document", "xhr", "fetch", "script"}
        if response.request.resource_type not in important:
            return

        print(
            f"[RESPONSE] {response.status} "
            f"{response.request.resource_type.upper()} {response.url}"
        )

        content_type = response.headers.get("content-type", "")
        url = response.url

        # track all statuses per url
        self._seen_urls.setdefault(url, []).append(response.status)

        # track failed requests (deduped in summary())
        if response.status >= 400:
            self.failed_requests.append({
                "url": url,
                "status": response.status,
                "method": response.request.method,
            })

        if not self._is_api(url, content_type):
            return

        print(f"[API DETECTED] {response.status} {url}")

        body_text = ""
        body_json = None

        try:
            body_text = await response.text()
            body_json = json.loads(body_text)
        except Exception:
            pass

        entry = {
            "url": url,
            "status": response.status,
            "method": response.request.method,
            "content_type": content_type,
            "preview": body_text[:500],
            "body": body_json,
        }

        if self._is_graphql(url, body_json):
            print(f"[GRAPHQL] {url}")
            self.graphql_calls.append(entry)
        else:
            self.api_calls.append(entry)

        self.responses.append(entry)

    # =========================================================
    # ATTACH TO PAGE
    # =========================================================

    def attach(self, page):
        page.on("request", self.on_request)
        page.on("response", self.on_response)

    # =========================================================
    # SUMMARY
    # =========================================================

    def summary(self):
        # filter out 403s for URLs that eventually got a 200 (e.g. Cloudflare challenge)
        resolved = {url for url, statuses in self._seen_urls.items() if 200 in statuses}
        real_failures = [
            f for f in self.failed_requests
            if not (f["status"] == 403 and f["url"] in resolved)
        ]
        return {
            "api_endpoints": self.api_calls,
            "graphql_calls": self.graphql_calls,
            "failed_requests": real_failures,
        }
