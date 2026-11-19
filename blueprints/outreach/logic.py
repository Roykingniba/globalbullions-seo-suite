"""Outreach tools.

The email finder scans one domain per call (scan_domain) so the browser can
drive a list of any length one domain at a time and show real progress. No
single web request ever has to cover the whole list, which is what used to
make long lists hang and then time out on shared hosting.

Newer outreach tools (broken-link finder, social profile finder, pitch
personalizer) live at the bottom of this file.
"""

import re
import time
from html import unescape
from urllib.parse import urljoin, urlparse, urldefrag, unquote

import requests
from bs4 import BeautifulSoup

from config import config

DEFAULT_KEYWORDS = [
    "contact", "support", "inquiry", "feedback", "reach us",
    "connect", "customer service", "contact us", "advertise",
    "partnership", "collaborate", "email", "message", "call",
    "sales", "business inquiries", "request", "join us",
    "write for us", "guest post", "contribute", "submit an article",
    "contributor guidelines", "submission guidelines", "blog for us",
    "become a contributor", "share your story", "guest authors",
    "write with us", "articles", "editorial", "publication",
    "content contribution", "collaborative writing", "freelance writing",
    "content submission", "co-author", "guest contributor",
    "editorial guidelines", "about", "about us",
]

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}\b")
OBFUSCATED_EMAIL_PATTERN = re.compile(
    r"\b([A-Za-z0-9._%+-]+)\s*[\[\(\{]?\s*(?:at|AT)\s*[\]\)\}]?\s*"
    r"([A-Za-z0-9-]+(?:\s*[\[\(\{]?\s*(?:dot|DOT)\s*[\]\)\}]?\s*[A-Za-z0-9-]+)+)\b"
)

# Things that match the email regex but are never real inboxes.
_ASSET_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico",
              ".css", ".js", ".mp4", ".webm", ".pdf", ".avif")
_JUNK_DOMAINS = {
    "example.com", "example.org", "example.net", "domain.com", "email.com",
    "yourdomain.com", "yoursite.com", "company.com", "sentry.io",
    "sentry-next.wixpress.com", "sentry.wixpress.com", "wixpress.com",
    "ingest.sentry.io", "mysite.com", "website.com", "test.com",
}
_JUNK_LOCAL = {"name", "email", "user", "username", "your", "youremail", "yourname", "john.doe", "johndoe"}

# Pages that are almost never contact pages even when a keyword matches the URL.
_SKIP_EXT = _ASSET_EXT + (".zip", ".rar", ".xml", ".json", ".txt", ".doc", ".docx", ".xls", ".xlsx")

MAX_PAGES_PER_DOMAIN = 8     # candidate contact pages fetched per domain
DOMAIN_TIME_BUDGET = 40      # seconds; keeps each scan request well under host timeouts


def _clean_email(raw):
    e = unquote(raw).strip().strip(".,;:'\"()<>[]").lower()
    if e.startswith("mailto:"):
        e = e[7:]
    e = e.split("?")[0]
    if "@" not in e or e.count("@") != 1:
        return None
    local, dom = e.split("@")
    if not local or not dom or "." not in dom:
        return None
    if e.endswith(_ASSET_EXT) or dom in _JUNK_DOMAINS or local in _JUNK_LOCAL:
        return None
    if re.fullmatch(r"[0-9a-f]{24,}", local):   # error-tracker keys, not people
        return None
    if re.search(r"@\d+x\.", e):                  # retina image names like logo@2x.png
        return None
    if not EMAIL_PATTERN.fullmatch(e):
        return None
    return e


def _decode_cfemail(hexstr):
    """Cloudflare 'email protection' hides addresses in a data-cfemail hex blob."""
    try:
        key = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ key) for i in range(2, len(hexstr), 2))
    except ValueError:
        return ""


def extract_emails(html_text, soup=None):
    """Return a sorted list of unique, cleaned email addresses found in a page."""
    found = set()
    text = unescape(html_text)
    for m in EMAIL_PATTERN.findall(text):
        found.add(m)
    for name, rest in OBFUSCATED_EMAIL_PATTERN.findall(text):
        dom = re.sub(r"\s*[\[\(\{]?\s*(?:dot|DOT)\s*[\]\)\}]?\s*", ".", rest)
        found.add(f"{name}@{dom}")
    if soup is not None:
        for a in soup.select('a[href^="mailto:"]'):
            found.add(a["href"])
        for el in soup.select("[data-cfemail]"):
            found.add(_decode_cfemail(el.get("data-cfemail", "")))
        for a in soup.select('a[href*="/cdn-cgi/l/email-protection#"]'):
            found.add(_decode_cfemail(a["href"].split("#", 1)[1]))
    cleaned = {c for c in (_clean_email(x) for x in found) if c}
    return sorted(cleaned)


def _normalise_domain(raw):
    raw = raw.strip()
    if not raw:
        return None, None
    url = raw if raw.startswith(("http://", "https://")) else f"https://{raw}"
    parsed = urlparse(url)
    if not parsed.netloc:
        return None, None
    host = parsed.netloc.lower()
    return f"{parsed.scheme}://{host}", host


def _same_site(url, host):
    h = urlparse(url).netloc.lower()
    bare = host[4:] if host.startswith("www.") else host
    return h == bare or h.endswith("." + bare)


def _new_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def _get(session, url, timeout):
    r = session.get(url, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    ctype = r.headers.get("Content-Type", "")
    if ctype and "html" not in ctype and "xml" not in ctype and "text" not in ctype:
        raise requests.exceptions.RequestException(f"Not an HTML page ({ctype.split(';')[0]})")
    return r


def _short_error(exc):
    if isinstance(exc, requests.exceptions.Timeout):
        return "Timed out"
    if isinstance(exc, requests.exceptions.SSLError):
        return "SSL certificate error"
    if isinstance(exc, requests.exceptions.ConnectionError):
        return "Could not connect (site down or domain does not resolve)"
    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        return f"HTTP {exc.response.status_code}"
    msg = str(exc)
    return msg[:160] if msg else exc.__class__.__name__


def _match_keyword(href, text, keywords):
    h = href.lower()
    t = text.lower()
    for kw in keywords:
        slug = kw.replace(" ", "-")
        if kw in t or kw in h or slug in h or kw.replace(" ", "") in h:
            return kw
    return None


def scan_domain(raw_domain, keywords=None, timeout=10, max_pages=MAX_PAGES_PER_DOMAIN,
                budget=DOMAIN_TIME_BUDGET):
    """Scan a single domain for contact pages and email addresses.

    Returns a JSON-serialisable dict:
      domain, status ("ok" | "error"), emails, pages [{url, keyword, emails}],
      errors [{url, error}], seconds
    """
    started = time.monotonic()
    keywords = [k.strip().lower() for k in (keywords or DEFAULT_KEYWORDS) if k.strip()]
    base_url, host = _normalise_domain(raw_domain)
    out = {"domain": raw_domain.strip(), "status": "ok", "emails": [], "pages": [], "errors": [], "seconds": 0}
    if not base_url:
        out.update(status="error", errors=[{"url": raw_domain, "error": "Not a valid domain"}])
        return out

    session = _new_session()
    all_emails = set()

    def time_left():
        return budget - (time.monotonic() - started)

    # 1. Homepage (fall back to http:// if https fails to connect)
    home = None
    for attempt in (base_url, base_url.replace("https://", "http://", 1)):
        try:
            home = _get(session, attempt, timeout)
            break
        except requests.exceptions.RequestException as e:
            err = _short_error(e)
            if attempt.startswith("http://") or not isinstance(
                    e, (requests.exceptions.SSLError, requests.exceptions.ConnectionError)):
                out["errors"].append({"url": attempt, "error": err})
                break
    if home is None:
        out["status"] = "error"
        out["seconds"] = round(time.monotonic() - started, 1)
        return out

    home_url = home.url
    host = urlparse(home_url).netloc.lower() or host
    soup = BeautifulSoup(home.text, "html.parser")
    home_emails = extract_emails(home.text, soup)
    if home_emails:
        all_emails.update(home_emails)
        out["pages"].append({"url": home_url, "keyword": "homepage", "emails": home_emails})

    # 2. Candidate contact pages from the homepage links (URL or link text match)
    candidates, seen = [], {urldefrag(home_url)[0].rstrip("/")}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        url = urldefrag(urljoin(home_url, href))[0]
        if not url.startswith(("http://", "https://")) or not _same_site(url, host):
            continue
        if urlparse(url).path.lower().endswith(_SKIP_EXT):
            continue
        key = url.rstrip("/")
        if key in seen:
            continue
        kw = _match_keyword(href, a.get_text(" ", strip=True), keywords)
        if kw:
            seen.add(key)
            candidates.append((keywords.index(kw), url, kw))

    # 3. Nothing linked from the homepage: look in the sitemap
    if not candidates and time_left() > timeout:
        sitemap_url = urljoin(home_url, "/sitemap.xml")
        try:
            sm = session.get(sitemap_url, timeout=timeout)
            sm.raise_for_status()
            sm_soup = BeautifulSoup(sm.content, "xml")
            locs = [l.get_text(strip=True) for l in sm_soup.find_all("loc")]
            # A sitemap index points at other sitemaps; peek into the first page one.
            if locs and all(l.lower().endswith(".xml") for l in locs[:5]):
                page_maps = [l for l in locs if "page" in l.lower()] or locs[:1]
                sub = session.get(page_maps[0], timeout=timeout)
                sub.raise_for_status()
                locs = [l.get_text(strip=True) for l in BeautifulSoup(sub.content, "xml").find_all("loc")]
            for loc in locs:
                kw = _match_keyword(loc, "", keywords)
                if kw and loc.rstrip("/") not in seen and _same_site(loc, host):
                    seen.add(loc.rstrip("/"))
                    candidates.append((keywords.index(kw), loc, kw))
        except requests.exceptions.RequestException as e:
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code != 404:
                out["errors"].append({"url": sitemap_url, "error": _short_error(e)})

    # Earlier keywords in the list are the more contact-like ones, so try those first.
    candidates.sort(key=lambda c: c[0])

    # 4. Fetch each candidate once
    for _, url, kw in candidates[:max_pages]:
        if time_left() < 2:
            out["errors"].append({"url": url, "error": "Skipped: time limit for this domain reached"})
            break
        try:
            r = _get(session, url, min(timeout, max(2, time_left())))
            emails = extract_emails(r.text, BeautifulSoup(r.text, "html.parser"))
            all_emails.update(emails)
            out["pages"].append({"url": r.url, "keyword": kw, "emails": emails})
        except requests.exceptions.RequestException as e:
            out["errors"].append({"url": url, "error": _short_error(e)})

    out["emails"] = sorted(all_emails)
    out["seconds"] = round(time.monotonic() - started, 1)
    return out


def process_domains(domains, keywords, timeout=10, errors=None):
    """Scan several domains in one go. Used only by the no-JavaScript fallback."""
    for d in domains:
        res = scan_domain(d, keywords, timeout=timeout)
        if errors is not None:
            errors.extend((res["domain"], e["url"], e["error"]) for e in res["errors"])
        yield res


# ---------------------------------------------------------------------------
# Broken-link outreach finder — bulk version of the technical broken-link
# checker, framed around finding link-building opportunities across many
# resource/"further reading" pages at once.
# ---------------------------------------------------------------------------
def find_broken_link_opportunities(page_urls, timeout=15):
    session = requests.Session()
    session.headers.update({"User-Agent": config.user_agent})
    results = []

    for page_url in page_urls:
        base_url = page_url if page_url.startswith(("http://", "https://")) else f"https://{page_url}"
        try:
            resp = session.get(base_url, timeout=timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
        except requests.exceptions.RequestException as e:
            results.append({"page": base_url, "broken_links": [], "error": str(e)})
            continue

        links, seen = [], set()
        for a in soup.find_all("a", href=True):
            href = urljoin(base_url, a["href"])
            if href.startswith(("http://", "https://")) and href not in seen:
                seen.add(href)
                links.append({"url": href, "anchor_text": a.get_text(strip=True)[:80]})

        broken = []
        for link in links:
            try:
                r = session.head(link["url"], timeout=timeout, allow_redirects=True)
                if r.status_code == 405:
                    r = session.get(link["url"], timeout=timeout, allow_redirects=True, stream=True)
                if r.status_code >= 400:
                    broken.append({**link, "status": r.status_code})
            except requests.exceptions.RequestException as e:
                broken.append({**link, "status": None, "error": str(e)})

        results.append({"page": base_url, "broken_links": broken, "error": None})

    return results


# ---------------------------------------------------------------------------
# Social profile finder
# ---------------------------------------------------------------------------
SOCIAL_DOMAINS = {
    "twitter.com": "X / Twitter",
    "x.com": "X / Twitter",
    "linkedin.com": "LinkedIn",
    "facebook.com": "Facebook",
    "instagram.com": "Instagram",
    "youtube.com": "YouTube",
    "tiktok.com": "TikTok",
    "pinterest.com": "Pinterest",
    "github.com": "GitHub",
    "threads.net": "Threads",
}


def find_social_profiles(domains, timeout=15):
    session = requests.Session()
    session.headers.update({"User-Agent": config.user_agent})
    results = []

    for domain in domains:
        base_url = domain if domain.startswith(("http://", "https://")) else f"https://{domain}"
        found = {}
        try:
            resp = session.get(base_url, timeout=timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                netloc = urlparse(urljoin(base_url, href)).netloc.lower().replace("www.", "")
                for social_domain, platform in SOCIAL_DOMAINS.items():
                    if netloc == social_domain and platform not in found:
                        found[platform] = urljoin(base_url, href)
            results.append({"domain": base_url, "profiles": found, "error": None})
        except requests.exceptions.RequestException as e:
            results.append({"domain": base_url, "profiles": {}, "error": str(e)})

    return results


# ---------------------------------------------------------------------------
# Guest-post / outreach pitch personalizer — bulk mail-merge using each
# site's own <title> tag as the {{site_name}} placeholder value.
# ---------------------------------------------------------------------------
def personalize_pitches(domains, template, timeout=15):
    session = requests.Session()
    session.headers.update({"User-Agent": config.user_agent})
    results = []

    for domain in domains:
        base_url = domain if domain.startswith(("http://", "https://")) else f"https://{domain}"
        site_name = domain
        error = None
        try:
            resp = session.get(base_url, timeout=timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            if soup.title and soup.title.string:
                site_name = soup.title.string.strip()
        except requests.exceptions.RequestException as e:
            error = str(e)

        pitch = (
            template.replace("{{site_name}}", site_name)
                    .replace("{{domain}}", urlparse(base_url).netloc)
        )
        results.append({"domain": base_url, "site_name": site_name, "pitch": pitch, "error": error})

    return results
