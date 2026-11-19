"""KAI MCP download: finds the current plugin zip and reads its version from
the WordPress plugin header inside it, so publishing a new release is just
replacing the zip in ~/seo_suite/downloads/ (no code change, no restart)."""

import os
import re
import zipfile

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "downloads")

_HEADER_FIELDS = {
    "name": "Plugin Name",
    "version": "Version",
    "requires_wp": "Requires at least",
    "requires_php": "Requires PHP",
    "tested": "Tested up to",
    "description": "Description",
}

_cache = {"key": None, "info": None}


def _latest_zip():
    if not os.path.isdir(DOWNLOAD_DIR):
        return None
    zips = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)
            if f.lower().endswith(".zip") and f.lower().startswith("kai")]
    return max(zips, key=os.path.getmtime) if zips else None


def _read_header(zpath):
    info = {}
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():
            # The main plugin file sits one folder deep: kai-vibe/kai-vibe.php
            if name.count("/") != 1 or not name.endswith(".php"):
                continue
            head = z.read(name)[:8192].decode("utf-8", "ignore")
            if "Plugin Name:" not in head:
                continue
            for key, label in _HEADER_FIELDS.items():
                m = re.search(r"^[\s*#@/]*" + re.escape(label) + r":\s*(.+)$", head, re.M | re.I)
                if m:
                    info[key] = m.group(1).strip()
            break
    return info


def plugin_info():
    """Return {path, filename, size_kb, version, name, ...} or None if no zip is published."""
    path = _latest_zip()
    if not path:
        return None
    key = (path, os.path.getmtime(path))
    if _cache["key"] != key:
        try:
            header = _read_header(path)
        except (zipfile.BadZipFile, OSError):
            header = {}
        version = header.get("version", "")
        slug = "kai-mcp" + (f"-{version}" if version else "")
        _cache["info"] = {
            **header,
            "path": path,
            "download_name": f"{slug}.zip",
            "size_kb": max(1, round(os.path.getsize(path) / 1024)),
        }
        _cache["key"] = key
    return _cache["info"]
