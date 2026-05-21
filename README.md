# csvwiz 🧙

**Transform, filter, and summarize CSV files from the command line.**

csvwiz is a lightweight Python CLI tool that makes common CSV operations fast and scriptable — no spreadsheet required.

---

## Features

| Command   | What it does                                      |
|-----------|---------------------------------------------------|
| `head`    | Preview the first N rows as a formatted table     |
| `summary` | Dataset overview + optional numeric column stats  |
| `filter`  | Keep rows matching a column condition             |
| `select`  | Keep only specified columns                       |
| `sort`    | Sort rows by any column (string or numeric)       |
| `dedupe`  | Remove duplicate rows                             |
| `rename`  | Rename a column header                            |

---

## Requirements

- Python 3.10 or higher
- No third-party dependencies

---

## Installation

### From source (recommended for development)

```bash
git clone https://github.com/<your-username>/csvwiz.git
cd csvwiz
pip install -e .
```

After installing, the `csvwiz` command will be available in your shell.

### Without installing

You can also run csvwiz directly:

```bash
python -m csvwiz.cli <command> [options]
```

---

## Usage

### `head` — Preview rows

```bash
csvwiz head data.csv
csvwiz head data.csv --n 20
```

### `summary` — Dataset overview

```bash
csvwiz summary data.csv
csvwiz summary data.csv --column price
```

### `filter` — Filter rows

```bash
# Keep rows where status equals "active"
csvwiz filter data.csv --col status --op eq --val active

# Keep rows where score > 80
csvwiz filter data.csv --col score --op gt --val 80

# Keep rows where name contains "smith"
csvwiz filter data.csv --col name --op contains --val smith
```

**Available operators:**

| Operator     | Meaning                        |
|--------------|--------------------------------|
| `eq`         | Equal to                       |
| `ne`         | Not equal to                   |
| `contains`   | Contains substring (case-insensitive) |
| `startswith` | Starts with (case-insensitive) |
| `endswith`   | Ends with (case-insensitive)   |
| `gt`         | Greater than                   |
| `lt`         | Less than                      |
| `gte`        | Greater than or equal to       |
| `lte`        | Less than or equal to          |

### `select` — Keep specific columns

```bash
csvwiz select data.csv --columns name,email,score
```

### `sort` — Sort rows

```bash
# Sort by name (alphabetical)
csvwiz sort data.csv --col name

# Sort by price descending (numeric)
csvwiz sort data.csv --col price --numeric --desc
```

### `dedupe` — Remove duplicates

```bash
# Remove fully duplicate rows
csvwiz dedupe data.csv

# Remove rows with duplicate emails (keep first occurrence)
csvwiz dedupe data.csv --columns email
```

### `rename` — Rename a column

```bash
csvwiz rename data.csv --from "First Name" --to first_name
```

---

## Composing commands

All commands read from a file or stdin (`-`) and write to stdout by default, so you can pipe them together:

```bash
# Filter active users, keep only name + email, sort by name
csvwiz filter data.csv --col status --op eq --val active \
  | csvwiz select - --columns name,email \
  | csvwiz sort - --col name \
  > result.csv
```

---

## Output options

Most commands support `--out FILE` to write directly to a file:

```bash
csvwiz filter data.csv --col city --op eq --val Boston --out boston.csv
```

And `--delimiter` to change the output separator:

```bash
csvwiz select data.csv --columns name,age --delimiter $'\t' --out data.tsv
```

---

## Running tests

```bash
python -m pytest tests/ -v
```

---

## Project structure

```
csvwiz/
├── csvwiz/
│   ├── __init__.py      # Version info
│   ├── cli.py           # CLI entry point (argparse)
│   ├── operations.py    # Core data operations
│   └── formatter.py     # Output formatting helpers
├── tests/
│   └── test_operations.py
├── pyproject.toml
└── README.md
```

---

## License

MIT
