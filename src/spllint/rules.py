"""Correctness and performance lint rules for SPL."""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List
from .parse import split_pipeline, Stage


@dataclass
class Finding:
    stage: int
    severity: str       # high | medium | low
    rule: str
    message: str


def lint(spl: str) -> List[Finding]:
    stages = split_pipeline(spl)
    out: List[Finding] = []

    def add(i, sev, rule, msg):
        out.append(Finding(i, sev, rule, msg))

    search = stages[0] if stages else None
    if search and search.is_search:
        text = search.args
        if not re.search(r"\bindex\s*=", text, re.I):
            add(0, "high", "no-index", "Search has no index= — it will scan all indexes.")
        if re.search(r"\bindex\s*=\s*\*", text, re.I):
            add(0, "high", "index-wildcard", "index=* scans every index; name the index.")
        for m in re.finditer(r"=\s*\*\w", text):
            add(0, "medium", "leading-wildcard", "Leading wildcard (=*term) can't use the index — slow.")
        if not re.search(r"\bsourcetype\s*=", text, re.I):
            add(0, "low", "no-sourcetype", "Consider adding sourcetype= to narrow the search.")

    for i, s in enumerate(stages):
        if s.command == "join":
            add(i, "high", "join", "`join` is expensive and capped at 50k rows — prefer `stats` by a key.")
        if s.command == "transaction":
            add(i, "medium", "transaction", "`transaction` is memory-heavy — prefer `stats`/`streamstats` when possible.")
        if s.command == "stats" and i == 0:
            add(i, "low", "stats-first", "Consider `tstats` over accelerated data models for big speedups.")
        if s.command in ("table", "fields") and i < len(stages) - 1:
            pass
        if s.command == "sort" and not re.search(r"\b\d+\b|^\s*-?\w", s.args):
            add(i, "low", "sort-unbounded", "Unbounded `sort` — add a limit, e.g. `sort 1000 -_time`.")
        if s.command == "rex" and "max_match" not in s.args and re.search(r"\(\?P?<", s.args):
            pass

    # field selection should come before expensive later stages? (informational)
    cmds = [s.command for s in stages]
    if "fields" not in cmds and "table" not in cmds and len(stages) > 3:
        add(len(stages) - 1, "low", "no-field-trim",
            "No `fields`/`table` to trim columns — pulling unused fields wastes I/O.")

    out.sort(key=lambda f: {"high": 0, "medium": 1, "low": 2}[f.severity])
    return out
