#!/usr/bin/env python3
"""
MCR Tool Matcher — Layer 2: PreToolUse hook.
Auto-allows all tools (replacing old echo hook).
For "need-signal" tools (Read/Grep/Glob/WebSearch/WebFetch),
also injects relevant vault context based on what Claude is looking for.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcr_lib import (
    read_hook_input,
    write_hook_output,
    load_index,
    tokenize_query,
    match_terms,
    filter_matches,
    record_injected,
    build_context_string,
)

CONTENT_BUDGET = 7000

# Tools that signal Claude needs information
NEED_SIGNAL_TOOLS = {"Read", "Grep", "Glob", "WebSearch", "WebFetch"}

_PATH_SPLIT_RE = re.compile(r"[/\\._-]+")


def extract_search_terms(tool_name, tool_input):
    """Extract search-relevant text from tool input based on tool type."""
    if not isinstance(tool_input, dict):
        return ""

    if tool_name == "Read":
        # Extract meaningful path segments
        fp = tool_input.get("file_path", "")
        parts = _PATH_SPLIT_RE.split(fp)
        return " ".join(parts)

    if tool_name == "Grep":
        # Pattern is the primary signal, path adds context
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        path_parts = _PATH_SPLIT_RE.split(path)
        return f"{pattern} {' '.join(path_parts)}"

    if tool_name == "Glob":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        parts = _PATH_SPLIT_RE.split(f"{pattern} {path}")
        return " ".join(parts)

    if tool_name == "WebSearch":
        return tool_input.get("query", "")

    if tool_name == "WebFetch":
        url = tool_input.get("url", "")
        # Extract path segments and query params from URL
        parts = _PATH_SPLIT_RE.split(url)
        return " ".join(parts)

    return ""


def make_auto_allow(additional_context=None):
    """Build the auto-allow response, optionally with injected context."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "Auto-allowed by user preference",
        }
    }
    if additional_context:
        output["hookSpecificOutput"]["additionalContext"] = additional_context
    return output


def main():
    hook_input = read_hook_input()

    # If we can't read input, still auto-allow (never block)
    if hook_input is None:
        write_hook_output(make_auto_allow())
        return

    tool_name = hook_input.get("tool_name") or hook_input.get("toolName", "")
    tool_input = hook_input.get("tool_input") or hook_input.get("toolInput") or hook_input.get("input", {})

    # Not a need-signal tool — just auto-allow, no context injection
    if tool_name not in NEED_SIGNAL_TOOLS:
        write_hook_output(make_auto_allow())
        return

    # Try to inject context for need-signal tools
    index = load_index()
    if index is None:
        write_hook_output(make_auto_allow())
        return

    search_text = extract_search_terms(tool_name, tool_input)
    if len(search_text) < 3:
        write_hook_output(make_auto_allow())
        return

    tokens = tokenize_query(search_text)
    if not tokens:
        write_hook_output(make_auto_allow())
        return

    matches = match_terms(tokens, index)
    if not matches:
        write_hook_output(make_auto_allow())
        return

    session_id = hook_input.get("session_id", "")
    matches = filter_matches(matches, session_id=session_id)
    if not matches:
        write_hook_output(make_auto_allow())
        return

    context, injected = build_context_string(matches, CONTENT_BUDGET)
    if injected and session_id:
        record_injected(injected, session_id)
    write_hook_output(make_auto_allow(context if context else None))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never block on error — always auto-allow
        try:
            write_hook_output(make_auto_allow())
        except Exception:
            sys.exit(0)
