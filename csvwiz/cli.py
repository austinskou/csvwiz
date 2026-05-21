#!/usr/bin/env python3
"""csvwiz – transform, filter, and summarize CSV files from the command line.

Usage examples:
    csvwiz summary data.csv
    csvwiz summary data.csv --column price
    csvwiz filter data.csv --col status --op eq --val active
    csvwiz select data.csv --columns name,email,age
    csvwiz sort data.csv --col age --numeric --desc
    csvwiz dedupe data.csv
    csvwiz dedupe data.csv --columns email
    csvwiz rename data.csv --from "First Name" --to first_name
    csvwiz head data.csv --n 10
"""

import argparse
import sys

from csvwiz import __version__
from csvwiz import operations as ops
from csvwiz import formatter as fmt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvwiz",
        description="Transform, filter, and summarize CSV files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--version", action="version", version=f"csvwiz {__version__}")

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # ── summary ──────────────────────────────────────────────────────────────
    p_sum = sub.add_parser("summary", help="Show dataset overview and optional column stats.")
    p_sum.add_argument("file", help="CSV file path, or '-' for stdin.")
    p_sum.add_argument("--column", "-c", metavar="COL",
                       help="Also compute numeric stats for this column.")

    # ── filter ───────────────────────────────────────────────────────────────
    p_flt = sub.add_parser("filter", help="Keep rows matching a column condition.")
    p_flt.add_argument("file", help="CSV file path, or '-' for stdin.")
    p_flt.add_argument("--col", required=True, metavar="COL", help="Column name to test.")
    p_flt.add_argument("--op", required=True, metavar="OP",
                       choices=["eq", "ne", "contains", "gt", "lt", "gte", "lte",
                                "startswith", "endswith"],
                       help="Comparison operator.")
    p_flt.add_argument("--val", required=True, metavar="VALUE", help="Value to compare against.")
    p_flt.add_argument("--out", "-o", metavar="FILE", default="-",
                       help="Output file (default: stdout).")
    p_flt.add_argument("--delimiter", metavar="DELIM", default=",",
                       help="Output delimiter (default: comma).")

    # ── select ───────────────────────────────────────────────────────────────
    p_sel = sub.add_parser("select", help="Keep only specified columns.")
    p_sel.add_argument("file", help="CSV file path, or '-' for stdin.")
    p_sel.add_argument("--columns", required=True, metavar="COL1,COL2,...",
                       help="Comma-separated list of columns to keep.")
    p_sel.add_argument("--out", "-o", metavar="FILE", default="-",
                       help="Output file (default: stdout).")
    p_sel.add_argument("--delimiter", metavar="DELIM", default=",",
                       help="Output delimiter (default: comma).")

    # ── sort ─────────────────────────────────────────────────────────────────
    p_srt = sub.add_parser("sort", help="Sort rows by a column.")
    p_srt.add_argument("file", help="CSV file path, or '-' for stdin.")
    p_srt.add_argument("--col", required=True, metavar="COL", help="Column to sort by.")
    p_srt.add_argument("--desc", action="store_true", help="Sort in descending order.")
    p_srt.add_argument("--numeric", "-n", action="store_true",
                       help="Treat column values as numbers.")
    p_srt.add_argument("--out", "-o", metavar="FILE", default="-",
                       help="Output file (default: stdout).")
    p_srt.add_argument("--delimiter", metavar="DELIM", default=",",
                       help="Output delimiter (default: comma).")

    # ── dedupe ───────────────────────────────────────────────────────────────
    p_dd = sub.add_parser("dedupe", help="Remove duplicate rows.")
    p_dd.add_argument("file", help="CSV file path, or '-' for stdin.")
    p_dd.add_argument("--columns", metavar="COL1,COL2,...",
                      help="Columns to use as dedup key (default: all columns).")
    p_dd.add_argument("--out", "-o", metavar="FILE", default="-",
                      help="Output file (default: stdout).")
    p_dd.add_argument("--delimiter", metavar="DELIM", default=",",
                      help="Output delimiter (default: comma).")

    # ── rename ───────────────────────────────────────────────────────────────
    p_ren = sub.add_parser("rename", help="Rename a column.")
    p_ren.add_argument("file", help="CSV file path, or '-' for stdin.")
    p_ren.add_argument("--from", dest="old_name", required=True, metavar="OLD",
                       help="Current column name.")
    p_ren.add_argument("--to", dest="new_name", required=True, metavar="NEW",
                       help="New column name.")
    p_ren.add_argument("--out", "-o", metavar="FILE", default="-",
                       help="Output file (default: stdout).")
    p_ren.add_argument("--delimiter", metavar="DELIM", default=",",
                       help="Output delimiter (default: comma).")

    # ── head ─────────────────────────────────────────────────────────────────
    p_head = sub.add_parser("head", help="Preview the first N rows as a table.")
    p_head.add_argument("file", help="CSV file path, or '-' for stdin.")
    p_head.add_argument("--n", type=int, default=10, metavar="N",
                        help="Number of rows to show (default: 10).")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        headers, rows = ops.read_csv(args.file)
    except FileNotFoundError:
        fmt.print_error(f"File not found: {args.file}")
        sys.exit(1)
    except Exception as e:
        fmt.print_error(f"Could not read file: {e}")
        sys.exit(1)

    try:
        match args.command:

            case "summary":
                summary = ops.summarize(headers, rows, column=args.column)
                fmt.print_summary(summary)

            case "filter":
                filtered = ops.filter_rows(rows, args.col, args.op, args.val)
                fmt.print_info(f"{len(filtered)} of {len(rows)} rows match.")
                ops.write_csv(headers, filtered, args.out, args.delimiter)

            case "select":
                cols = [c.strip() for c in args.columns.split(",")]
                missing = [c for c in cols if c not in headers]
                if missing:
                    fmt.print_error(f"Unknown columns: {missing}. Available: {headers}")
                    sys.exit(1)
                new_headers, new_rows = ops.select_columns(rows, cols)
                ops.write_csv(new_headers, new_rows, args.out, args.delimiter)

            case "sort":
                sorted_rows = ops.sort_rows(rows, args.col,
                                            descending=args.desc,
                                            numeric=args.numeric)
                ops.write_csv(headers, sorted_rows, args.out, args.delimiter)

            case "dedupe":
                key_cols = [c.strip() for c in args.columns.split(",")] if args.columns else None
                unique, dupes = ops.dedupe_rows(rows, key_cols)
                fmt.print_info(f"Removed {dupes} duplicate(s). {len(unique)} rows remain.")
                ops.write_csv(headers, unique, args.out, args.delimiter)

            case "rename":
                new_headers, new_rows = ops.rename_column(
                    headers, rows, args.old_name, args.new_name
                )
                ops.write_csv(new_headers, new_rows, args.out, args.delimiter)
                fmt.print_info(f"Renamed '{args.old_name}' → '{args.new_name}'.")

            case "head":
                fmt.print_table(headers, rows, max_rows=args.n)

    except ValueError as e:
        fmt.print_error(str(e))
        sys.exit(1)
    except BrokenPipeError:
        pass  # e.g. piped to head


if __name__ == "__main__":
    main()
