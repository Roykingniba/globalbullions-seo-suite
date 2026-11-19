"""Live content grading engine — deliberately pure-Python/regex, no spaCy or
network calls, so it stays fast enough for on-keystroke (debounced) scoring
in the browser. Reuses the tokenizer/stopword list from classic_seo so both
tools treat text the same way."""

import re
from collections import Counter

import textstat

from blueprints.classic_seo.logic import STOPWORDS, WORD_RE

HEADING_RE = re.compile(r"^#{1,3}\s+.+", re.MULTILINE)


def _tokenize(text):
    return [w.lower() for w in WORD_RE.findall(text)]


def _keyword_count(text_lower, keyword):
    keyword = keyword.strip().lower()
    if not keyword:
        return 0
    if " " in keyword:
        return text_lower.count(keyword)
    words = _tokenize(text_lower)
    return words.count(keyword)


def _first_n_words(text, n=100):
    words = text.split()
    return " ".join(words[:n])


def extract_suggested_keywords(text, title="", exclude=None, top_n=8):
    """Frequency/position-weighted phrase extraction — a content-driven guess
    at what this piece is actually about, NOT search-volume data (that needs
    a paid keyword-research API)."""
    exclude = {k.lower() for k in (exclude or [])}
    words = _tokenize(text)
    meaningful = [w for w in words if w not in STOPWORDS and len(w) > 2]

    first_100 = set(_tokenize(_first_n_words(text, 100)))
    title_words = set(_tokenize(title))

    def weight(phrase_words):
        base = 1.0
        if any(w in title_words for w in phrase_words):
            base += 2.0
        if any(w in first_100 for w in phrase_words):
            base += 1.0
        return base

    unigrams = Counter()
    for w in meaningful:
        unigrams[w] += weight([w])

    bigrams = Counter()
    for a, b in zip(words, words[1:]):
        if a in STOPWORDS or b in STOPWORDS:
            continue
        bigrams[f"{a} {b}"] += weight([a, b])

    trigrams = Counter()
    for a, b, c in zip(words, words[1:], words[2:]):
        if a in STOPWORDS or c in STOPWORDS:
            continue
        trigrams[f"{a} {b} {c}"] += weight([a, b, c])

    candidates = []
    for phrase, score in list(trigrams.items()) + list(bigrams.items()) + list(unigrams.items()):
        if phrase in exclude:
            continue
        candidates.append((phrase, score))

    candidates.sort(key=lambda x: x[1], reverse=True)

    seen_words = set()
    results = []
    for phrase, score in candidates:
        phrase_words = set(phrase.split())
        if phrase_words & seen_words and len(phrase_words) == 1:
            continue
        results.append(phrase)
        seen_words |= phrase_words
        if len(results) >= top_n:
            break
    return results


def _readability_label(flesch):
    if flesch >= 60:
        return "Good — easy to read"
    if flesch >= 40:
        return "Fair — could be simpler"
    return "Difficult — consider shorter sentences"


def grade_content(text, keyword, secondary_keywords=None, title=""):
    text = text or ""
    keyword = (keyword or "").strip()
    secondary_keywords = [k.strip() for k in (secondary_keywords or []) if k.strip()]
    title = title or ""

    plain_text = HEADING_RE.sub(lambda m: m.group(0).lstrip("#").strip(), text)
    words = plain_text.split()
    word_count = len(words)
    text_lower = plain_text.lower()

    kw_count = _keyword_count(text_lower, keyword) if keyword else 0
    kw_density = round((kw_count / word_count) * 100, 2) if word_count and keyword else 0.0
    first_100 = _first_n_words(plain_text, 100).lower()
    kw_in_first_100 = bool(keyword) and (keyword.lower() in first_100)
    kw_in_title = bool(keyword) and bool(title) and (keyword.lower() in title.lower())

    heading_count = len(HEADING_RE.findall(text))

    readability = {}
    try:
        flesch = textstat.flesch_reading_ease(plain_text) if word_count >= 20 else 0
        readability = {
            "flesch_reading_ease": round(flesch, 1),
            "label": _readability_label(flesch) if word_count >= 20 else "Add more text to measure",
        }
    except Exception:
        readability = {"flesch_reading_ease": 0, "label": "Add more text to measure"}

    secondary_coverage = {
        kw: (kw.lower() in text_lower) for kw in secondary_keywords
    }
    secondary_hit_ratio = (
        sum(secondary_coverage.values()) / len(secondary_coverage) if secondary_coverage else None
    )

    # ---- scoring: (weight, achieved_fraction) pairs, skipped if not applicable ----
    components = []
    if title:
        components.append(("keyword_in_title", 10, 1.0 if kw_in_title else 0.0))
    if keyword:
        components.append(("keyword_in_intro", 15, 1.0 if kw_in_first_100 else 0.0))
        if kw_count == 0:
            density_score = 0.0
        elif 0.5 <= kw_density <= 2.5:
            density_score = 1.0
        elif kw_density > 2.5:
            density_score = 0.4  # present but likely stuffed
        else:
            density_score = 0.5  # present but sparse
        components.append(("keyword_density", 20, density_score))
    length_score = (
        0.0 if word_count < 150 else
        0.5 if word_count < 300 else
        0.75 if word_count < 600 else
        1.0
    )
    components.append(("length", 20, length_score))
    flesch_val = readability.get("flesch_reading_ease", 0)
    read_score = (
        1.0 if flesch_val >= 60 else
        0.65 if flesch_val >= 40 else
        0.3 if flesch_val > 0 else 0.0
    )
    components.append(("readability", 15, read_score))
    heading_needed = word_count > 500
    heading_score = 1.0 if (heading_count > 0 or not heading_needed) else 0.0
    components.append(("headings", 10, heading_score))
    if secondary_hit_ratio is not None:
        components.append(("secondary_keywords", 10, secondary_hit_ratio))

    possible = sum(w for _, w, _ in components)
    achieved = sum(w * frac for _, w, frac in components)
    score = round((achieved / possible) * 100) if possible else 0

    checklist = []
    if title:
        checklist.append({
            "label": "Primary keyword appears in the title",
            "status": "pass" if kw_in_title else "fail",
            "detail": "" if kw_in_title else "Consider working your target keyword into the title.",
        })
    if keyword:
        checklist.append({
            "label": "Primary keyword appears in the first 100 words",
            "status": "pass" if kw_in_first_100 else "fail",
            "detail": "" if kw_in_first_100 else "Search engines and AI systems weight early mentions heavily — introduce the keyword up front.",
        })
        if kw_count == 0:
            kw_status, kw_detail = "fail", f"'{keyword}' doesn't appear in the content at all yet."
        elif kw_density > 2.5:
            kw_status, kw_detail = "warn", f"Density is {kw_density}% — this reads as keyword stuffing above ~2.5%."
        elif kw_density < 0.5:
            kw_status, kw_detail = "warn", f"Density is only {kw_density}% — consider a few more natural mentions."
        else:
            kw_status, kw_detail = "pass", f"Density is {kw_density}%, a healthy range."
        checklist.append({"label": "Keyword density is healthy (0.5%–2.5%)", "status": kw_status, "detail": kw_detail})
    checklist.append({
        "label": "Content length is substantial",
        "status": "pass" if word_count >= 600 else ("warn" if word_count >= 300 else "fail"),
        "detail": f"{word_count} words — {'solid depth' if word_count >= 600 else 'consider expanding for more thorough topic coverage' if word_count >= 300 else 'this reads as thin content; aim for 600+ words on most topics'}.",
    })
    checklist.append({
        "label": "Readability is approachable",
        "status": "pass" if flesch_val >= 60 else ("warn" if flesch_val >= 40 else "fail"),
        "detail": readability.get("label", ""),
    })
    checklist.append({
        "label": "Uses headings to break up longer content",
        "status": "pass" if heading_score == 1.0 else "warn",
        "detail": "" if heading_score == 1.0 else "Add a few `##` headings — long unbroken text is harder to scan and to extract answers from.",
    })
    if secondary_keywords:
        hit = sum(secondary_coverage.values())
        checklist.append({
            "label": f"Covers related keywords ({hit}/{len(secondary_keywords)})",
            "status": "pass" if secondary_hit_ratio >= 0.75 else ("warn" if secondary_hit_ratio >= 0.4 else "fail"),
            "detail": ", ".join(k for k, present in secondary_coverage.items() if not present) and
                      f"Missing: {', '.join(k for k, present in secondary_coverage.items() if not present)}" or "",
        })

    suggested = extract_suggested_keywords(plain_text, title=title, exclude=[keyword] + secondary_keywords)

    return {
        "score": score,
        "word_count": word_count,
        "heading_count": heading_count,
        "keyword_count": kw_count,
        "keyword_density_pct": kw_density,
        "keyword_in_title": kw_in_title,
        "keyword_in_first_100": kw_in_first_100,
        "readability": readability,
        "secondary_coverage": secondary_coverage,
        "checklist": checklist,
        "suggested_keywords": suggested,
    }


# Google's own published "helpful, reliable, people-first content" self-assessment
# questions (Search Central: Creating helpful, reliable, people-first content),
# plus core E-E-A-T concepts — these can't be graded algorithmically from text
# alone, so they're presented as a manual self-check rather than folded into
# the numeric score above.
HELPFUL_CONTENT_CHECKLIST = [
    "Does the content provide original information, reporting, research, or analysis?",
    "Does the content provide substantial value when compared to other pages on the topic?",
    "Does the content demonstrate first-hand expertise or experience with the subject?",
    "Would you trust this content for issues related to your money or your life (YMYL)?",
    "Is the content free of exaggerated or shocking claims made mainly to attract clicks?",
    "Was this content written primarily for people, not to manipulate search rankings?",
    "Does the page avoid stitching together content from multiple sources without adding value?",
    "Is the content free of obvious spelling, stylistic, or factual errors?",
    "Does the title or headline avoid overpromising relative to what the content delivers?",
    "Would someone leave this page feeling they'd learned enough about the topic?",
]
