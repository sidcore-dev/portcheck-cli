"""Command-line entry point for portcheck-cli."""
from __future__ import annotations

import argparse
import sys

from .core import DEFAULT_TIMEOUT, check_port, parse_target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portcheck-cli",
        description=(
            "Check whether a single host:port is accepting TCP connections. "
            "Checks one target at a time by design — not a network scanner."
        ),
    )
    parser.add_argument("target", help="Target to check, in host:port form (e.g. example.com:443)")
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"Connection timeout in seconds (default: {DEFAULT_TIMEOUT})"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        host, port = parse_target(args.target)
    except ValueError as exc:
        print(f"portcheck-cli: error: {exc}", file=sys.stderr)
        return 2

    result = check_port(host, port, timeout=args.timeout)

    if result.status == "open":
        print(result.message)
        return 0
    if result.status == "closed":
        print(result.message)
        return 1

    print(f"portcheck-cli: error: {result.message}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
