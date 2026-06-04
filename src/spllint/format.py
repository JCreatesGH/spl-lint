"""Pretty-print an SPL search: one command per line, normalized pipes."""
from __future__ import annotations
from .parse import split_pipeline


def format_spl(spl: str) -> str:
    stages = split_pipeline(spl)
    lines = []
    for i, s in enumerate(stages):
        body = s.raw.strip()
        body = " ".join(body.split())   # collapse internal whitespace
        lines.append(body if i == 0 else f"| {body}")
    return "\n".join(lines)
