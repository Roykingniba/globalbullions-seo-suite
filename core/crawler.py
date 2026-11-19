"""Ported from seo_tool/scraper/crawler.py — no Streamlit dependency, no
headless browser. Only change from the original: imports point at
core.pipeline_config / core.parser instead of the standalone seo_tool package,
and the tqdm progress bar is dropped (the job runner's progress_callback
already reports progress to the web UI)."""

import json
import logging
import time
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from typing import Callable, Dict, List, Optional
from urllib.parse import urldefrag, urlparse
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests

from core.pipeline_config import PipelineConfig
from core.parser import PageParser

logger = logging.getLogger(__name__)

_WORKERS = 5  # concurrent HTTP connections


class WebCrawler:
    def __init__(self, config: PipelineConfig, progress_callback: Optional[Callable] = None):
        self.config = config
        self.progress_callback = progress_callback
        self.session = self._build_session()
        self._robots_cache: Dict[str, Optional[RobotFileParser]] = {}
        self.visited: set = set()
        self.failed: set = set()
        # RLock, not Lock: crawl()'s locked block calls _is_allowed(), which
        # re-enters _robots()'s own `with self._lock` on the same thread — a
        # plain Lock would deadlock there every time.
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    def _build_session(self) -> requests.Session:
        s = requests.Session()
        s.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
        })
        return s

    # ------------------------------------------------------------------
    def _robots(self, netloc: str) -> Optional[RobotFileParser]:
        with self._lock:
            if netloc in self._robots_cache:
                return self._robots_cache[netloc]
        rp = RobotFileParser()
        try:
            rp.set_url(f"https://{netloc}/robots.txt")
            rp.read()
        except Exception:
            rp = None
        with self._lock:
            self._robots_cache[netloc] = rp
        return rp

    def _is_allowed(self, url: str) -> bool:
        if not self.config.respect_robots_txt:
            return True
        rp = self._robots(urlparse(url).netloc)
        return rp is None or rp.can_fetch(self.config.user_agent, url)

    # ------------------------------------------------------------------
    def _fetch(self, url: str) -> Optional[tuple]:
        """Returns (html, status_code, final_url) or None on failure."""
        for attempt in range(self.config.max_retries):
            try:
                resp = self.session.get(
                    url,
                    timeout=self.config.request_timeout,
                    allow_redirects=True,
                )
                if "text/html" not in resp.headers.get("Content-Type", ""):
                    return None
                return resp.text, resp.status_code, resp.url
            except requests.RequestException as exc:
                if attempt == self.config.max_retries - 1:
                    logger.warning("Failed %s: %s", url, exc)
                    return None
                time.sleep(0.5)
        return None

    # ------------------------------------------------------------------
    @staticmethod
    def _norm(url: str) -> str:
        url, _ = urldefrag(url)
        return url.rstrip("/")

    # ------------------------------------------------------------------
    def crawl(self, root_url: str) -> pd.DataFrame:
        root_url = self._norm(root_url)
        parsed_root = urlparse(root_url)
        base_domain = f"{parsed_root.scheme}://{parsed_root.netloc}"
        parser = PageParser(base_domain)

        pending: deque = deque([(root_url, 0)])
        pages: List[Dict] = []

        with ThreadPoolExecutor(max_workers=_WORKERS) as executor:
            futures: Dict = {}

            while (pending or futures) and len(pages) < self.config.max_pages:
                # Fill executor up to _WORKERS concurrent fetches
                while pending and len(futures) < _WORKERS \
                        and len(pages) + len(futures) < self.config.max_pages:
                    url, depth = pending.popleft()
                    norm_url = self._norm(url)
                    with self._lock:
                        if norm_url in self.visited:
                            continue
                        if depth > self.config.max_depth:
                            continue
                        if not self._is_allowed(norm_url):
                            logger.debug("robots.txt blocked: %s", norm_url)
                            continue
                        self.visited.add(norm_url)
                    futures[executor.submit(self._fetch, norm_url)] = (norm_url, depth)

                if not futures:
                    break

                # Wait for at least one fetch to finish
                done, _ = wait(
                    list(futures.keys()),
                    return_when=FIRST_COMPLETED,
                    timeout=self.config.request_timeout + 2,
                )
                if not done:
                    # Timeout — cancel remaining and stop
                    break

                for future in done:
                    url, depth = futures.pop(future)
                    try:
                        result = future.result()
                    except Exception as exc:
                        logger.warning("Fetch error %s: %s", url, exc)
                        with self._lock:
                            self.failed.add(url)
                        continue

                    if result is None:
                        with self._lock:
                            self.failed.add(url)
                        continue

                    html, status, final_url = result
                    final_url = self._norm(final_url)

                    if status != 200:
                        continue

                    try:
                        page = parser.parse(html, final_url)
                    except Exception as exc:
                        logger.warning("Parse error on %s: %s", final_url, exc)
                        continue

                    page["crawl_status"] = status
                    page["depth"] = depth
                    pages.append(page)

                    if self.progress_callback:
                        self.progress_callback(len(pages), self.config.max_pages, final_url)

                    # Enqueue newly discovered internal links
                    for link in json.loads(page.get("internal_links", "[]")):
                        normed = self._norm(link)
                        with self._lock:
                            if normed not in self.visited:
                                pending.append((normed, depth + 1))

                # Polite delay: sleep once per batch, not per page
                if self.config.request_delay > 0 and done:
                    time.sleep(self.config.request_delay)

        logger.info("Crawl done: %d pages, %d failed", len(pages), len(self.failed))
        return pd.DataFrame(pages)
