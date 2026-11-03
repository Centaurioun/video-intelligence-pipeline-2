"""Transparent filename/parent metadata floor."""
from __future__ import annotations

import re
from collections.abc import Iterable


def metadata_tokens(query: str, basename: str, parent: str) -> set[str]:
    text = " ".join((query, basename, parent)).casefold()
    # Keep only Unicode letters/digits; underscores and all punctuation delimit.
    tokens: list[str] = []
    current: list[str] = []
    for char in text:
        if char.isalnum():
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return set(tokens)


def token_set_jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def metadata_score(query: str, basename: str, parent: str) -> float:
    # The floor compares the unchanged query token set against source metadata.
    query_tokens = metadata_tokens(query, "", "")
    source_tokens = metadata_tokens("", basename, parent)
    return token_set_jaccard(query_tokens, source_tokens)
