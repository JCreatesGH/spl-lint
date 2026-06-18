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
        if re.search(r"=\s*\*\w", text):
            add(0, "medium", "leading-wildcard", "Leading wildcard (=*term) can't use the index — slow.")
        # `field=*` (star then space/end) matches every event that has the field — a no-op filter.
        for m in re.finditer(r"\b(\w+)\s*=\s*\*(?=\s|$)", text):
            if m.group(1).lower() != "index":      # index=* has its own rule
                add(0, "low", "wildcard-field",
                    f"`{m.group(1)}=*` matches all events with that field — a no-op filter; remove it.")
                break
        if not re.search(r"\bsourcetype\s*=", text, re.I):
            add(0, "low", "no-sourcetype", "Consider adding sourcetype= to narrow the search.")

    for i, s in enumerate(stages):
        if s.command == "join":
            add(i, "high", "join", "`join` is expensive and capped at 50k rows — prefer `stats` by a key.")
        if s.command in ("append", "appendcols"):
            add(i, "medium", "append",
                f"`{s.command}` runs a capped subsearch (50k rows / time-limited) — prefer `stats`/`lookup`.")
        if s.command == "transaction":
            add(i, "medium", "transaction", "`transaction` is memory-heavy — prefer `stats`/`streamstats` when possible.")
        if s.command == "dedup":
            add(i, "low", "dedup",
                "`dedup` buffers events to de-duplicate; for latest-per-key, `stats latest(...) by <key>` is usually faster.")
        if s.command == "stats" and i == 0:
            add(i, "low", "stats-first", "Consider `tstats` over accelerated data models for big speedups.")
        # A subsearch ([ ... ]) is capped at 10k results / 60s; it may silently truncate.
        if "[" in s.args:
            add(i, "medium", "subsearch", "Subsearch is capped at 10k results / 60s — it may silently truncate; prefer `stats`/`lookup`.")
        # `sort` with no leading positive count (or `sort 0`) sorts the whole result set.
        if s.command == "sort":
            m = re.match(r"\s*(\d+)\b", s.args)
            if m is None or int(m.group(1)) == 0:
                add(i, "low", "sort-unbounded", "Unbounded `sort` — add a limit, e.g. `sort 1000 -_time`.")
        if s.command == "mvexpand":
            add(i, "low", "mvexpand", "`mvexpand` multiplies the event count — it can blow up the row set.")

    # field selection should come before expensive later stages? (informational)
    cmds = [s.command for s in stages]
    if "fields" not in cmds and "table" not in cmds and len(stages) > 3:
        add(len(stages) - 1, "low", "no-field-trim",
            "No `fields`/`table` to trim columns — pulling unused fields wastes I/O.")

    out.sort(key=lambda f: {"high": 0, "medium": 1, "low": 2}[f.severity])
    return out
