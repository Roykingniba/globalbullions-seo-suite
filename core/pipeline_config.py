"""Config for the crawl/score/cannibalization/link-map pipeline — kept separate
from the app-level config.py to avoid name collisions, and ported ~as-is from
seo_tool/config.py (Streamlit-free already)."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineConfig:
    # --- Crawler ---
    max_pages: int = 100
    request_delay: float = 1.0
    request_timeout: int = 15
    max_retries: int = 2
    user_agent: str = "Mozilla/5.0 (compatible; KaiSEOSuite/1.0; +https://globalbullions.com/seo-suite)"
    respect_robots_txt: bool = True
    max_depth: int = 6

    # --- NLP / Embeddings ---
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    use_openai_embeddings: bool = False
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-3-small"

    # --- Cannibalization ---
    cannibalization_threshold: float = 0.85

    # --- Content Scoring Weights (must sum to 1.0) ---
    readability_weight: float = 0.30
    topic_depth_weight: float = 0.40
    helpful_content_weight: float = 0.30

    # --- LLM Scoring (optional, Anthropic) ---
    enable_llm_scoring: bool = False
    anthropic_api_key: Optional[str] = None
    llm_model: str = "claude-haiku-4-5-20251001"

    # --- SpaCy ---
    spacy_model: str = "en_core_web_sm"

    # --- Link Mapping ---
    min_link_relevance_score: float = 0.50
    max_suggestions_per_page: int = 10

    # --- Storage / Output ---
    output_dir: str = "outputs"
    db_path: str = "seo_audit.db"
    graph_output: str = "link_graph.html"

    def __post_init__(self):
        os.makedirs(self.output_dir, exist_ok=True)
