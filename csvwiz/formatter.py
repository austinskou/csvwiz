"""Output formatting helpers for csvwiz."""

from typing import Any


def format_number(val: float) -> str:
    """Format a float cleanly — integer if whole, else 4 decimal places."""
    return str(int(val)) if val == int(val) else f"{val:.4f}"


def print_table(headers: list[str], rows: list[dict[str, str]], max_rows: int = 0) -> None:
    """Print rows as a pretty ASCII table."""
    if not headers:
        print("(no columns)")
        return

    display_rows = rows[:max_rows] if max_rows else rows

    # Compute column widths
    widths = {h: len(h) for h in headers}
    for row in display_rows:
        for h in headers:
            widths[h] = max(widths[h], len(row.get(h, "")))

    sep = "+" + "+".join("-" * (widths[h] + 2) for h in headers) + "+"
    header_row = "|" + "|".join(f" {h:<{widths[h]}} " for h in headers) + "|"

    print(sep)
    print(header_row)
    print(sep)
    for row in display_rows:
        print("|" + "|".join(f" {row.get(h, ''):<{widths[h]}} " for h in headers) + "|")
    print(sep)

    if max_rows and len(rows) > max_rows:
        print(f"  … {len(rows) - max_rows} more rows (use --head N to show more)")


def print_summary(summary: dict[str, Any]) -> None:
    """Print a dataset or column summary in a readable format."""
    print(f"\n{'─' * 40}")
    print(f"  📊 csvwiz Summary")
    print(f"{'─' * 40}")
    print(f"  Rows          : {summary['total_rows']}")
    print(f"  Columns       : {summary['total_columns']}")
    print(f"  Column names  : {', '.join(summary['columns'])}")

    if "column" in summary:
        print(f"\n  Column        : {summary['column']}")
        print(f"  Count (num)   : {summary.get('count', 0)}")
        print(f"  Missing       : {summary.get('missing', 0)}")
        if summary.get("count", 0) > 0:
            print(f"  Min           : {format_number(summary['min'])}")
            print(f"  Max           : {format_number(summary['max'])}")
            print(f"  Sum           : {format_number(summary['sum'])}")
            print(f"  Mean          : {format_number(summary['mean'])}")
            print(f"  Median        : {format_number(summary['median'])}")
        elif "note" in summary:
            print(f"  Note          : {summary['note']}")

    print(f"{'─' * 40}\n")


def print_info(msg: str) -> None:
    print(f"ℹ  {msg}")


def print_success(msg: str) -> None:
    print(f"✔  {msg}")


def print_error(msg: str) -> None:
    print(f"✘  {msg}")
