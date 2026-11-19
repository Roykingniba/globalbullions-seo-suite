import os

import pandas as pd

from config import config as app_config
from core.pipeline_config import PipelineConfig
from core.crawler import WebCrawler
from core.content_scorer import ContentScorer
from core.embeddings import EmbeddingEngine
from core.cannibalization import CannibalizationDetector
from core.link_mapper import LinkMapper
from core.graph_builder import GraphBuilder
from jobs.runner import update_progress


def build_basic_findings(pages_df):
    records = pages_df.to_dict("records")
    title_counts, h1_counts = {}, {}
    for r in records:
        title = (r.get("title") or "").strip()
        if title:
            title_counts[title] = title_counts.get(title, 0) + 1
        h1 = (r.get("h1") or "").strip()
        if h1:
            h1_counts[h1] = h1_counts.get(h1, 0) + 1

    findings = {
        "missing_titles": [], "duplicate_titles": [], "missing_meta": [],
        "missing_h1": [], "duplicate_h1": [], "thin_content": [],
    }
    for r in records:
        url = r["url"]
        title = (r.get("title") or "").strip()
        h1 = (r.get("h1") or "").strip()
        meta = (r.get("meta_description") or "").strip()
        word_count = r.get("word_count") or 0

        if not title:
            findings["missing_titles"].append(url)
        elif title_counts.get(title, 0) > 1:
            findings["duplicate_titles"].append(url)

        if not meta:
            findings["missing_meta"].append(url)

        if not h1:
            findings["missing_h1"].append(url)
        elif h1_counts.get(h1, 0) > 1:
            findings["duplicate_h1"].append(url)

        if word_count and word_count < 300:
            findings["thin_content"].append(url)

    return findings


def run_full_audit(job, root_url, max_pages):
    """Job-runner target: crawl a site, score content, detect cannibalization,
    map internal link opportunities, and build a link graph — one pass, one
    crawl, matching seo_tool's original pipeline (cli.py's run_pipeline)."""
    job_dir = os.path.join(app_config.data_dir, "jobs", job["id"])
    os.makedirs(job_dir, exist_ok=True)

    cfg = PipelineConfig(
        max_pages=max_pages,
        output_dir=job_dir,
        db_path=os.path.join(job_dir, "audit.db"),
        use_openai_embeddings=app_config.use_openai_embeddings,
        openai_api_key=app_config.openai_api_key,
        anthropic_api_key=app_config.anthropic_api_key,
    )

    def on_crawl_progress(done, total, url):
        update_progress(job, done, total, url, phase="Crawling")

    crawler = WebCrawler(cfg, progress_callback=on_crawl_progress)
    pages_df = crawler.crawl(root_url)
    if pages_df.empty:
        raise RuntimeError("No pages could be crawled — check the URL and that it isn't blocking crawlers via robots.txt.")

    update_progress(job, 1, 1, "Scoring content quality", phase="Scoring")
    scorer = ContentScorer(cfg)
    score_rows = scorer.score_pages(pages_df.to_dict("records"))
    scores_df = pd.DataFrame(score_rows)
    for col in scores_df.columns:
        pages_df[col] = scores_df[col].values

    update_progress(job, 1, 1, "Generating embeddings", phase="Embeddings")
    engine = EmbeddingEngine(cfg)
    embeddings = engine.encode(pages_df["body_text"].fillna("").tolist())

    update_progress(job, 1, 1, "Detecting content cannibalization", phase="Cannibalization")
    detector = CannibalizationDetector(cfg)
    conflicts_df = detector.find_conflicts(pages_df, embeddings)
    conflict_summary = detector.summary(conflicts_df)

    update_progress(job, 1, 1, "Mapping internal link opportunities", phase="Link mapping")
    mapper = LinkMapper(cfg)
    opps_df = mapper.find_opportunities(pages_df, embeddings)

    update_progress(job, 1, 1, "Building link graph", phase="Graph")
    builder = GraphBuilder(cfg)
    graph = builder.build(pages_df, opps_df)
    graph_path = builder.visualize(graph, output_path=os.path.join(job_dir, "link_graph.html"))
    graph_metrics = builder.metrics(graph)

    findings = build_basic_findings(pages_df)
    update_progress(job, 1, 1, "Done", phase="Done")

    sorted_opps = (
        opps_df.sort_values("semantic_relevance_score", ascending=False)
        if not opps_df.empty else opps_df
    )

    return {
        "pages_crawled": len(pages_df),
        "failed": len(crawler.failed),
        "avg_content_score": round(float(pages_df["content_score"].mean()), 1),
        "findings": findings,
        "conflicts": conflicts_df.to_dict("records"),
        "conflict_summary": conflict_summary,
        "opportunities": sorted_opps.head(50).to_dict("records"),
        "opportunities_total": len(opps_df),
        "graph_available": bool(graph_path),
        "graph_metrics": graph_metrics,
        "job_dir": job_dir,
    }


def _normalize_for_match(url):
    return url.rstrip("/")


def run_internal_link_suggestions(job, target_url, site_url, max_pages):
    """Crawls the site like run_full_audit, but skips cannibalization/graph
    building (not needed here) and instead filters the internal-link map down
    to just the one page the user cares about — both directions: pages that
    should link to it, and pages it should link out to."""
    job_dir = os.path.join(app_config.data_dir, "jobs", job["id"])
    os.makedirs(job_dir, exist_ok=True)

    cfg = PipelineConfig(
        max_pages=max_pages,
        output_dir=job_dir,
        db_path=os.path.join(job_dir, "linkfinder.db"),
        use_openai_embeddings=app_config.use_openai_embeddings,
        openai_api_key=app_config.openai_api_key,
        min_link_relevance_score=0.35,
        max_suggestions_per_page=25,
    )

    def on_crawl_progress(done, total, url):
        update_progress(job, done, total, url, phase="Crawling")

    crawler = WebCrawler(cfg, progress_callback=on_crawl_progress)
    pages_df = crawler.crawl(site_url)
    if pages_df.empty:
        raise RuntimeError("No pages could be crawled — check the URL and that it isn't blocking crawlers via robots.txt.")

    target_norm = _normalize_for_match(target_url)
    matched = pages_df[pages_df["url"].apply(_normalize_for_match) == target_norm]
    if matched.empty:
        raise RuntimeError(
            f"The target page ({target_url}) wasn't found within the {len(pages_df)} pages crawled — "
            "make sure it's reachable from the homepage/sitemap and inside the page-count limit."
        )

    update_progress(job, 1, 1, "Generating embeddings", phase="Embeddings")
    engine = EmbeddingEngine(cfg)
    embeddings = engine.encode(pages_df["body_text"].fillna("").tolist())

    update_progress(job, 1, 1, "Mapping internal link opportunities", phase="Link mapping")
    mapper = LinkMapper(cfg)
    opps_df = mapper.find_opportunities(pages_df, embeddings)
    update_progress(job, 1, 1, "Done", phase="Done")

    if opps_df.empty:
        outgoing, incoming = [], []
    else:
        outgoing = (
            opps_df[opps_df["source_url"].apply(_normalize_for_match) == target_norm]
            .sort_values("semantic_relevance_score", ascending=False).to_dict("records")
        )
        incoming = (
            opps_df[opps_df["target_url"].apply(_normalize_for_match) == target_norm]
            .sort_values("semantic_relevance_score", ascending=False).to_dict("records")
        )

    return {
        "target_url": matched.iloc[0]["url"],
        "target_title": matched.iloc[0]["title"],
        "pages_crawled": len(pages_df),
        "outgoing": outgoing,
        "incoming": incoming,
    }
