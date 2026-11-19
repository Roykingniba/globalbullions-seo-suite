"""Ported from seo_tool/mapper/link_mapper.py — unchanged logic."""

import json
import logging
import re
from typing import Dict, List, Set

import numpy as np
import pandas as pd

from core.pipeline_config import PipelineConfig

logger = logging.getLogger(__name__)

_STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "and", "or", "but", "if", "as",
}


class LinkMapper:
    """
    Vectorised internal link opportunity finder.
    Uses NumPy masking to short-list candidate pairs instead of an O(n^2)
    Python loop, then generates anchor text only for qualifying pairs.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config

    # ------------------------------------------------------------------
    def find_opportunities(
        self,
        df: pd.DataFrame,
        embeddings: np.ndarray,
    ) -> pd.DataFrame:
        if len(df) < 2:
            return self._empty_df()

        existing = self._existing_links(df)
        min_score = self.config.min_link_relevance_score
        max_per = self.config.max_suggestions_per_page

        # Similarity matrix (already L2-normalised)
        sim = (embeddings @ embeddings.T).astype(np.float32)
        np.fill_diagonal(sim, 0.0)  # no self-links

        urls = df["url"].tolist()
        titles = df["h1"].fillna(df["title"]).fillna("").tolist()
        bodies = df["body_text"].fillna("").tolist()

        rows: List[Dict] = []

        for i, src_url in enumerate(urls):
            existing_targets = existing.get(src_url, set())

            # Vectorised candidate selection: find all j above threshold
            row_scores = sim[i]  # shape (n,)
            candidates = np.where(row_scores >= min_score)[0]

            if candidates.size == 0:
                continue

            # Sort descending by score and take only what we need
            order = np.argsort(row_scores[candidates])[::-1]
            candidates = candidates[order]

            page_opps: List[Dict] = []
            for j in candidates:
                if len(page_opps) >= max_per:
                    break
                tgt_url = urls[j]
                if tgt_url in existing_targets:
                    continue
                page_opps.append({
                    "source_url": src_url,
                    "target_url": tgt_url,
                    "recommended_anchor_text": self._anchor_text(bodies[i], titles[j], bodies[j]),
                    "semantic_relevance_score": round(float(row_scores[j]), 4),
                    "opportunity_type": "semantic",
                })

            rows.extend(page_opps)

        logger.info("Link opportunities: %d", len(rows))
        return pd.DataFrame(rows) if rows else self._empty_df()

    # ------------------------------------------------------------------
    @staticmethod
    def _existing_links(df: pd.DataFrame) -> Dict[str, Set[str]]:
        result: Dict[str, Set[str]] = {}
        for _, row in df.iterrows():
            try:
                links = json.loads(row.get("internal_links") or "[]")
            except (json.JSONDecodeError, TypeError):
                links = []
            result[row["url"]] = set(links)
        return result

    # ------------------------------------------------------------------
    def _anchor_text(self, source_body: str, target_title: str, target_body: str) -> str:
        if not target_title and not target_body:
            return "related content"
        if target_title and len(target_title) <= 60:
            return self._clean(target_title)
        if target_title:
            key = self._key_phrase(target_title)
            pattern = re.compile(r"\b" + re.escape(key) + r"\b", re.IGNORECASE)
            match = pattern.search(source_body[:5_000])
            if match:
                return match.group(0)
        if target_title:
            words = [w for w in target_title.split() if w.lower() not in _STOP_WORDS]
            if words:
                return self._clean(" ".join(words[:4]))
        return "learn more"

    # ------------------------------------------------------------------
    @staticmethod
    def _key_phrase(title: str) -> str:
        words = [w for w in title.split() if w.lower() not in _STOP_WORDS]
        return " ".join(words[:3]) if words else title[:50]

    @staticmethod
    def _clean(text: str) -> str:
        text = re.sub(r"[^\w\s\-]", "", text)
        return re.sub(r"\s+", " ", text).strip()[:80]

    # ------------------------------------------------------------------
    @staticmethod
    def _empty_df() -> pd.DataFrame:
        return pd.DataFrame(columns=[
            "source_url", "target_url",
            "recommended_anchor_text", "semantic_relevance_score",
            "opportunity_type",
        ])
