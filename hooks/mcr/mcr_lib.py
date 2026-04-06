"""
MCR (Model Context Retrieval) — Shared Library
Automatic context injection for Claude Code via hooks.
Pure stdlib Python, no dependencies.

Configuration:
  Set MCR_VAULT_PATH env var or defaults to ~/obsidian-vault
"""

import json
import os
import re
import sys
from math import log2

VAULT_PATH = os.environ.get("MCR_VAULT_PATH", os.path.expanduser("~/obsidian-vault"))
INDEX_PATH = os.path.join(VAULT_PATH, ".mcr", "index.json")

STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall", "must",
    "not", "no", "nor", "if", "then", "else", "when", "while", "where",
    "how", "what", "which", "who", "whom", "whose", "why", "that", "this",
    "these", "those", "it", "its", "he", "she", "they", "them", "their",
    "we", "our", "you", "your", "me", "my", "him", "her", "his", "us",
    "all", "each", "every", "both", "few", "more", "most", "other", "some",
    "such", "than", "too", "very", "just", "about", "above", "after",
    "again", "also", "any", "because", "before", "between", "down", "during",
    "even", "first", "get", "into", "like", "make", "made", "many", "much",
    "new", "now", "only", "out", "over", "own", "same", "set", "so",
    "still", "take", "through", "under", "up", "use", "used", "using",
    "want", "well", "here", "there", "need", "know", "way", "look",
})

# --- Frontmatter Parsing ---

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TAGS_RE = re.compile(r"^tags:\s*\[(.*?)\]", re.MULTILINE)
_KW_RE = re.compile(r"^keywords:\s*(.+)", re.MULTILINE)
_ALIASES_RE = re.compile(r"^aliases:\s*\[(.*?)\]", re.MULTILINE)
_PRIORITY_RE = re.compile(r"^priority:\s*(\w+)", re.MULTILINE)
_TITLE_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)

PRIORITY_MULTIPLIER = {"high": 1.5, "normal": 1.0, "low": 0.5}


def parse_frontmatter(content):
    """Parse YAML-like frontmatter with regex. Returns (metadata_dict, body_text)."""
    meta = {"tags": [], "keywords": [], "aliases": [], "priority": "normal", "title": ""}
    body = content

    fm_match = _FM_RE.match(content)
    if fm_match:
        fm = fm_match.group(1)
        body = content[fm_match.end():]

        m = _TAGS_RE.search(fm)
        if m:
            meta["tags"] = [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]

        m = _KW_RE.search(fm)
        if m:
            meta["keywords"] = [k.strip().strip("'\"") for k in m.group(1).split(",") if k.strip()]

        m = _ALIASES_RE.search(fm)
        if m:
            meta["aliases"] = [a.strip().strip("'\"") for a in m.group(1).split(",") if a.strip()]

        m = _PRIORITY_RE.search(fm)
        if m:
            meta["priority"] = m.group(1).lower()

    title_match = _TITLE_RE.search(body)
    if title_match:
        meta["title"] = title_match.group(1).strip()

    return meta, body


# --- Tokenization ---

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")


def tokenize_query(text, max_chars=2000):
    """Extract search tokens from text. Returns set of lowercase terms + bigrams."""
    text = text[:max_chars].lower()
    tokens = [t for t in _TOKEN_RE.findall(text) if t not in STOPWORDS]

    result = set(tokens)
    for i in range(len(tokens) - 1):
        result.add(f"{tokens[i]} {tokens[i+1]}")

    return result


# --- Index Loading ---

def load_index():
    """Load index.json. Returns dict or None on failure."""
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


# --- Matching ---

def match_terms(tokens, index):
    """Match tokens against index. Returns [(relative_path, score)] sorted by score desc."""
    terms_index = index.get("terms", {})
    files_meta = index.get("files", {})
    scores = {}
    match_counts = {}

    for token in tokens:
        entries = terms_index.get(token, [])
        for entry in entries:
            fp = entry["file"]
            w = entry["weight"]
            scores[fp] = scores.get(fp, 0.0) + w
            match_counts[fp] = match_counts.get(fp, 0) + 1

    for fp in scores:
        n = match_counts[fp]
        if n > 1:
            scores[fp] *= (1.0 + 0.3 * log2(n))

    results = [(fp, sc) for fp, sc in scores.items() if sc >= 1.0]

    def sort_key(item):
        fp, sc = item
        char_count = files_meta.get(fp, {}).get("char_count", 99999)
        return (-sc, char_count, fp)

    results.sort(key=sort_key)
    return results


# --- File Reading with Budget ---

def read_vault_files(matches, char_budget, max_files=5):
    """Read matched vault files within character budget. Returns formatted string."""
    if not matches:
        return ""

    parts = []
    remaining = char_budget

    for fp, _score in matches[:max_files]:
        if remaining <= 100:
            break

        full_path = os.path.join(VAULT_PATH, fp)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        _, body = parse_frontmatter(content)
        body = body.strip()

        if not body:
            continue

        header = f"--- [vault: {fp}] ---\n"
        footer = "\n--- [end] ---"
        overhead = len(header) + len(footer)

        if len(body) + overhead <= remaining:
            parts.append(f"{header}{body}{footer}")
            remaining -= len(body) + overhead
        else:
            available = remaining - overhead - 50
            if available < 100:
                break
            truncated = body[:available] + "\n[...truncated, see full file in vault]"
            parts.append(f"{header}{truncated}{footer}")
            remaining = 0

    return "\n\n".join(parts)


# --- Output Building ---

MCR_HEADER = "[MCR: Knowledge vault context injected automatically. These are reference documents relevant to the current task.]"
MCR_FOOTER = "[End MCR context]"


def build_context_string(matches, char_budget):
    """Build the full additionalContext string from matches."""
    content = read_vault_files(matches, char_budget)
    if not content:
        return ""
    return f"{MCR_HEADER}\n\n{content}\n\n{MCR_FOOTER}"


# --- Safe Hook I/O ---

def read_hook_input():
    """Read JSON from stdin. Returns dict or None."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None


def write_hook_output(obj):
    """Write JSON to stdout and exit 0."""
    json.dump(obj, sys.stdout, ensure_ascii=False)
    sys.exit(0)


def safe_exit_empty():
    """Exit with empty output (no context injection, no blocking)."""
    sys.exit(0)
