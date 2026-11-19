"""Keyword ideation tools. Neither of these use paid keyword-research APIs
(Google Ads Keyword Planner, SEMrush, Ahrefs, etc. all require a paid account
for volume data) — they're built entirely from Google's public autocomplete
endpoint and deterministic question/preposition combinations, so there's no
search-volume number here, only breadth of related phrasing people actually
type."""

import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from config import config

QUESTION_WORDS = ["what", "why", "how", "who", "when", "where", "which", "will", "can", "should", "does", "is", "are"]
PREPOSITIONS = ["for", "vs", "versus", "without", "with", "near", "like", "or"]
ALPHABET = list("abcdefghijklmnopqrstuvwxyz")

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "is", "are", "was", "were",
    "to", "of", "in", "on", "at", "for", "with", "by", "from", "as", "how",
    "what", "why", "who", "when", "where", "which", "will", "can", "should",
    "does", "do", "vs", "versus", "near", "like",
}


def _autocomplete(query, timeout=6):
    """Query Google's public (undocumented but long-standing and widely used
    by free keyword tools) autocomplete/suggest endpoint. Best-effort: returns
    an empty list on any failure rather than raising, since one failed query
    shouldn't sink the whole batch."""
    try:
        resp = requests.get(
            "https://suggestqueries.google.com/complete/search",
            params={"client": "firefox", "q": query},
            headers={"User-Agent": config.user_agent},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return [s for s in data[1] if isinstance(s, str)]
    except Exception:
        return []


def generate_keyword_ideas(seed):
    seed = seed.strip().lower()
    if not seed:
        return {"seed": seed, "autocomplete": [], "alphabet": {}, "questions": [], "prepositions": []}

    queries = {"_seed": seed}
    for letter in ALPHABET:
        queries[f"az:{letter}"] = f"{seed} {letter}"
    for qw in QUESTION_WORDS:
        queries[f"q:{qw}"] = f"{qw} {seed}"
    for prep in PREPOSITIONS:
        queries[f"p:{prep}"] = f"{seed} {prep}"

    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_key = {executor.submit(_autocomplete, q): key for key, q in queries.items()}
        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                results[key] = future.result()
            except Exception:
                results[key] = []

    autocomplete = sorted(set(results.get("_seed", [])))

    alphabet = {}
    for letter in ALPHABET:
        suggestions = [s for s in results.get(f"az:{letter}", []) if s.lower() != seed]
        if suggestions:
            alphabet[letter] = sorted(set(suggestions))

    questions = sorted({s for qw in QUESTION_WORDS for s in results.get(f"q:{qw}", [])})
    prepositions = sorted({s for prep in PREPOSITIONS for s in results.get(f"p:{prep}", [])})

    return {
        "seed": seed,
        "autocomplete": autocomplete,
        "alphabet": alphabet,
        "questions": questions,
        "prepositions": prepositions,
        "total_count": len(autocomplete) + sum(len(v) for v in alphabet.values()) + len(questions) + len(prepositions),
    }


def cluster_keywords(keywords):
    """Group a flat list of keywords into topic clusters using shared
    significant-word overlap — no ML, no external data, fully deterministic."""
    cleaned = [k.strip() for k in keywords if k.strip()]
    tokenized = []
    for kw in cleaned:
        tokens = {w for w in re.findall(r"[a-z0-9']+", kw.lower()) if w not in _STOPWORDS and len(w) > 2}
        tokenized.append((kw, tokens))

    token_freq = Counter()
    for _, tokens in tokenized:
        token_freq.update(tokens)

    clusters = {}
    used = set()
    # Seed clusters with the most common significant tokens first, so the
    # biggest, most obvious topic groups form before leftovers get bucketed.
    for token, _ in token_freq.most_common():
        if token in used:
            continue
        members = [kw for kw, tokens in tokenized if token in tokens and kw not in
                   {m for members in clusters.values() for m in members}]
        if len(members) >= 2:
            clusters[token] = members
            used.add(token)

    grouped = {kw for members in clusters.values() for kw in members}
    leftovers = [kw for kw, _ in tokenized if kw not in grouped]

    cluster_list = [{"label": token, "keywords": members} for token, members in clusters.items()]
    cluster_list.sort(key=lambda c: len(c["keywords"]), reverse=True)
    if leftovers:
        cluster_list.append({"label": "Ungrouped", "keywords": leftovers})

    return cluster_list
