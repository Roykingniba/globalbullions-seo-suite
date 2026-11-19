from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import config
from blueprints.audit.logic import (
    audit_robots_and_sitemap, check_ai_crawler_access, validate_schema, fetch_text,
)

def generate_llms_txt(base_url, site_name=None):
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"

    sitemap_info = audit_robots_and_sitemap(base_url)
    # Reuse the sitemap-discovery step rather than re-implementing it; we don't
    # care about robots blocking here, just the URL list.
    page_urls = []
    for sm_url in sitemap_info["sitemap_candidates"]:
        try:
            resp = fetch_text(sm_url)
            soup = BeautifulSoup(resp.content, "xml")
            nested = [loc.get_text(strip=True) for loc in soup.find_all("sitemap")]
            if nested:
                for nested_url in nested:
                    try:
                        nresp = fetch_text(nested_url)
                        nsoup = BeautifulSoup(nresp.content, "xml")
                        page_urls.extend(loc.get_text(strip=True) for loc in nsoup.find_all("loc"))
                    except requests.exceptions.RequestException:
                        pass
            else:
                page_urls.extend(loc.get_text(strip=True) for loc in soup.find_all("loc"))
        except requests.exceptions.RequestException:
            pass

    if not page_urls:
        page_urls = [root]

    pages = []
    for url in page_urls:
        try:
            resp = fetch_text(url)
            soup = BeautifulSoup(resp.text, "lxml")
            title = soup.title.string.strip() if soup.title and soup.title.string else url
            meta = soup.find("meta", attrs={"name": "description"})
            description = meta["content"].strip() if meta and meta.get("content") else ""
            pages.append({"url": url, "title": title, "description": description})
        except requests.exceptions.RequestException:
            continue

    name = site_name or parsed.netloc
    lines = [f"# {name}", ""]
    if pages and pages[0]["description"]:
        lines.append(f"> {pages[0]['description']}")
        lines.append("")
    lines.append("## Pages")
    for p in pages:
        desc = f": {p['description']}" if p["description"] else ""
        lines.append(f"- [{p['title']}]({p['url']}){desc}")

    return {
        "content": "\n".join(lines),
        "pages_included": len(pages),
        "truncated": False,
    }


def score_geo_readiness(base_url, html):
    soup = BeautifulSoup(html, "lxml")

    ai_access = check_ai_crawler_access(base_url)
    schema_results = validate_schema(html)

    h1 = soup.find("h1")
    h1_text = h1.get_text(strip=True) if h1 else ""

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body_text = soup.get_text(separator=" ", strip=True) if soup.body else ""
    first_150_words = " ".join(body_text.split()[:150]).lower()

    h1_words = [w for w in h1_text.lower().split() if len(w) > 3]
    overlap = sum(1 for w in h1_words if w in first_150_words)
    answer_first = bool(h1_words) and (overlap / len(h1_words)) >= 0.4

    has_schema = any(not r["raw_error"] for r in schema_results) if schema_results else False
    schema_complete = all(not r["missing_fields"] for r in schema_results if not r["raw_error"]) if schema_results else False

    ai_access_pct = (ai_access["allowed_count"] / ai_access["total_count"]) if ai_access["total_count"] else 0

    score = 0
    score += 40 * ai_access_pct
    score += 25 if has_schema else 0
    score += 10 if (has_schema and schema_complete) else 0
    score += 25 if answer_first else 0

    return {
        "score": round(score),
        "ai_access_pct": round(ai_access_pct * 100),
        "ai_access_detail": ai_access,
        "has_schema": has_schema,
        "schema_complete": schema_complete,
        "schema_count": len(schema_results),
        "answer_first": answer_first,
        "h1_found": bool(h1_text),
    }
