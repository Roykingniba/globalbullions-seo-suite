import re
from collections import Counter

import requests
import textstat
from bs4 import BeautifulSoup

from config import config

STOPWORDS = set("""
a an the and or but if is are was were be been being to of in on at for with
as by from that this these those it its it's your you we our they he she
his her them i my me not no so than then too very can will just also
""".split())

WORD_RE = re.compile(r"[a-zA-Z']+")


def soup_from_html(html):
    return BeautifulSoup(html, "lxml")


def get_title_and_meta(soup):
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta = soup.find("meta", attrs={"name": "description"})
    description = meta["content"].strip() if meta and meta.get("content") else ""
    return title, description


def extract_visible_text(soup):
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def keyword_density_report(text, target_keyword=""):
    words = [w.lower() for w in WORD_RE.findall(text)]
    total = len(words)
    meaningful = [w for w in words if w not in STOPWORDS and len(w) > 2]

    unigrams = Counter(meaningful).most_common(15)

    bigrams = Counter(
        f"{a} {b}" for a, b in zip(words, words[1:])
        if a not in STOPWORDS and b not in STOPWORDS
    ).most_common(10)

    trigrams = Counter(
        f"{a} {b} {c}" for a, b, c in zip(words, words[1:], words[2:])
        if a not in STOPWORDS and c not in STOPWORDS
    ).most_common(10)

    target_density = None
    if target_keyword.strip():
        kw = target_keyword.strip().lower()
        kw_words = kw.split()
        if len(kw_words) == 1:
            count = words.count(kw)
        else:
            joined = " ".join(words)
            count = joined.count(kw)
        target_density = {
            "keyword": target_keyword.strip(),
            "count": count,
            "density_pct": round((count / total) * 100, 2) if total else 0.0,
        }

    readability = {}
    try:
        readability = {
            "flesch_reading_ease": round(textstat.flesch_reading_ease(text), 1),
            "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(text), 1),
        }
    except Exception:
        pass

    return {
        "word_count": total,
        "unigrams": unigrams,
        "bigrams": bigrams,
        "trigrams": trigrams,
        "target_density": target_density,
        "readability": readability,
    }


SECURITY_HEADERS = [
    ("Strict-Transport-Security", "Forces browsers to use HTTPS for future visits."),
    ("Content-Security-Policy", "Restricts what sources scripts/styles/frames can load from."),
    ("X-Content-Type-Options", "Should be 'nosniff' — stops MIME-type sniffing attacks."),
    ("X-Frame-Options", "Controls whether the page can be embedded in an iframe (clickjacking protection)."),
    ("Referrer-Policy", "Controls how much referrer info is sent to other sites."),
    ("Permissions-Policy", "Restricts access to browser features (camera, geolocation, etc.)."),
]


def check_security_headers(headers):
    results = []
    for name, desc in SECURITY_HEADERS:
        value = headers.get(name)
        results.append({"name": name, "description": desc, "present": bool(value), "value": value})
    return results


def parse_canonical_hreflang(soup, page_url):
    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag["href"].strip() if canonical_tag and canonical_tag.get("href") else None

    hreflang_tags = soup.find_all("link", rel="alternate")
    hreflang = [
        {"hreflang": t.get("hreflang"), "href": t.get("href")}
        for t in hreflang_tags if t.get("hreflang")
    ]

    issues = []
    if not canonical:
        issues.append("No canonical tag found.")
    elif canonical.rstrip("/") != page_url.rstrip("/"):
        issues.append(f"Canonical points to a different URL than the one fetched ({canonical}).")

    if hreflang:
        has_self = any(h["href"] and h["href"].rstrip("/") == page_url.rstrip("/") for h in hreflang)
        has_x_default = any(h["hreflang"] == "x-default" for h in hreflang)
        if not has_self:
            issues.append("No hreflang tag self-references this exact page — search engines expect a self-referencing entry.")
        if not has_x_default:
            issues.append("No 'x-default' hreflang entry found (recommended for a fallback locale).")

    return {"canonical": canonical, "hreflang": hreflang, "issues": issues}


def follow_redirect_chain(url, timeout=None, max_hops=10):
    """Manually follow redirects one hop at a time so we can report the
    full chain and detect loops, rather than just the final response."""
    timeout = timeout or config.request_timeout
    headers = {"User-Agent": config.user_agent}
    chain = []
    seen = set()
    current = url

    for _ in range(max_hops):
        if current in seen:
            chain.append({"url": current, "status": None, "error": "Redirect loop detected."})
            return chain, "loop"
        seen.add(current)
        try:
            resp = requests.get(current, headers=headers, timeout=timeout, allow_redirects=False)
        except requests.exceptions.RequestException as e:
            chain.append({"url": current, "status": None, "error": str(e)})
            return chain, "error"

        location = resp.headers.get("Location")
        chain.append({"url": current, "status": resp.status_code, "error": None, "location": location})

        if resp.is_redirect and location:
            from urllib.parse import urljoin
            current = urljoin(current, location)
            continue
        return chain, "ok"

    chain.append({"url": current, "status": None, "error": "Too many redirects (stopped after 10 hops)."})
    return chain, "too_many"


def rdap_lookup(domain):
    """Query the free RDAP.org router (no API key needed) for domain
    registration data — a modern, JSON replacement for raw WHOIS."""
    resp = requests.get(f"https://rdap.org/domain/{domain}", timeout=config.request_timeout,
                         headers={"User-Agent": config.user_agent})
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()

    events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
    nameservers = [ns.get("ldhName") for ns in data.get("nameservers", []) if ns.get("ldhName")]

    return {
        "domain": data.get("ldhName", domain),
        "registered": events.get("registration"),
        "last_changed": events.get("last changed"),
        "expires": events.get("expiration"),
        "status": data.get("status", []),
        "nameservers": nameservers,
    }
