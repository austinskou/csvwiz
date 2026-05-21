"""Core CSV processing operations for csvwiz."""

import csv
import io
import sys
from typing import Any, Iterator


def read_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    """Read a CSV file and return (headers, rows)."""
    opener = open(path, newline="", encoding="utf-8") if path != "-" else io.TextIOWrapper(sys.stdin.buffer, newline="")
    with opener as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    return list(headers), rows


def write_csv(
    headers: list[str],
    rows: list[dict[str, str]],
    path: str = "-",
    delimiter: str = ",",
) -> None:
    """Write rows to a CSV file or stdout."""
    out = open(path, "w", newline="", encoding="utf-8") if path != "-" else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=headers, delimiter=delimiter, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path != "-":
            out.close()


def filter_rows(
    rows: list[dict[str, str]],
    column: str,
    operator: str,
    value: str,
) -> list[dict[str, str]]:
    """Filter rows by column value using a comparison operator.

    Supported operators: eq, ne, contains, gt, lt, gte, lte, startswith, endswith
    Numeric comparisons (gt, lt, gte, lte) fall back to string comparison if
    values can't be parsed as floats.
    """
    results = []
    for row in rows:
        cell = row.get(column, "")
        match operator:
            case "eq":
                keep = cell == value
            case "ne":
                keep = cell != value
            case "contains":
                keep = value.lower() in cell.lower()
            case "startswith":
                keep = cell.lower().startswith(value.lower())
            case "endswith":
                keep = cell.lower().endswith(value.lower())
            case "gt" | "lt" | "gte" | "lte":
                try:
                    a, b = float(cell), float(value)
                except ValueError:
                    a, b = cell, value  # type: ignore[assignment]
                match operator:
                    case "gt":
                        keep = a > b
                    case "lt":
                        keep = a < b
                    case "gte":
                        keep = a >= b
                    case "lte":
                        keep = a <= b
                    case _:
                        keep = False
            case _:
                raise ValueError(f"Unknown operator '{operator}'. "
                                 "Use: eq, ne, contains, gt, lt, gte, lte, startswith, endswith")
        if keep:
            results.append(row)
    return results


def select_columns(
    rows: list[dict[str, str]],
    columns: list[str],
) -> tuple[list[str], list[dict[str, str]]]:
    """Return only the specified columns from each row."""
    return columns, [{col: row.get(col, "") for col in columns} for row in rows]


def sort_rows(
    rows: list[dict[str, str]],
    column: str,
    descending: bool = False,
    numeric: bool = False,
) -> list[dict[str, str]]:
    """Sort rows by a column value."""
    def key(row: dict[str, str]) -> Any:
        val = row.get(column, "")
        if numeric:
            try:
                return float(val)
            except ValueError:
                return float("-inf") if not descending else float("inf")
        return val.lower()

    return sorted(rows, key=key, reverse=descending)


def summarize(
    headers: list[str],
    rows: list[dict[str, str]],
    column: str | None = None,
) -> dict[str, Any]:
    """Summarize the dataset or a specific numeric column."""
    summary: dict[str, Any] = {
        "total_rows": len(rows),
        "total_columns": len(headers),
        "columns": headers,
    }

    if column:
        values = []
        missing = 0
        for row in rows:
            raw = row.get(column, "").strip()
            if raw == "":
                missing += 1
                continue
            try:
                values.append(float(raw))
            except ValueError:
                missing += 1

        if values:
            summary["column"] = column
            summary["count"] = len(values)
            summary["missing"] = missing
            summary["min"] = min(values)
            summary["max"] = max(values)
            summary["sum"] = sum(values)
            summary["mean"] = sum(values) / len(values)
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            mid = n // 2
            summary["median"] = (
                sorted_vals[mid] if n % 2 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
            )
        else:
            summary["column"] = column
            summary["count"] = 0
            summary["missing"] = missing
            summary["note"] = "No numeric values found in this column."

    return summary


def dedupe_rows(
    rows: list[dict[str, str]],
    columns: list[str] | None = None,
) -> tuple[list[dict[str, str]], int]:
    """Remove duplicate rows, optionally keyed on specific columns.

    Returns (deduplicated_rows, number_of_duplicates_removed).
    """
    seen: set[tuple[str, ...]] = set()
    unique: list[dict[str, str]] = []
    dupes = 0
    for row in rows:
        key_cols = columns if columns else list(row.keys())
        key = tuple(row.get(col, "") for col in key_cols)
        if key in seen:
            dupes += 1
        else:
            seen.add(key)
            unique.append(row)
    return unique, dupes


def rename_column(
    headers: list[str],
    rows: list[dict[str, str]],
    old_name: str,
    new_name: str,
) -> tuple[list[str], list[dict[str, str]]]:
    """Rename a column in headers and all rows."""
    if old_name not in headers:
        raise ValueError(f"Column '{old_name}' not found. Available: {headers}")
    new_headers = [new_name if h == old_name else h for h in headers]
    new_rows = [
        {(new_name if k == old_name else k): v for k, v in row.items()}
        for row in rows
    ]
    return new_headers, new_rows
