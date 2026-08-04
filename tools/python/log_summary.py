#!/usr/bin/env python3

"""
log_summary.py

Command-line log summarization utility.

Reads a log file, reports its size, counts common severity markers, surfaces repeated message patterns, and optionally filters by one or more keywords.

Examples:
  python log_summary.py logs/app.log
  python log_summary.py logs/app.log -k database dependency
  python log_summary.py logs/app.log -t 10
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

SEVERITIES = ["CRITICAL", "ERROR", "WARN", "WARNING", "INFO", "DEBUG"]

EXIT_WARNING = 1  # One or more warning markers found.
# argparse uses exit code 2 for malformed command-line usage.
EXIT_INPUT_ERROR = 3  # Invalid input or execution validation failure.
EXIT_NO_MATCHES = 4  # No lines matched the selected keyword filters.
EXIT_HIGH_SEVERITY = 5  # One or more CRITICAL or ERROR markers found.


@dataclass
class LogSummary:
    path: Path
    file_size: int
    total_lines: int
    matching_lines: int
    keywords: list[str] | None
    unmatched_keywords: list[str]
    severity_counts: dict[str, int]
    high_severity_patterns: list[tuple[str, int]]
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
        dest="keywords",
        nargs="+",
        help=(
            "Optional case-insensitive keyword filters. "
            "Lines matching any supplied keyword are included."
        ),
    )

    parser.add_argument(
        "-t",
        "--top",
        type=int,
        default=5,
        help="Number of repeated patterns to show. Default: 5",
    )

    return parser.parse_args()


def format_file_size(size_bytes: int) -> str:
    size = float(size_bytes)
    units = ("B", "K", "M", "G", "T")

    for unit in units[:-1]:
        if size < 1024:
            if unit == "B":
                return f"{int(size)}{unit}"

            return f"{size:.2f}{unit}"

        size /= 1024

    return f"{size:.2f}{units[-1]}"


def normalize_line(line: str) -> str:
    stripped = line.strip()

    stripped = re.sub(
        r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
        r"(?:[.,]\d+)?(?:Z|[+-]\d{2}:\d{2})?\s*",
        "",
        stripped,
    )
    stripped = re.sub(
        r"\brequest_id=[^\s]+",
        "request_id=<id>",
        stripped,
    )
    stripped = re.sub(
        r"\btrace_id=[^\s]+",
        "trace_id=<id>",
        stripped,
    )

    return stripped


def line_matches_keyword(line: str, keyword: str) -> bool:
    return keyword.lower() in line.lower()


def line_matches_keywords(
    line: str,
    keywords: list[str] | None,
) -> bool:
    if not keywords:
        return True

    return any(
        line_matches_keyword(line, keyword)
        for keyword in keywords
    )


def find_unmatched_keywords(
    lines: list[str],
    keywords: list[str] | None,
) -> list[str]:
    if not keywords or len(keywords) < 2:
        return []

    return [
        keyword
        for keyword in keywords
        if not any(
            line_matches_keyword(line, keyword)
            for line in lines
        )
    ]


def line_has_severity(line: str, severity: str) -> bool:
    return (
        re.search(
            rf"\b{re.escape(severity)}\b",
            line.upper(),
        )
        is not None
    )


def count_severities(lines: list[str]) -> dict[str, int]:
    counts = {severity: 0 for severity in SEVERITIES}

    for line in lines:
        for severity in SEVERITIES:
            if line_has_severity(line, severity):
                counts[severity] += 1

    return counts


def summarize_log(
    path: Path,
    keywords: list[str] | None,
    top: int,
) -> LogSummary:
    file_size = path.stat().st_size

    with path.open("r", encoding="utf-8", errors="replace") as file:
        lines = file.readlines()

    total_lines = len(lines)

    filtered_lines = [
        line.rstrip("\n")
        for line in lines
        if line_matches_keywords(line, keywords)
    ]

    unmatched_keywords = find_unmatched_keywords(
        lines=lines,
        keywords=keywords,
    )

    severity_counts = count_severities(filtered_lines)

    high_severity_counter = Counter(
        normalize_line(line)
        for line in filtered_lines
        if (
            line_has_severity(line, "ERROR")
            or line_has_severity(line, "CRITICAL")
        )
        and normalize_line(line)
    )

    high_severity_patterns = high_severity_counter.most_common(top)

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
        file_size=file_size,
        total_lines=total_lines,
        matching_lines=len(filtered_lines),
        keywords=keywords,
        unmatched_keywords=unmatched_keywords,
        severity_counts=severity_counts,
        high_severity_patterns=high_severity_patterns,
        top_repeated_lines=top_repeated_lines,
        first_match=first_match,
        last_match=last_match,
    )


def print_summary(summary: LogSummary) -> None:
    print("\n--- Log Summary ---")
    print(f"Log file: {summary.path.as_posix()}")
    print(f"File size: {format_file_size(summary.file_size)}")
    print(f"Total lines scanned: {summary.total_lines}")

    if summary.keywords:
        print("Keyword filters: " + ", ".join(summary.keywords))

        if summary.unmatched_keywords:
            print(
                "No matches for: "
                + ", ".join(summary.unmatched_keywords)
            )

        print(f"Matching lines: {summary.matching_lines}")
    else:
        print("Keyword filters: not provided")

    print("\n--- Severity Counts ---")

    for severity in SEVERITIES:
        print(f"{severity}: {summary.severity_counts[severity]}")

    print("\n--- High-Severity Patterns ---")

    if summary.high_severity_patterns:
        for line, count in summary.high_severity_patterns:
            print(f"{count}x {line}")
    else:
        print("No ERROR or CRITICAL patterns found.")

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
        return EXIT_INPUT_ERROR

    if args.top < 1:
        print(
            "Error: --top must be greater than 0",
            file=sys.stderr,
        )
        return EXIT_INPUT_ERROR

    summary = summarize_log(
        path=args.path,
        keywords=args.keywords,
        top=args.top,
    )

    print_summary(summary)

    if summary.matching_lines == 0:
        return EXIT_NO_MATCHES

    if (
        summary.severity_counts["CRITICAL"] > 0
        or summary.severity_counts["ERROR"] > 0
    ):
        return EXIT_HIGH_SEVERITY

    if (
        summary.severity_counts["WARN"] > 0
        or summary.severity_counts["WARNING"] > 0
    ):
        return EXIT_WARNING

    return 0


if __name__ == "__main__":
    sys.exit(main())