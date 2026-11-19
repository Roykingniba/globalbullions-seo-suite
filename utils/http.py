"""Shared HTTP helpers used across the lightweight, synchronous tools."""

import urllib.parse

import requests

from config import config


class FetchError(Exception):
    """Raised when a URL can't be fetched — carries a user-facing message."""


def normalize_url(raw: str) -> str:
    """Turn user input like 'example.com' or 'example.com/page' into a full URL."""
    raw = (raw or "").strip()
    if not raw:
        raise FetchError("Please enter a URL or domain.")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    parsed = urllib.parse.urlparse(raw)
    if not parsed.netloc:
        raise FetchError(f"'{raw}' doesn't look like a valid URL.")
    return raw


def domain_of(url: str) -> str:
    return urllib.parse.urlparse(url).netloc


def fetch(url: str, timeout: int = None, allow_redirects: bool = True, method: str = "GET"):
    """Fetch a URL with the shared session config. Raises FetchError on failure
    with a message safe to show directly to the user."""
    timeout = timeout or config.request_timeout
    headers = {"User-Agent": config.user_agent}
    try:
        resp = requests.request(
            method, url, headers=headers, timeout=timeout,
            allow_redirects=allow_redirects,
        )
        return resp
    except requests.exceptions.SSLError:
        raise FetchError(f"SSL error connecting to {url} — the certificate may be invalid or expired.")
    except requests.exceptions.ConnectionError:
        raise FetchError(f"Couldn't connect to {url} — the domain may not exist or is refusing connections.")
    except requests.exceptions.Timeout:
        raise FetchError(f"Timed out waiting for {url} to respond.")
    except requests.exceptions.RequestException as e:
        raise FetchError(f"Error fetching {url}: {e}")
