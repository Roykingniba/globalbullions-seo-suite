"""Ported from seo_tool/analyzer/content_scorer.py — unchanged logic."""

import logging
from typing import Dict, List

import textstat

from core.pipeline_config import PipelineConfig

logger = logging.getLogger(__name__)


class ContentScorer:
    """
    Scores each page 0-100 across three dimensions:
      • Readability     – Flesch-Kincaid Reading Ease
      • Topic Depth     – Entity + noun-chunk breadth via SpaCy NER
      • Helpful Content – Optional LLM evaluation (Anthropic)
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._nlp = None
        self._load_spacy()

    # ------------------------------------------------------------------
    def _load_spacy(self):
        try:
            import spacy
            self._nlp = spacy.load(
                self.config.spacy_model,
                exclude=["senter"],  # senter not needed; shaves ~15% off inference
            )
            logger.info("SpaCy model loaded: %s", self.config.spacy_model)
        except Exception as exc:
            logger.warning("SpaCy unavailable (%s). Topic-depth will return 50.", exc)

    # ------------------------------------------------------------------
    def score_pages(self, pages: List[Dict]) -> List[Dict]:
        """Batch-score all pages. 3-5x faster than calling score_page() per row."""
        texts = [self._clean_text(p.get("body_text")) for p in pages]

        # -- Readability (pure Python, fast) --
        readability = [self._flesch(t) for t in texts]

        # -- Topic depth: batch via nlp.pipe() --
        topic = [50.0] * len(texts)
        if self._nlp:
            try:
                capped = [t[:5_000] if t else " " for t in texts]
                for idx, doc in enumerate(self._nlp.pipe(capped, batch_size=16)):
                    topic[idx] = self._topic_depth_doc(doc)
            except Exception as exc:
                logger.warning("Batch topic-depth error: %s", exc)

        # -- Helpful content (LLM — inherently serial) --
        helpful = [
            self._helpful_content(p) if self.config.enable_llm_scoring else 50.0
            for p in pages
        ]

        wr = self.config.readability_weight
        wt = self.config.topic_depth_weight
        wh = self.config.helpful_content_weight

        return [
            {
                "content_score": round(readability[i] * wr + topic[i] * wt + helpful[i] * wh, 2),
                "readability_score": round(readability[i], 2),
                "topic_depth_score": round(topic[i], 2),
                "helpful_content_score": round(helpful[i], 2),
            }
            for i in range(len(pages))
        ]

    # kept for backward compatibility
    def score_page(self, page: Dict) -> Dict:
        return self.score_pages([page])[0]

    # ------------------------------------------------------------------
    @staticmethod
    def _clean_text(raw) -> str:
        return str(raw).strip() if raw and str(raw) not in ("nan", "None") else ""

    # ------------------------------------------------------------------
    def _flesch(self, text: str) -> float:
        if not text or len(text.split()) < 10:
            return 0.0
        try:
            raw = textstat.flesch_reading_ease(text)
            if 60 <= raw <= 70:
                return 100.0
            elif raw > 70:
                return max(0.0, 100.0 - (raw - 70) * 1.5)
            else:
                return max(0.0, raw * (100.0 / 60.0))
        except Exception:
            return 50.0

    # ------------------------------------------------------------------
    def _topic_depth_doc(self, doc) -> float:
        """Score a pre-processed SpaCy Doc (used in batch path)."""
        try:
            entity_types = {ent.label_ for ent in doc.ents}
            unique_ents = {ent.text.lower() for ent in doc.ents}
            noun_chunks = {
                chunk.lemma_.lower()
                for chunk in doc.noun_chunks
                if len(chunk.text) > 2
            }
            type_score = min(40.0, len(entity_types) * 4.0)
            ent_score = min(30.0, len(unique_ents) * 0.6)
            chunk_score = min(30.0, len(noun_chunks) * 0.3)
            return type_score + ent_score + chunk_score
        except Exception as exc:
            logger.warning("Topic-depth error: %s", exc)
            return 50.0

    # ------------------------------------------------------------------
    def _helpful_content(self, page: Dict) -> float:
        if not self.config.anthropic_api_key:
            return 50.0
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)
            excerpt = (page.get("body_text") or "")[:2_000]
            title = page.get("title", "")
            prompt = f"""Rate this webpage on Google's Helpful Content guidelines (0-100).

Title: {title}
Content excerpt: {excerpt}

Award points for:
- Original, substantive value (0-30)
- Written for humans, not search engines (0-25)
- Demonstrated expertise or first-hand experience (0-25)
- Fully satisfies likely search intent (0-20)

Reply with ONLY a single integer 0-100."""
            msg = client.messages.create(
                model=self.config.llm_model,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            return min(100.0, max(0.0, float(msg.content[0].text.strip())))
        except Exception as exc:
            logger.warning("LLM scoring failed: %s", exc)
            return 50.0
