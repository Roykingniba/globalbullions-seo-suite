"""Pure-stdlib helpers for the Text and Data Utilities tools.

Everything here runs on the standard library only. That is deliberate: these
tools add no new packages to requirements.txt and nothing to the cold-start
cost, which matters because the app already imports torch on first request.
"""

import base64
import binascii
import colorsys
import difflib
import hashlib
import html as html_mod
import json
import re
import secrets
import string
import unicodedata
import urllib.parse
import uuid


class ToolError(Exception):
    """Raised for input the user can fix, and shown to them verbatim."""


# ── Text counting ─────────────────────────────────────────────────────────

_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")


def count_text(text):
    words = text.split()
    stripped = text.strip()
    paragraphs = [p for p in re.split(r"\n\s*\n", stripped) if p.strip()]
    sentences = [s for s in _SENTENCE_SPLIT.split(stripped) if s.strip()]
    lines = stripped.splitlines() if stripped else []

    longest = max((len(w) for w in words), default=0)
    avg_word = round(sum(len(w) for w in words) / len(words), 1) if words else 0.0

    # 200 words per minute for silent reading, 130 for speaking aloud. These
    # are the usual rules of thumb, not measurements of any specific reader.
    read_min = len(words) / 200 if words else 0
    speak_min = len(words) / 130 if words else 0

    freq = {}
    for raw in words:
        key = re.sub(r"[^\w'-]", "", raw.lower())
        if key:
            freq[key] = freq.get(key, 0) + 1
    top = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:12]

    return {
        "characters": len(text),
        "characters_no_spaces": len(re.sub(r"\s", "", text)),
        "words": len(words),
        "unique_words": len(freq),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "lines": len(lines),
        "longest_word": longest,
        "avg_word_length": avg_word,
        "reading_time": _fmt_minutes(read_min),
        "speaking_time": _fmt_minutes(speak_min),
        "top_words": top,
    }


def _fmt_minutes(minutes):
    if minutes <= 0:
        return "0 sec"
    total = int(round(minutes * 60))
    m, s = divmod(total, 60)
    if m and s:
        return f"{m} min {s} sec"
    if m:
        return f"{m} min"
    return f"{s} sec"


# ── Case conversion ───────────────────────────────────────────────────────

# Words kept lowercase in title case unless they start or end the string.
_MINOR = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "if", "in",
    "into", "nor", "of", "on", "onto", "or", "over", "per", "so", "the",
    "to", "up", "via", "vs", "with", "yet",
}


def convert_case(text, mode):
    if mode == "lower":
        return text.lower()
    if mode == "upper":
        return text.upper()
    if mode == "sentence":
        return _sentence_case(text)
    if mode == "title":
        return _title_case(text)
    if mode == "camel":
        parts = _tokens(text)
        return parts[0].lower() + "".join(p.capitalize() for p in parts[1:]) if parts else ""
    if mode == "pascal":
        return "".join(p.capitalize() for p in _tokens(text))
    if mode == "snake":
        return "_".join(p.lower() for p in _tokens(text))
    if mode == "kebab":
        return "-".join(p.lower() for p in _tokens(text))
    if mode == "constant":
        return "_".join(p.upper() for p in _tokens(text))
    if mode == "alternating":
        out, i = [], 0
        for ch in text:
            if ch.isalpha():
                out.append(ch.lower() if i % 2 == 0 else ch.upper())
                i += 1
            else:
                out.append(ch)
        return "".join(out)
    if mode == "invert":
        return text.swapcase()
    raise ToolError(f"Unknown case mode: {mode}")


def _tokens(text):
    # Split on non-alphanumerics and on camelCase humps, so "myXMLParser" and
    # "my-xml parser" both come out as the same word list. Two passes are
    # needed: the first catches lower-to-upper ("myXml"), the second splits a
    # run of capitals from the word that follows ("XMLParser" -> "XML Parser").
    # Without the second, an acronym swallows the next word: myXMLParser would
    # tokenise as ["my", "XMLParser"] and snake_case to "my_xmlparser".
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return [t for t in re.split(r"[^A-Za-z0-9]+", spaced) if t]


def _sentence_case(text):
    lowered = text.lower()
    out = list(lowered)
    capitalize_next = True
    for i, ch in enumerate(out):
        if capitalize_next and ch.isalpha():
            out[i] = ch.upper()
            capitalize_next = False
        elif ch in ".!?":
            capitalize_next = True
    return "".join(out)


def _title_case(text):
    words = text.split()
    out = []
    for i, w in enumerate(words):
        bare = w.lower()
        if i not in (0, len(words) - 1) and bare.strip(string.punctuation) in _MINOR:
            out.append(bare)
        else:
            out.append(bare[:1].upper() + bare[1:] if bare else w)
    return " ".join(out)


# ── Slugs ─────────────────────────────────────────────────────────────────

def slugify(text, separator="-", lowercase=True, max_length=0):
    # Decompose accented characters, then drop the combining marks, so
    # "Crème Brûlée" becomes "creme-brulee" rather than losing the words.
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in normalized if not unicodedata.combining(c))
    ascii_only = ascii_only.encode("ascii", "ignore").decode("ascii")

    if lowercase:
        ascii_only = ascii_only.lower()

    slug = re.sub(r"[^\w\s-]", "", ascii_only).strip()
    slug = re.sub(r"[\s_-]+", separator, slug)
    slug = slug.strip(separator)

    if max_length and len(slug) > max_length:
        slug = slug[:max_length].rstrip(separator)
        # Avoid cutting a word in half when there is a separator to cut at.
        if separator in slug:
            head, _, tail = slug.rpartition(separator)
            if len(tail) < 3 and head:
                slug = head
    return slug


# ── Line tools ────────────────────────────────────────────────────────────

def process_lines(text, operation, case_sensitive=True, trim=True):
    lines = text.splitlines()
    if trim:
        lines = [ln.strip() for ln in lines]

    original_count = len(lines)

    if operation == "dedupe":
        seen, out = set(), []
        for ln in lines:
            key = ln if case_sensitive else ln.lower()
            if key not in seen:
                seen.add(key)
                out.append(ln)
        lines = out
    elif operation == "dedupe_keep_blank":
        seen, out = set(), []
        for ln in lines:
            if not ln.strip():
                out.append(ln)
                continue
            key = ln if case_sensitive else ln.lower()
            if key not in seen:
                seen.add(key)
                out.append(ln)
        lines = out
    elif operation == "sort_az":
        lines = sorted(lines, key=None if case_sensitive else str.lower)
    elif operation == "sort_za":
        lines = sorted(lines, key=None if case_sensitive else str.lower, reverse=True)
    elif operation == "sort_length":
        lines = sorted(lines, key=len)
    elif operation == "reverse":
        lines = lines[::-1]
    elif operation == "shuffle":
        lines = list(lines)
        # secrets rather than random: no reason to use a predictable PRNG here.
        for i in range(len(lines) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            lines[i], lines[j] = lines[j], lines[i]
    elif operation == "remove_blank":
        lines = [ln for ln in lines if ln.strip()]
    elif operation == "number":
        width = len(str(len(lines)))
        lines = [f"{str(i).rjust(width)}. {ln}" for i, ln in enumerate(lines, 1)]
    else:
        raise ToolError(f"Unknown operation: {operation}")

    return {
        "text": "\n".join(lines),
        "original_count": original_count,
        "result_count": len(lines),
        "removed": original_count - len(lines),
    }


# ── Diff ──────────────────────────────────────────────────────────────────

def diff_texts(left, right, ignore_case=False, ignore_whitespace=False):
    a = left.splitlines()
    b = right.splitlines()

    def norm(lines):
        out = lines
        if ignore_whitespace:
            out = [" ".join(ln.split()) for ln in out]
        if ignore_case:
            out = [ln.lower() for ln in out]
        return out

    matcher = difflib.SequenceMatcher(None, norm(a), norm(b))
    rows = []
    added = removed = changed = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for off in range(i2 - i1):
                rows.append({"kind": "equal", "left_no": i1 + off + 1,
                             "right_no": j1 + off + 1, "left": a[i1 + off], "right": b[j1 + off]})
        elif tag == "delete":
            for off in range(i2 - i1):
                rows.append({"kind": "removed", "left_no": i1 + off + 1,
                             "right_no": None, "left": a[i1 + off], "right": ""})
                removed += 1
        elif tag == "insert":
            for off in range(j2 - j1):
                rows.append({"kind": "added", "left_no": None,
                             "right_no": j1 + off + 1, "left": "", "right": b[j1 + off]})
                added += 1
        elif tag == "replace":
            span = max(i2 - i1, j2 - j1)
            for off in range(span):
                lo = a[i1 + off] if i1 + off < i2 else ""
                ro = b[j1 + off] if j1 + off < j2 else ""
                rows.append({
                    "kind": "changed",
                    "left_no": i1 + off + 1 if i1 + off < i2 else None,
                    "right_no": j1 + off + 1 if j1 + off < j2 else None,
                    "left": lo, "right": ro,
                })
                changed += 1

    return {
        "rows": rows,
        "added": added,
        "removed": removed,
        "changed": changed,
        "identical": added == removed == changed == 0,
        "similarity": round(matcher.ratio() * 100, 1),
    }


# ── Encoding ──────────────────────────────────────────────────────────────

def base64_convert(text, action, url_safe=False):
    try:
        if action == "encode":
            raw = text.encode("utf-8")
            return (base64.urlsafe_b64encode(raw) if url_safe else base64.b64encode(raw)).decode("ascii")
        data = text.strip()
        # Restore padding: people routinely paste base64 with the "=" stripped.
        pad = (-len(data)) % 4
        data += "=" * pad
        decoded = base64.urlsafe_b64decode(data) if url_safe else base64.b64decode(data)
        return decoded.decode("utf-8")
    except (binascii.Error, ValueError) as e:
        raise ToolError(f"That does not look like valid Base64: {e}")
    except UnicodeDecodeError:
        raise ToolError("Decoded fine, but the result is binary data rather than text.")


def url_convert(text, action, component=True):
    if action == "encode":
        return urllib.parse.quote(text, safe="" if component else "/:?#[]@!$&'()*+,;=")
    try:
        return urllib.parse.unquote(text, errors="strict")
    except UnicodeDecodeError:
        raise ToolError("That contains percent-escapes that are not valid UTF-8.")


def html_convert(text, action, quotes=True):
    if action == "encode":
        return html_mod.escape(text, quote=quotes)
    return html_mod.unescape(text)


# ── Hashing ───────────────────────────────────────────────────────────────

HASH_ALGOS = ["md5", "sha1", "sha256", "sha384", "sha512"]


def hash_text(text, algos=None):
    raw = text.encode("utf-8")
    out = []
    for name in (algos or HASH_ALGOS):
        if name not in HASH_ALGOS:
            continue
        h = hashlib.new(name, raw)
        out.append({"algo": name.upper(), "digest": h.hexdigest(), "bits": h.digest_size * 8})
    return out


# ── Generators ────────────────────────────────────────────────────────────

def generate_uuids(count=10, version=4, uppercase=False, braces=False, hyphens=True):
    count = max(1, min(int(count), 500))
    out = []
    for _ in range(count):
        val = str(uuid.uuid4()) if version == 4 else str(uuid.uuid1())
        if not hyphens:
            val = val.replace("-", "")
        if uppercase:
            val = val.upper()
        if braces:
            val = "{" + val + "}"
        out.append(val)
    return out


AMBIGUOUS = "il1Lo0O"


def generate_passwords(length=20, count=5, lower=True, upper=True,
                       digits=True, symbols=True, exclude_ambiguous=False):
    length = max(4, min(int(length), 128))
    count = max(1, min(int(count), 50))

    pools = []
    if lower:
        pools.append(string.ascii_lowercase)
    if upper:
        pools.append(string.ascii_uppercase)
    if digits:
        pools.append(string.digits)
    if symbols:
        pools.append("!@#$%^&*()-_=+[]{};:,.?/")
    if not pools:
        raise ToolError("Pick at least one character type.")

    if exclude_ambiguous:
        pools = [
            "".join(c for c in p if c not in AMBIGUOUS) or p
            for p in pools
        ]

    alphabet = "".join(pools)
    out = []
    for _ in range(count):
        # Guarantee one character from each selected pool, then fill the rest,
        # then shuffle. Rejection-sampling instead would be slower and can loop.
        chars = [secrets.choice(p) for p in pools]
        chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
        for i in range(len(chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chars[i], chars[j] = chars[j], chars[i]
        out.append("".join(chars[:length]))

    # log2(alphabet ** length), reported as a rough strength signal only.
    import math
    entropy = round(length * math.log2(len(alphabet)), 1)
    return {"passwords": out, "entropy_bits": entropy, "alphabet_size": len(alphabet)}


_LOREM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua enim ad minim veniam "
    "quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo "
    "consequat duis aute irure in reprehenderit voluptate velit esse cillum "
    "eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident "
    "sunt culpa qui officia deserunt mollit anim id est laborum"
).split()


def generate_lorem(kind="paragraphs", count=3, start_classic=True):
    count = max(1, min(int(count), 200))

    def sentence():
        n = 6 + secrets.randbelow(12)
        words = [_LOREM_WORDS[secrets.randbelow(len(_LOREM_WORDS))] for _ in range(n)]
        return words[0].capitalize() + " " + " ".join(words[1:]) + "."

    if kind == "words":
        words = [_LOREM_WORDS[secrets.randbelow(len(_LOREM_WORDS))] for _ in range(count)]
        if start_classic:
            words[:2] = ["lorem", "ipsum"]
        return " ".join(words)

    if kind == "sentences":
        out = [sentence() for _ in range(count)]
        if start_classic:
            out[0] = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        return " ".join(out)

    paras = []
    for i in range(count):
        body = " ".join(sentence() for _ in range(3 + secrets.randbelow(4)))
        if i == 0 and start_classic:
            body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " + body
        paras.append(body)
    return "\n\n".join(paras)


# ── JSON ──────────────────────────────────────────────────────────────────

def format_json(text, indent=2, sort_keys=False, minify=False, ensure_ascii=False):
    if not text.strip():
        raise ToolError("Paste some JSON first.")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        # Show the offending line, which is far more useful than the offset.
        lines = text.splitlines()
        snippet = lines[e.lineno - 1].strip() if 0 < e.lineno <= len(lines) else ""
        detail = f" Near line {e.lineno}, column {e.colno}"
        if snippet:
            detail += f": {snippet[:120]}"
        raise ToolError(f"{e.msg}.{detail}")

    if minify:
        out = json.dumps(parsed, separators=(",", ":"), sort_keys=sort_keys,
                         ensure_ascii=ensure_ascii)
    else:
        out = json.dumps(parsed, indent=int(indent), sort_keys=sort_keys,
                         ensure_ascii=ensure_ascii)

    return {
        "text": out,
        "kind": type(parsed).__name__,
        "top_level_keys": len(parsed) if isinstance(parsed, (dict, list)) else 1,
        "original_bytes": len(text.encode("utf-8")),
        "result_bytes": len(out.encode("utf-8")),
    }


# ── UTM builder ───────────────────────────────────────────────────────────

UTM_FIELDS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id"]


def build_utm(base_url, params, lowercase=True):
    base_url = (base_url or "").strip()
    if not base_url:
        raise ToolError("Enter the URL you want to tag.")
    if not re.match(r"^https?://", base_url, re.I):
        base_url = "https://" + base_url

    parsed = urllib.parse.urlsplit(base_url)
    if not parsed.netloc:
        raise ToolError("That does not look like a complete URL.")

    if not params.get("utm_source") or not params.get("utm_medium"):
        raise ToolError("Source and medium are both required. Analytics tools "
                        "group traffic by that pair, so a tag without them is not useful.")

    existing = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    # Drop any utm_* already on the URL so re-tagging does not duplicate them.
    existing = [(k, v) for k, v in existing if k.lower() not in UTM_FIELDS]

    for key in UTM_FIELDS:
        val = (params.get(key) or "").strip()
        if not val:
            continue
        if lowercase:
            val = val.lower()
        # Spaces in UTM values are a common source of split reports.
        val = re.sub(r"\s+", "-", val)
        existing.append((key, val))

    query = urllib.parse.urlencode(existing, quote_via=urllib.parse.quote)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))


# ── Colour ────────────────────────────────────────────────────────────────

_NAMED = {
    "black": "000000", "white": "ffffff", "red": "ff0000", "green": "008000",
    "blue": "0000ff", "yellow": "ffff00", "cyan": "00ffff", "magenta": "ff00ff",
    "gray": "808080", "grey": "808080", "orange": "ffa500", "purple": "800080",
    "navy": "000080", "teal": "008080", "silver": "c0c0c0", "maroon": "800000",
}


def parse_color(value):
    v = (value or "").strip().lower()
    if not v:
        raise ToolError("Enter a colour value.")

    if v in _NAMED:
        v = "#" + _NAMED[v]

    m = re.match(r"^#?([0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})$", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return _color_payload(r, g, b, a)

    m = re.match(r"^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,/\s]+([\d.%]+))?\s*\)$", v)
    if m:
        r, g, b = (int(round(float(m.group(i)))) for i in (1, 2, 3))
        a = _alpha(m.group(4))
        for c in (r, g, b):
            if not 0 <= c <= 255:
                raise ToolError("RGB channels must be between 0 and 255.")
        return _color_payload(r, g, b, a)

    m = re.match(r"^hsla?\(\s*([\d.]+)(?:deg)?[,\s]+([\d.]+)%?[,\s]+([\d.]+)%?(?:[,/\s]+([\d.%]+))?\s*\)$", v)
    if m:
        h_ = float(m.group(1)) % 360 / 360
        s_ = float(m.group(2)) / 100
        l_ = float(m.group(3)) / 100
        r_, g_, b_ = colorsys.hls_to_rgb(h_, l_, s_)
        return _color_payload(round(r_ * 255), round(g_ * 255), round(b_ * 255), _alpha(m.group(4)))

    raise ToolError("Could not read that colour. Try a form like #3b82f6, "
                    "rgb(59 130 246), hsl(217 91% 60%), or a name like teal.")


def _alpha(raw):
    if raw is None:
        return 1.0
    raw = raw.strip()
    if raw.endswith("%"):
        return max(0.0, min(float(raw[:-1]) / 100, 1.0))
    return max(0.0, min(float(raw), 1.0))


def _color_payload(r, g, b, a=1.0):
    hex6 = f"#{r:02x}{g:02x}{b:02x}"
    h_, l_, s_ = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    h_deg, s_pct, l_pct = round(h_ * 360), round(s_ * 100), round(l_ * 100)

    # WCAG relative luminance, used for the contrast ratios below.
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    lum = 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)
    on_white = round((1.05) / (lum + 0.05), 2)
    on_black = round((lum + 0.05) / 0.05, 2)

    return {
        "hex": hex6,
        "hex_alpha": f"#{r:02x}{g:02x}{b:02x}{round(a * 255):02x}" if a < 1 else hex6,
        "rgb": f"rgb({r} {g} {b})",
        "rgb_legacy": f"rgb({r}, {g}, {b})",
        "rgba": f"rgba({r}, {g}, {b}, {round(a, 3)})",
        "hsl": f"hsl({h_deg} {s_pct}% {l_pct}%)",
        "hsl_legacy": f"hsl({h_deg}, {s_pct}%, {l_pct}%)",
        "r": r, "g": g, "b": b, "alpha": round(a, 3),
        "h": h_deg, "s": s_pct, "l": l_pct,
        "luminance": round(lum, 4),
        "contrast_white": on_white,
        "contrast_black": on_black,
        "best_text": "#000000" if on_black > on_white else "#ffffff",
        "shades": [_shade(r, g, b, f) for f in (0.9, 0.75, 0.6, 0.45, 0.3)],
        "tints": [_tint(r, g, b, f) for f in (0.15, 0.3, 0.45, 0.6, 0.75)],
    }


def _shade(r, g, b, f):
    return f"#{round(r * f):02x}{round(g * f):02x}{round(b * f):02x}"


def _tint(r, g, b, f):
    return "#%02x%02x%02x" % (
        round(r + (255 - r) * f), round(g + (255 - g) * f), round(b + (255 - b) * f)
    )
