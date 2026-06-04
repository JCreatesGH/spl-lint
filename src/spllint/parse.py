"""Split an SPL search into pipeline stages, respecting quotes/brackets."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class Stage:
    raw: str
    command: str       # "search" for the implicit first stage
    args: str

    @property
    def is_search(self) -> bool:
        return self.command == "search"


def _split_top_level(spl: str) -> List[str]:
    parts, buf = [], []
    depth = 0
    quote = None
    for ch in spl:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch; buf.append(ch); continue
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth = max(0, depth - 1)
        if ch == "|" and depth == 0:
            parts.append("".join(buf)); buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def split_pipeline(spl: str) -> List[Stage]:
    stages: List[Stage] = []
    for i, part in enumerate(_split_top_level(spl)):
        tokens = part.split(None, 1)
        first = tokens[0] if tokens else ""
        known = {"search","stats","tstats","eval","where","table","fields","sort","head",
                 "tail","dedup","rename","rex","join","transaction","timechart","chart",
                 "lookup","inputlookup","makeresults","bucket","bin","top","rare","mvexpand",
                 "spath","fillnull","streamstats","eventstats","append","appendcols","map"}
        if i == 0 and first.lower() not in known:
            stages.append(Stage(raw=part, command="search", args=part))
        else:
            stages.append(Stage(raw=part, command=first.lower(),
                                args=tokens[1] if len(tokens) > 1 else ""))
    return stages
