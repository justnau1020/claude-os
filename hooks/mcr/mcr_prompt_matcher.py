#!/usr/bin/env python3
"""
MCR Prompt Matcher — Layer 1: UserPromptSubmit hook.
Receives user prompt, matches against vault index, injects relevant context.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcr_lib import (
    read_hook_input,
    write_hook_output,
    safe_exit_empty,
    load_index,
    tokenize_query,
    match_terms,
    filter_matches,
    record_injected,
    build_context_string,
)

CONTENT_BUDGET = 8000


def main():
    hook_input = read_hook_input()
    if hook_input is None:
        safe_exit_empty()

    prompt = hook_input.get("prompt") or hook_input.get("user_prompt") or hook_input.get("userPrompt", "")
    if len(prompt) < 5:
        safe_exit_empty()

    index = load_index()
    if index is None:
        safe_exit_empty()

    tokens = tokenize_query(prompt)
    if not tokens:
        safe_exit_empty()

    matches = match_terms(tokens, index)
    if not matches:
        safe_exit_empty()

    session_id = hook_input.get("session_id", "")
    matches = filter_matches(matches, session_id=session_id)
    if not matches:
        safe_exit_empty()

    context, injected = build_context_string(matches, CONTENT_BUDGET)
    if not context:
        safe_exit_empty()

    record_injected(injected, session_id)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    write_hook_output(output)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        safe_exit_empty()
