#!/usr/bin/env python3

"""
log_summary.py

Command-line log summarization utility.

Reads a log file, counts common severity markers, surfaces repeated messages or repeated raw lines, and optionally filters by keyword so support can identify likely error patterns faster than manual scanning.

Examples:
  python log_summary.py logs/app.log
  python log_summary.py logs/app.log --keyword dependency
  python log_summary.py logs/app.log --top 10
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

SEVERITIES = ["CRITICAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG"]


@dataclass
class LogSummary:
    path: Path
    total_lines: int
    matching_lines: int
    keyword: str | None
    severity_counts: dict[str, int]
    top_repeated_lines: list[tuple[str, int]]
    first_match: str | None
    last_match: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize severity markers and repeated patterns in a log file."
    )

    parser.add_argument(
        "path",
        type=Path,
        help="Path to the log file to summarize.",
    )

    parser.add_argument(
        "-k",
        "--keyword",
        help="Optional keyword filter. Matching is case-insensitive.",
    )

    parser.add_argument(
        "-t",
        "--top",
        type=int,
        default=5,
        help="Number of repeated lines to show. Default: 5",
    )

    return parser.parse_args()


def normalize_line(line: str) -> str:
    """
    Normalize a log line enough to group obvious repeats without pretending to fully parse every log format.
    """
    stripped = line.strip()

    stripped = re.sub(
        r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:,\d+)?\s*",
        "",
        stripped,
    )
    stripped = re.sub(r"\brequest_id=[^\s]+", "request_id=<id>", stripped)
    stripped = re.sub(r"\btrace_id=[^\s]+", "trace_id=<id>", stripped)

    return stripped


def line_matches_keyword(line: str, keyword: str | None) -> bool:
    if keyword is None:
        return True

    return keyword.lower() in line.lower()


def count_severities(lines: list[str]) -> dict[str, int]:
    counts = {severity: 0 for severity in SEVERITIES}

    for line in lines:
        upper_line = line.upper()

        for severity in SEVERITIES:
            if re.search(rf"\b{re.escape(severity)}\b", upper_line):
                counts[severity] += 1

    return counts


def summarize_log(path: Path, keyword: str | None, top: int) -> LogSummary:
    with path.open("r", encoding="utf-8", errors="replace") as file:
        lines = file.readlines()

    total_lines = len(lines)

    filtered_lines = [
        line.rstrip("\n")
        for line in lines
        if line_matches_keyword(line, keyword)
    ]

    severity_counts = count_severities(filtered_lines)

    normalized_counter = Counter(
        normalize_line(line)
        for line in filtered_lines
        if normalize_line(line)
    )

    top_repeated_lines = [
        (line, count)
        for line, count in normalized_counter.most_common(top)
        if count > 1
    ]

    first_match = filtered_lines[0] if filtered_lines else None
    last_match = filtered_lines[-1] if filtered_lines else None

    return LogSummary(
        path=path,
        total_lines=total_lines,
        matching_lines=len(filtered_lines),
        keyword=keyword,
        severity_counts=severity_counts,
        top_repeated_lines=top_repeated_lines,
        first_match=first_match,
        last_match=last_match,
    )


def print_summary(summary: LogSummary) -> None:
    print("\n--- Log Summary ---")
    print(f"Log file: {summary.path.as_posix()}")
    print(f"Total lines scanned: {summary.total_lines}")

    if summary.keyword:
        print(f"Keyword filter: {summary.keyword}")
        print(f"Matching lines: {summary.matching_lines}")
    else:
        print("Keyword filter: not provided")
        print(f"Matching lines: {summary.matching_lines}")

    print("\n--- Severity Counts ---")

    for severity in SEVERITIES:
        print(f"{severity}: {summary.severity_counts[severity]}")

    print("\n--- Repeated Message Patterns ---")

    if summary.top_repeated_lines:
        for line, count in summary.top_repeated_lines:
            print(f"{count}x {line}")
    else:
        print("No repeated lines found above 1 occurrence.")

    print("\n--- First / Last Matching Line ---")

    if summary.first_match:
        print(f"First: {summary.first_match}")
        print(f"Last:  {summary.last_match}")
    else:
        print("No matching lines found.")


def main() -> int:
    args = parse_args()

    if not args.path.is_file():
        print(
            f"Error: log file does not exist or is not a regular file: {args.path}",
            file=sys.stderr,
        )
        return 1

    if args.top < 1:
        print("Error: --top must be greater than 0", file=sys.stderr)
        return 1

    summary = summarize_log(
        path=args.path,
        keyword=args.keyword,
        top=args.top,
    )

    print_summary(summary)

    if summary.matching_lines == 0:
        return 1

    if (
        summary.severity_counts["CRITICAL"] > 0
        or summary.severity_counts["ERROR"] > 0
    ):
        return 2

    if (
        summary.severity_counts["WARN"] > 0
        or summary.severity_counts["WARNING"] > 0
    ):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())