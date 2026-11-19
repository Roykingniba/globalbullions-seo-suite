"""Patches importlib.metadata.packages_distributions() with a fast
equivalent before anything in this package imports torch/transformers.

Root cause: transformers' import_utils.py calls the stdlib
packages_distributions(), which enumerates every file of every installed
distribution and calls .exists() on each one (via skip_missing_files) to
build a top-level-module -> distribution-name map. With a large venv (torch,
transformers, spacy, pandas, etc. and their transitive deps), that's
thousands of filesystem stat calls — individually fast on Linux, but on
Windows (especially under real-time antivirus scanning of freshly-installed
packages) this measurably turns a <2s call into a 60-90+ second hang, which
was reproduced and confirmed here via faulthandler.dump_traceback_later.

The replacement below gets the same top-level-name -> distribution mapping
from each distribution's top_level.txt metadata file (a single read, no
per-file existence check), which is what most real packages already ship.
"""

import importlib.metadata as _metadata


def _fast_packages_distributions():
    result = {}
    for dist in _metadata.distributions():
        name = dist.metadata.get("Name") if dist.metadata else None
        if not name:
            continue
        try:
            top_level_text = dist.read_text("top_level.txt")
        except Exception:
            top_level_text = None
        if top_level_text:
            for top in top_level_text.splitlines():
                top = top.strip()
                if top:
                    result.setdefault(top, []).append(name)
    return result


if not getattr(_metadata, "_kai_seo_suite_patched", False):
    _metadata.packages_distributions = _fast_packages_distributions
    _metadata._kai_seo_suite_patched = True
