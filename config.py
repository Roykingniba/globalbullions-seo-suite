import os
from dataclasses import dataclass, field


@dataclass
class Config:
    secret_key: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "dev-key-change-me"))
    user_agent: str = "Mozilla/5.0 (compatible; KaiSEOSuite/1.0; +https://globalbullions.com/seo-suite)"
    request_timeout: int = 15

    # Canonical production origin — used for canonical tags, sitemap.xml, and
    # Open Graph URLs so they're correct even when the app is reached via a
    # different host (localhost during dev, an IP, a staging subdomain, etc).
    # Includes the /seo-suite subdirectory since the app is mounted there,
    # not at the domain root — Passenger/WSGI sets SCRIPT_NAME for the
    # mount point automatically, so request.path stays relative and this
    # just needs to be the full mounted root.
    site_url: str = field(default_factory=lambda: os.environ.get("SITE_URL", "https://globalbullions.com/seo-suite"))

    openai_api_key: str = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    use_openai_embeddings: bool = field(default_factory=lambda: os.environ.get("USE_OPENAI_EMBEDDINGS", "false").lower() == "true")

    # Site crawler cap: the only remaining limit in the whole suite. The
    # cannibalization/link-mapper step builds an NxN similarity matrix in
    # memory, which grows quadratically — uncapped, a very large site could
    # exhaust Stellar Plus's 2GB RAM and take the whole site down for every
    # visitor. 20,000 pages (~1.6GB matrix) covers all but the largest sites
    # while keeping that failure mode out of reach.
    max_crawl_pages: int = 20_000

    data_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "data"))


config = Config()

# Well-known AI/LLM crawler user-agent tokens, used by the AI-crawler-access checker
# and the GEO readiness scorer. Kept as one shared list so both tools stay in sync.
AI_CRAWLER_USER_AGENTS = [
    ("GPTBot", "OpenAI — used to train/ground ChatGPT"),
    ("ChatGPT-User", "OpenAI — live browsing on behalf of a ChatGPT user"),
    ("OAI-SearchBot", "OpenAI — powers ChatGPT search"),
    ("ClaudeBot", "Anthropic — training crawler for Claude"),
    ("Claude-User", "Anthropic — live browsing on behalf of a Claude user"),
    ("Claude-SearchBot", "Anthropic — powers Claude search"),
    ("PerplexityBot", "Perplexity — crawls for its answer engine"),
    ("Perplexity-User", "Perplexity — live browsing on behalf of a user"),
    ("Google-Extended", "Google — controls use in Gemini/AI Overviews training"),
    ("GoogleOther", "Google — general-purpose auxiliary crawler"),
    ("CCBot", "Common Crawl — dataset used by many LLM trainers"),
    ("Bytespider", "ByteDance/TikTok — LLM training crawler"),
    ("Amazonbot", "Amazon — used for Alexa/AI products"),
    ("Applebot-Extended", "Apple — controls use in Apple Intelligence training"),
    ("Meta-ExternalAgent", "Meta — training crawler for Llama/AI products"),
    ("Diffbot", "Diffbot — feeds various downstream AI products"),
]
