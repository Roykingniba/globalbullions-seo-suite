import difflib
import math
from collections import Counter
from datetime import date
from xml.sax.saxutils import escape as xml_escape

from config import AI_CRAWLER_USER_AGENTS
from blueprints.classic_seo.logic import WORD_RE, STOPWORDS


def generate_sitemap_xml(urls):
    today = date.today().isoformat()
    entries = "".join(
        f"<url><loc>{xml_escape(u)}</loc><lastmod>{today}</lastmod></url>"
        for u in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}</urlset>"
    )


def generate_robots_txt(disallow_paths, sitemap_url, crawl_delay, blocked_ai_agents):
    lines = ["User-agent: *", "Allow: /"]
    for path in disallow_paths:
        path = path.strip()
        if path:
            lines.append(f"Disallow: {path}")
    if crawl_delay:
        lines.append(f"Crawl-delay: {crawl_delay}")

    for agent, _ in AI_CRAWLER_USER_AGENTS:
        if agent in blocked_ai_agents:
            lines.append("")
            lines.append(f"User-agent: {agent}")
            lines.append("Disallow: /")

    if sitemap_url:
        lines.append("")
        lines.append(f"Sitemap: {sitemap_url}")

    return "\n".join(lines) + "\n"


def generate_meta_tags(title, description, url, image_url, site_name, twitter_handle):
    lines = []
    if title:
        lines.append(f"<title>{xml_escape(title)}</title>")
    if description:
        lines.append(f'<meta name="description" content="{xml_escape(description)}">')
    if url:
        lines.append(f'<link rel="canonical" href="{xml_escape(url)}">')
    lines.append(f'<meta property="og:type" content="website">')
    if title:
        lines.append(f'<meta property="og:title" content="{xml_escape(title)}">')
    if description:
        lines.append(f'<meta property="og:description" content="{xml_escape(description)}">')
    if url:
        lines.append(f'<meta property="og:url" content="{xml_escape(url)}">')
    if site_name:
        lines.append(f'<meta property="og:site_name" content="{xml_escape(site_name)}">')
    if image_url:
        lines.append(f'<meta property="og:image" content="{xml_escape(image_url)}">')
    lines.append(f'<meta name="twitter:card" content="{"summary_large_image" if image_url else "summary"}">')
    if twitter_handle:
        lines.append(f'<meta name="twitter:site" content="{xml_escape(twitter_handle)}">')
    if title:
        lines.append(f'<meta name="twitter:title" content="{xml_escape(title)}">')
    if description:
        lines.append(f'<meta name="twitter:description" content="{xml_escape(description)}">')
    if image_url:
        lines.append(f'<meta name="twitter:image" content="{xml_escape(image_url)}">')
    return "\n".join(lines)


def generate_htaccess(redirect_pairs):
    lines = ["RewriteEngine On", ""]
    for old, new in redirect_pairs:
        old, new = old.strip(), new.strip()
        if old and new:
            lines.append(f"Redirect 301 {old} {new}")
    return "\n".join(lines) + "\n"


def _tokenize(text):
    return [w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOPWORDS and len(w) > 2]


def _cosine_similarity(tokens_a, tokens_b):
    vec_a, vec_b = Counter(tokens_a), Counter(tokens_b)
    all_words = set(vec_a) | set(vec_b)
    dot = sum(vec_a[w] * vec_b[w] for w in all_words)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _shingles(tokens, n=3):
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def compare_content_similarity(text_a, text_b):
    tokens_a, tokens_b = _tokenize(text_a), _tokenize(text_b)
    cosine = _cosine_similarity(tokens_a, tokens_b)

    shingles_a, shingles_b = _shingles(tokens_a), _shingles(tokens_b)
    if shingles_a or shingles_b:
        shared = len(shingles_a & shingles_b)
        total = len(shingles_a | shingles_b) or 1
        shingle_overlap = shared / total
    else:
        shingle_overlap = 0.0

    sequence_ratio = difflib.SequenceMatcher(None, text_a[:20000], text_b[:20000]).ratio()

    overall = round(((cosine * 0.5) + (shingle_overlap * 0.3) + (sequence_ratio * 0.2)) * 100, 1)

    return {
        "overall_similarity_pct": overall,
        "word_overlap_pct": round(cosine * 100, 1),
        "phrase_overlap_pct": round(shingle_overlap * 100, 1),
        "sequence_match_pct": round(sequence_ratio * 100, 1),
        "word_count_a": len(text_a.split()),
        "word_count_b": len(text_b.split()),
    }
