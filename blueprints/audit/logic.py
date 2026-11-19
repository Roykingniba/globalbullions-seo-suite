import json
import urllib.robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import config, AI_CRAWLER_USER_AGENTS

SCHEMA_REQUIRED_FIELDS = {
    "Article": ["headline", "author", "datePublished"],
    "NewsArticle": ["headline", "author", "datePublished"],
    "BlogPosting": ["headline", "author", "datePublished"],
    "Product": ["name", "offers"],
    "FAQPage": ["mainEntity"],
    "HowTo": ["name", "step"],
    "Organization": ["name", "url"],
    "LocalBusiness": ["name", "address"],
    "BreadcrumbList": ["itemListElement"],
    "Recipe": ["name", "recipeIngredient", "recipeInstructions"],
}


def _headers():
    return {"User-Agent": config.user_agent}


def fetch_text(url, timeout=None):
    resp = requests.get(url, headers=_headers(), timeout=timeout or config.request_timeout)
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------------
# Robots.txt + sitemap validator
# ---------------------------------------------------------------------------
def audit_robots_and_sitemap(base_url):
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = urljoin(root, "/robots.txt")

    robots_txt = None
    sitemap_urls_from_robots = []
    try:
        resp = fetch_text(robots_url)
        robots_txt = resp.text
        for line in robots_txt.splitlines():
            if line.strip().lower().startswith("sitemap:"):
                sitemap_urls_from_robots.append(line.split(":", 1)[1].strip())
    except requests.exceptions.RequestException:
        pass

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    if robots_txt is not None:
        rp.parse(robots_txt.splitlines())
    else:
        rp.disallow_all = False

    sitemap_candidates = sitemap_urls_from_robots or [urljoin(root, "/sitemap.xml")]

    page_urls = []
    sitemap_fetch_errors = []
    for sm_url in sitemap_candidates:
        try:
            resp = fetch_text(sm_url)
            soup = BeautifulSoup(resp.content, "xml")
            # sitemap index: nested <sitemap><loc> entries, one level deep
            nested = [loc.get_text(strip=True) for loc in soup.find_all("sitemap")]
            if nested:
                for nested_url in nested:
                    try:
                        nresp = fetch_text(nested_url)
                        nsoup = BeautifulSoup(nresp.content, "xml")
                        page_urls.extend(loc.get_text(strip=True) for loc in nsoup.find_all("loc"))
                    except requests.exceptions.RequestException as e:
                        sitemap_fetch_errors.append(f"{nested_url}: {e}")
            else:
                page_urls.extend(loc.get_text(strip=True) for loc in soup.find_all("loc"))
        except requests.exceptions.RequestException as e:
            sitemap_fetch_errors.append(f"{sm_url}: {e}")

    blocked = []
    for u in page_urls:
        path = urlparse(u).path or "/"
        if robots_txt is not None and not rp.can_fetch("*", path):
            blocked.append(u)

    return {
        "robots_url": robots_url,
        "robots_found": robots_txt is not None,
        "sitemap_candidates": sitemap_candidates,
        "sitemap_fetch_errors": sitemap_fetch_errors,
        "total_urls_checked": len(page_urls),
        "truncated": False,
        "blocked_urls": blocked,
    }


# ---------------------------------------------------------------------------
# Schema / JSON-LD validator
# ---------------------------------------------------------------------------
def validate_schema(html):
    soup = BeautifulSoup(html, "lxml")
    blocks = soup.find_all("script", attrs={"type": "application/ld+json"})
    results = []
    for block in blocks:
        raw = block.string or block.get_text()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            results.append({"type": None, "valid_json": False, "missing_fields": [], "raw_error": True})
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            schema_type = item.get("@type")
            if isinstance(schema_type, list):
                schema_type = schema_type[0] if schema_type else None
            required = SCHEMA_REQUIRED_FIELDS.get(schema_type, [])
            missing = [f for f in required if f not in item]
            results.append({
                "type": schema_type or "(unknown type)",
                "valid_json": True,
                "missing_fields": missing,
                "raw_error": False,
            })
    return results


# ---------------------------------------------------------------------------
# Mixed content checker
# ---------------------------------------------------------------------------
def find_mixed_content(html, page_url):
    if not page_url.startswith("https://"):
        return {"applicable": False, "insecure_resources": []}

    soup = BeautifulSoup(html, "lxml")
    insecure = []
    for tag, attr in [("img", "src"), ("script", "src"), ("link", "href"), ("iframe", "src"), ("source", "src")]:
        for el in soup.find_all(tag):
            val = el.get(attr)
            if val and val.strip().lower().startswith("http://"):
                insecure.append({"tag": tag, "attr": attr, "url": val})
    return {"applicable": True, "insecure_resources": insecure}


# ---------------------------------------------------------------------------
# JS-dependency heuristic detector
# ---------------------------------------------------------------------------
def detect_js_dependency(html):
    soup = BeautifulSoup(html, "lxml")
    total_html_len = len(html)
    script_count = len(soup.find_all("script"))

    body = soup.body
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body_text = soup.get_text(separator=" ", strip=True) if soup else ""
    word_count = len(body_text.split())

    spa_roots = 0
    for sel in ["#root", "#app", "#__next", "#___gatsby"]:
        el = soup.select_one(sel)
        if el is not None and len(el.get_text(strip=True)) < 40:
            spa_roots += 1

    likely_js_dependent = (word_count < 50 and total_html_len > 2000) or spa_roots > 0

    return {
        "total_html_bytes": total_html_len,
        "script_tags": script_count,
        "visible_word_count": word_count,
        "empty_spa_roots_found": spa_roots,
        "likely_js_dependent": likely_js_dependent,
    }


# ---------------------------------------------------------------------------
# Broken link checker
# ---------------------------------------------------------------------------
def check_broken_links(base_url, html):
    soup = BeautifulSoup(html, "lxml")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        if href.startswith(("http://", "https://")) and href not in seen:
            seen.add(href)
            links.append(href)

    results = []
    for link in links:
        try:
            resp = requests.head(link, headers=_headers(), timeout=config.request_timeout, allow_redirects=True)
            if resp.status_code == 405:  # some servers reject HEAD
                resp = requests.get(link, headers=_headers(), timeout=config.request_timeout, allow_redirects=True, stream=True)
            broken = resp.status_code >= 400
            results.append({"url": link, "status": resp.status_code, "broken": broken, "error": None})
        except requests.exceptions.RequestException as e:
            results.append({"url": link, "status": None, "broken": True, "error": str(e)})

    return {"links_checked": len(links), "truncated": False, "results": results}


# ---------------------------------------------------------------------------
# AI crawler access checker
# ---------------------------------------------------------------------------
def check_ai_crawler_access(base_url):
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = urljoin(root, "/robots.txt")

    robots_txt = None
    try:
        resp = fetch_text(robots_url)
        robots_txt = resp.text
    except requests.exceptions.RequestException:
        pass

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    if robots_txt is not None:
        rp.parse(robots_txt.splitlines())

    results = []
    for agent, description in AI_CRAWLER_USER_AGENTS:
        if robots_txt is None:
            allowed = True  # no robots.txt = everything allowed by default
        else:
            allowed = rp.can_fetch(agent, "/")
        results.append({"agent": agent, "description": description, "allowed": allowed})

    return {
        "robots_url": robots_url,
        "robots_found": robots_txt is not None,
        "results": results,
        "allowed_count": sum(1 for r in results if r["allowed"]),
        "total_count": len(results),
    }
