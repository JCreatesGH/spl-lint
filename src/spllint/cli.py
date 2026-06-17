"""Command-line interface: lint and pretty-print a Splunk SPL search."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List, Optional

from .rules import lint
from .format import format_spl

R, Y, C, X = "\033[31m", "\033[33m", "\033[36m", "\033[0m"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spllint", description="Lint and format Splunk SPL searches.")
    parser.add_argument("query", nargs="*", help="SPL search (or read from stdin)")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--no-format", action="store_true", help="don't print the formatted query")
    args = parser.parse_args(argv)

    spl = " ".join(args.query) if args.query else sys.stdin.read()
    if not spl.strip():
        parser.print_usage(sys.stderr)
        return 2

    findings = lint(spl)

    if args.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2))
    else:
        if not args.no_format:
            print(format_spl(spl))
            print()
        use_color = sys.stdout.isatty()
        color = {"high": R, "medium": Y, "low": C} if use_color else {"high": "", "medium": "", "low": ""}
        reset = X if use_color else ""
        if not findings:
            print("  ✓ no issues found")
        for f in findings:
            print(f"  {color[f.severity]}{f.severity.upper():6}{reset} [stage {f.stage}] {f.rule}: {f.message}")

    return 1 if any(f.severity == "high" for f in findings) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
