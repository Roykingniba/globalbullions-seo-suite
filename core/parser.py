"""Ported ~as-is from seo_tool/scraper/parser.py — no Streamlit dependency."""

import json
import re
from urllib.parse import urljoin, urlparse, urldefrag
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup, Comment, Tag

# Tags whose entire subtree is boilerplate
_STRIP_TAGS = {
    "nav", "footer", "header", "aside",
    "script", "style", "noscript", "form",
    "button", "iframe", "svg",
}

# Substrings in class/id values that signal boilerplate containers
_STRIP_SIGNALS = {
    "nav", "navigation", "menu", "footer", "header",
    "sidebar", "breadcrumb", "cookie", "banner",
    "advert", "advertisement", "promo", "popup",
    "modal", "widget", "social", "share", "comment",
    "related", "recommended", "newsletter",
}


class PageParser:
    def __init__(self, base_domain: str):
        parsed = urlparse(base_domain)
        self.netloc = parsed.netloc

    # ------------------------------------------------------------------
    def parse(self, html: str, url: str) -> Dict:
        soup = BeautifulSoup(html, "lxml")

        # Call each expensive extractor once
        body_text = self._body_text(soup)
        int_links, ext_links = self._links(soup, url)

        return {
            "url": url,
            "title": self._title(soup),
            "h1": self._h1(soup),
            "h2s": json.dumps(self._headings(soup, "h2")),
            "h3s": json.dumps(self._headings(soup, "h3")),
            "meta_description": self._meta_desc(soup),
            "body_text": body_text,
            "internal_links": json.dumps(int_links),
            "external_links": json.dumps(ext_links),
            "word_count": len(body_text.split()) if body_text else 0,
        }

    # ------------------------------------------------------------------
    def _title(self, soup: BeautifulSoup) -> str:
        t = soup.find("title")
        return t.get_text(strip=True) if t else ""

    def _h1(self, soup: BeautifulSoup) -> str:
        t = soup.find("h1")
        return t.get_text(strip=True) if t else ""

    def _headings(self, soup: BeautifulSoup, tag: str) -> List[str]:
        return [h.get_text(strip=True) for h in soup.find_all(tag)]

    def _meta_desc(self, soup: BeautifulSoup) -> str:
        for attrs in ({"name": "description"}, {"property": "og:description"}):
            tag = soup.find("meta", attrs=attrs)
            if tag:
                return tag.get("content", "") or ""
        return ""

    def _body_text(self, soup: BeautifulSoup) -> str:
        # Work on a deep copy so the original soup is never mutated
        clone = BeautifulSoup(str(soup), "lxml")

        # 1. Strip HTML comments
        for c in clone.find_all(string=lambda t: isinstance(t, Comment)):
            c.extract()

        # 2. Remove boilerplate tag types outright
        for tag_name in _STRIP_TAGS:
            for tag in clone.find_all(tag_name):
                tag.decompose()

        # 3. Remove elements whose class/id contains boilerplate keywords.
        #    IMPORTANT: collect candidates first, *then* decompose in a second
        #    pass.  Decomposing inside find_all()'s iterator nulls the .attrs
        #    dict of child elements still pending in the list, causing the
        #    "'NoneType' object has no attribute 'get'" crash on the next iter.
        candidates = []
        for el in clone.find_all(True):
            # Guard: element may have been decomposed as a child of an earlier
            # candidate — skip it if its attrs dict is gone.
            if not isinstance(el, Tag) or el.attrs is None:
                continue
            try:
                classes = " ".join(el.get("class") or []).lower()
                elem_id = (el.get("id") or "").lower()
            except Exception:
                continue
            combined = classes + " " + elem_id
            if any(sig in combined for sig in _STRIP_SIGNALS):
                candidates.append(el)

        # Batch-decompose: top-level candidates implicitly remove their children
        for el in candidates:
            try:
                el.decompose()
            except Exception:
                pass

        # 4. Prefer <main>/<article> over the full <body>
        main = clone.find("main") or clone.find("article")
        root = main if main else (clone.find("body") or clone)

        text = root.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text).strip()

    # ------------------------------------------------------------------
    def _normalize(self, url: str) -> str:
        url, _ = urldefrag(url)
        return url.rstrip("/")

    def _links(self, soup: BeautifulSoup, page_url: str) -> Tuple[List[str], List[str]]:
        internal, external = set(), set()
        for a in soup.find_all("a", href=True):
            try:
                href_val = a["href"]
                # href can be a list on malformed HTML
                if isinstance(href_val, list):
                    href_val = href_val[0] if href_val else ""
                href = str(href_val).strip()
            except Exception:
                continue

            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue

            abs_url = self._normalize(urljoin(page_url, href))
            parsed = urlparse(abs_url)

            if parsed.scheme not in ("http", "https"):
                continue

            if parsed.netloc == self.netloc or parsed.netloc.endswith("." + self.netloc):
                internal.add(abs_url)
            else:
                external.add(abs_url)

        return sorted(internal), sorted(external)
