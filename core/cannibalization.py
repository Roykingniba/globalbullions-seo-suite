"""Ported from seo_tool/analyzer/cannibalization.py — unchanged logic."""

import logging
from urllib.parse import urlparse
from typing import Dict

import numpy as np
import pandas as pd

from core.pipeline_config import PipelineConfig

logger = logging.getLogger(__name__)


class CannibalizationDetector:
    """
    Vectorised cosine-similarity conflict detector.
    Uses NumPy to find all pairs above threshold in one operation
    instead of a Python nested loop.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config

    # ------------------------------------------------------------------
    def find_conflicts(self, df: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
        if len(df) < 2:
            return self._empty_df()

        logger.info("Computing %dx%d similarity matrix ...", len(df), len(df))

        # Embeddings are already L2-normalised -> dot product == cosine similarity
        sim = (embeddings @ embeddings.T).astype(np.float32)

        thresh = self.config.cannibalization_threshold

        # Vectorised: find all (i, j) pairs in the upper triangle above threshold
        upper = np.triu(sim, k=1)
        i_idx, j_idx = np.where(upper >= thresh)

        if len(i_idx) == 0:
            return self._empty_df()

        urls = df["url"].tolist()
        rows = []
        for k in range(len(i_idx)):
            i, j = int(i_idx[k]), int(j_idx[k])
            score = float(sim[i, j])
            master = self._master(df.iloc[i], df.iloc[j])
            rows.append({
                "url_a": urls[i],
                "url_b": urls[j],
                "similarity_score": round(score, 4),
                "master_url": master,
                "conflict_type": "semantic",
            })

        logger.info("Conflicts found: %d", len(rows))
        return pd.DataFrame(rows) if rows else self._empty_df()

    # ------------------------------------------------------------------
    def _master(self, a: pd.Series, b: pd.Series) -> str:
        sa = float(a.get("content_score") or 0)
        sb = float(b.get("content_score") or 0)
        if abs(sa - sb) > 5:
            return a["url"] if sa > sb else b["url"]
        da = int(a.get("depth") or 0)
        db = int(b.get("depth") or 0)
        if da != db:
            return a["url"] if da < db else b["url"]
        segs_a = len(urlparse(a["url"]).path.split("/"))
        segs_b = len(urlparse(b["url"]).path.split("/"))
        return a["url"] if segs_a <= segs_b else b["url"]

    # ------------------------------------------------------------------
    @staticmethod
    def _empty_df() -> pd.DataFrame:
        return pd.DataFrame(
            columns=["url_a", "url_b", "similarity_score", "master_url", "conflict_type"]
        )

    # ------------------------------------------------------------------
    def summary(self, df: pd.DataFrame) -> Dict:
        if df.empty:
            return {"total_conflicts": 0, "affected_pages": 0, "avg_similarity": 0.0}
        affected = set(df["url_a"]) | set(df["url_b"])
        return {
            "total_conflicts": len(df),
            "affected_pages": len(affected),
            "avg_similarity": round(float(df["similarity_score"].mean()), 4),
        }
