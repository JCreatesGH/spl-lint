import sys
from .rules import lint
from .format import format_spl

R, Y, C, X = "\033[31m", "\033[33m", "\033[36m", "\033[0m"


def main(argv=None):
    argv = argv or sys.argv[1:]
    spl = " ".join(argv) if argv else sys.stdin.read()
    if not spl.strip():
        print("usage: spllint '<spl search>'"); return 2
    print(format_spl(spl)); print()
    findings = lint(spl)
    color = {"high": R, "medium": Y, "low": C}
    for f in findings:
        print(f"  {color[f.severity]}{f.severity.upper():6}{X} [stage {f.stage}] {f.rule}: {f.message}")
    high = sum(1 for f in findings if f.severity == "high")
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
