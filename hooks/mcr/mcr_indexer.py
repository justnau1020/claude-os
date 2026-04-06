#!/usr/bin/env python3
"""
MCR Indexer — Scans the vault and builds index.json.
Run manually after adding/editing vault files:
    python3 ~/.claude/hooks/mcr_indexer.py
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

# Add hooks dir to path for mcr_lib import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcr_lib import (
    VAULT_PATH,
    INDEX_PATH,
    STOPWORDS,
    parse_frontmatter,
    PRIORITY_MULTIPLIER,
)

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")
_HEADING_RE = re.compile(r"^#{2,3}\s+(.+)", re.MULTILINE)
_MD_STRIP_RE = re.compile(r"[*_`#\[\]()>]")

SKIP_DIRS = {".mcr", ".obsidian", ".git", ".trash", "templates"}
MAX_FILE_SIZE = 50 * 1024  # 50KB

# Term weights by source
W_KEYWORD = 5.0
W_ALIAS = 4.0
W_TAG = 3.0
W_TITLE = 2.0
W_HEADING = 1.5
W_BODY = 1.0


def extract_body_terms(body):
    """Extract meaningful terms from body text. Returns {term: weight}."""
    terms = {}

    # Extract heading terms (higher weight)
    for m in _HEADING_RE.finditer(body):
        heading_text = _MD_STRIP_RE.sub("", m.group(1)).lower()
        for token in _TOKEN_RE.findall(heading_text):
            if token not in STOPWORDS:
                terms[token] = max(terms.get(token, 0), W_HEADING)

    # Extract body terms (need 2+ occurrences)
    clean = _MD_STRIP_RE.sub(" ", body).lower()
    tokens = [t for t in _TOKEN_RE.findall(clean) if t not in STOPWORDS]
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1

    for t, count in freq.items():
        if count >= 2 and t not in terms:
            terms[t] = W_BODY

    return terms


def index_file(rel_path, full_path):
    """Index a single vault file. Returns (file_meta, term_entries) or None."""
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return None

    meta, body = parse_frontmatter(content)
    priority_mult = PRIORITY_MULTIPLIER.get(meta["priority"], 1.0)

    # Collect all terms with weights
    all_terms = {}

    # Keywords (highest weight)
    for kw in meta["keywords"]:
        kw_lower = kw.lower().strip()
        if kw_lower:
            all_terms[kw_lower] = W_KEYWORD * priority_mult
            # Also index individual words from multi-word keywords
            for word in _TOKEN_RE.findall(kw_lower):
                if word not in STOPWORDS and word != kw_lower:
                    all_terms[word] = max(all_terms.get(word, 0), W_KEYWORD * 0.6 * priority_mult)

    # Aliases
    for alias in meta["aliases"]:
        alias_lower = alias.lower().strip()
        if alias_lower:
            all_terms[alias_lower] = max(all_terms.get(alias_lower, 0), W_ALIAS * priority_mult)
            for word in _TOKEN_RE.findall(alias_lower):
                if word not in STOPWORDS and word != alias_lower:
                    all_terms[word] = max(all_terms.get(word, 0), W_ALIAS * 0.6 * priority_mult)

    # Tags
    for tag in meta["tags"]:
        tag_lower = tag.lower().strip()
        if tag_lower:
            all_terms[tag_lower] = max(all_terms.get(tag_lower, 0), W_TAG * priority_mult)

    # Title
    if meta["title"]:
        title_lower = meta["title"].lower()
        for word in _TOKEN_RE.findall(title_lower):
            if word not in STOPWORDS:
                all_terms[word] = max(all_terms.get(word, 0), W_TITLE * priority_mult)

    # Body terms
    body_terms = extract_body_terms(body)
    for term, weight in body_terms.items():
        all_terms[term] = max(all_terms.get(term, 0), weight * priority_mult)

    file_meta = {
        "title": meta["title"] or os.path.splitext(os.path.basename(rel_path))[0],
        "tags": meta["tags"],
        "priority": meta["priority"],
        "char_count": len(body.strip()),
        "mtime": os.path.getmtime(full_path),
    }

    return file_meta, all_terms


def build_index():
    """Scan vault and build the full index."""
    terms_index = {}  # term -> [{file, weight}]
    files_meta = {}   # rel_path -> {title, tags, priority, char_count, mtime}
    file_count = 0

    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip hidden/special dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        for fname in files:
            if not fname.endswith(".md"):
                continue

            full_path = os.path.join(root, fname)

            # Skip large files
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            rel_path = os.path.relpath(full_path, VAULT_PATH)
            result = index_file(rel_path, full_path)
            if result is None:
                continue

            file_meta, all_terms = result
            files_meta[rel_path] = file_meta
            file_count += 1

            # Add to inverted index
            for term, weight in all_terms.items():
                if term not in terms_index:
                    terms_index[term] = []
                terms_index[term].append({"file": rel_path, "weight": round(weight, 2)})

    # Sort each term's entries by weight descending
    for term in terms_index:
        terms_index[term].sort(key=lambda e: -e["weight"])

    index = {
        "version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "vault_path": VAULT_PATH,
        "file_count": file_count,
        "terms": terms_index,
        "files": files_meta,
    }

    return index


def main():
    # Ensure .mcr directory exists
    mcr_dir = os.path.join(VAULT_PATH, ".mcr")
    os.makedirs(mcr_dir, exist_ok=True)

    print(f"MCR Indexer: scanning {VAULT_PATH}...")
    index = build_index()

    # Atomic write
    tmp_path = INDEX_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, INDEX_PATH)

    print(f"Index built: {index['file_count']} files, {len(index['terms'])} unique terms")
    print(f"Written to: {INDEX_PATH}")

    # Print top terms for verification
    top_terms = sorted(index["terms"].items(), key=lambda x: -max(e["weight"] for e in x[1]))[:15]
    print("\nTop terms by weight:")
    for term, entries in top_terms:
        files = ", ".join(e["file"].split("/")[-1] for e in entries[:3])
        max_w = max(e["weight"] for e in entries)
        print(f"  {term} (w={max_w:.1f}) → {files}")


if __name__ == "__main__":
    main()
