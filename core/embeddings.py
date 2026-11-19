"""Ported from seo_tool/analyzer/embeddings.py — unchanged logic. Supports
either local sentence-transformers (default, per user's choice) or OpenAI API
embeddings via config.use_openai_embeddings, with the model loaded lazily on
first use (only when a job that needs it actually runs)."""

import logging
from typing import List

import numpy as np

from core.pipeline_config import PipelineConfig

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self._model = None
        if not config.use_openai_embeddings:
            self._load_st()

    # ------------------------------------------------------------------
    def _load_st(self):
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers: %s", self.config.embedding_model)
        self._model = SentenceTransformer(self.config.embedding_model)

    # ------------------------------------------------------------------
    def encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0,), dtype=np.float32)

        # Cap each text at 10 000 characters to keep memory predictable
        cleaned = [t[:10_000] if t else "empty" for t in texts]

        if self.config.use_openai_embeddings:
            return self._encode_openai(cleaned)
        return self._encode_st(cleaned)

    # ------------------------------------------------------------------
    def _encode_st(self, texts: List[str]) -> np.ndarray:
        bs = self.config.embedding_batch_size
        chunks = []
        for i in range(0, len(texts), bs):
            batch = [t if t.strip() else "empty" for t in texts[i : i + bs]]
            vecs = self._model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,   # L2-norm → dot product == cosine sim
            )
            chunks.append(vecs)
        return np.vstack(chunks).astype(np.float32)

    # ------------------------------------------------------------------
    def _encode_openai(self, texts: List[str]) -> np.ndarray:
        from openai import OpenAI

        client = OpenAI(api_key=self.config.openai_api_key)
        bs = self.config.embedding_batch_size
        all_vecs: List[List[float]] = []

        for i in range(0, len(texts), bs):
            batch = [t if t.strip() else "empty" for t in texts[i : i + bs]]
            resp = client.embeddings.create(
                input=batch,
                model=self.config.openai_embedding_model,
            )
            all_vecs.extend(e.embedding for e in resp.data)

        arr = np.array(all_vecs, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        return arr / (norms + 1e-8)
