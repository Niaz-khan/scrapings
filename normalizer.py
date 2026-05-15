"""
Normalizes raw extracted page data into a clean, consistent schema.

Output schema:
{
    "url": str,
    "title": str,
    "description": str,
    "keywords": [str],
    "language": str,
    "schema_type": str,          # from JSON-LD @type
    "structured_data": {...},    # merged from JSON-LD + Next.js props
    "api_data": [{...}],         # cleaned API payloads (noise filtered)
    "contact": {
        "emails": [str],
        "phones": [str],
        "address": str | None,
    },
    "content": {
        "headings": {str: [str]},
        "text": str,
        "links": [str],
        "images": [str],
        "forms": [...],
    }
}
"""
from urllib.parse import urlparse

# Domains considered analytics/noise — their API calls are excluded
_NOISE_DOMAINS = {
    "amplitude.com",
    "stripe.com",
    "stripe.network",
    "google.com",
    "facebook.com",
    "doubleclick.net",
    "analytics",
    "tosspayments.com",
    "botpress.cloud",
    "bpcontent.cloud",
    "googlesyndication.com",
}

# sub-paths that are widget-internal noise regardless of domain
_NOISE_PATHS = {
    "/user/hi", "/user/m", "/bug/client_log",
    "/elasticsearch/mget", "/elasticsearch/msearch",
}


def _is_noise_api(url):
    parsed = urlparse(url)
    if any(d in parsed.netloc for d in _NOISE_DOMAINS):
        return True
    if any(parsed.path.startswith(p) for p in _NOISE_PATHS):
        return True
    return False


# =========================================================
# JSON-LD
# =========================================================

def _normalize_json_ld(json_ld_list):
    """Merge all JSON-LD blocks into a flat dict."""
    merged = {}
    schema_type = None

    for block in (json_ld_list or []):
        if not isinstance(block, dict):
            continue
        if not schema_type and "@type" in block:
            schema_type = block["@type"]
        for k, v in block.items():
            if k.startswith("@"):
                continue
            merged[k] = v

    return merged, schema_type


# =========================================================
# NEXT.JS
# =========================================================

def _normalize_nextjs(nextjs_data):
    """Extract page props from __NEXT_DATA__."""
    if not nextjs_data or not isinstance(nextjs_data, dict):
        return {}

    props = nextjs_data.get("props", {})
    page_props = props.get("pageProps", props)
    return page_props if isinstance(page_props, dict) else {}


# =========================================================
# API PAYLOADS
# =========================================================

def _normalize_api_calls(api_endpoints):
    """Filter noise, deduplicate by URL, return clean list of {url, data}."""
    seen = set()
    result = []
    for entry in (api_endpoints or []):
        url = entry.get("url", "")
        if _is_noise_api(url):
            continue
        if url in seen:
            continue
        body = entry.get("body")
        if body is None:
            continue
        seen.add(url)
        result.append({
            "url": url,
            "status": entry.get("status"),
            "data": body,
        })
    return result


# =========================================================
# MAIN NORMALIZER
# =========================================================

def normalize(raw):
    """
    Takes raw extractor output dict, returns normalized schema dict.
    """
    json_ld = raw.get("json_ld") or []
    structured, schema_type = _normalize_json_ld(json_ld)
    nextjs_props = _normalize_nextjs(raw.get("nextjs_data"))

    # merge nextjs into structured (json_ld takes priority)
    merged_structured = {**nextjs_props, **structured}

    # description: prefer meta, fallback to json_ld
    description = (
        raw.get("metadata", {}).get("description")
        or structured.get("description")
        or ""
    )

    # keywords: prefer json_ld, fallback to meta
    keywords = structured.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",")]
    meta_keywords = raw.get("metadata", {}).get("keywords", "")
    if not keywords and meta_keywords:
        keywords = [k.strip() for k in meta_keywords.split(",")]

    language = (
        structured.get("inLanguage")
        or raw.get("metadata", {}).get("language")
        or ""
    )

    api_data = _normalize_api_calls(
        raw.get("network", {}).get("api_endpoints", [])
    )

    return {
        "url": raw.get("url", ""),
        "title": raw.get("title", ""),
        "description": description,
        "keywords": keywords,
        "language": language,
        "schema_type": schema_type,
        "structured_data": merged_structured,
        "api_data": api_data,
        "contact": {
            "emails": raw.get("emails", []),
            "phones": raw.get("phones", []),
            "address": structured.get("address"),
        },
        "content": {
            "headings": raw.get("headings", {}),
            "text": raw.get("text", ""),
            "links": raw.get("links", []),
            "images": raw.get("images", []),
            "forms": raw.get("forms", []),
        },
    }
