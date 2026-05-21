"""Tests for csvwiz core operations."""

import pytest
from csvwiz.operations import (
    filter_rows,
    select_columns,
    sort_rows,
    summarize,
    dedupe_rows,
    rename_column,
)

HEADERS = ["name", "age", "city", "score"]
ROWS = [
    {"name": "Alice", "age": "30", "city": "Boston",   "score": "88.5"},
    {"name": "Bob",   "age": "25", "city": "New York",  "score": "72"},
    {"name": "Carol", "age": "35", "city": "Boston",    "score": "95"},
    {"name": "Dave",  "age": "25", "city": "Chicago",   "score": ""},
    {"name": "Eve",   "age": "30", "city": "New York",  "score": "88.5"},
]


# ── filter_rows ──────────────────────────────────────────────────────────────

class TestFilterRows:
    def test_eq(self):
        result = filter_rows(ROWS, "city", "eq", "Boston")
        assert len(result) == 2
        assert all(r["city"] == "Boston" for r in result)

    def test_ne(self):
        result = filter_rows(ROWS, "city", "ne", "Boston")
        assert len(result) == 3

    def test_contains(self):
        result = filter_rows(ROWS, "city", "contains", "york")
        assert len(result) == 2

    def test_startswith(self):
        result = filter_rows(ROWS, "name", "startswith", "a")
        assert result[0]["name"] == "Alice"

    def test_endswith(self):
        result = filter_rows(ROWS, "name", "endswith", "e")
        names = {r["name"] for r in result}
        assert names == {"Alice", "Dave", "Eve"}

    def test_gt_numeric(self):
        result = filter_rows(ROWS, "age", "gt", "28")
        assert all(int(r["age"]) > 28 for r in result)

    def test_lt_numeric(self):
        result = filter_rows(ROWS, "age", "lt", "30")
        assert all(int(r["age"]) < 30 for r in result)

    def test_gte_numeric(self):
        result = filter_rows(ROWS, "age", "gte", "30")
        assert all(int(r["age"]) >= 30 for r in result)

    def test_lte_numeric(self):
        result = filter_rows(ROWS, "age", "lte", "25")
        assert all(int(r["age"]) <= 25 for r in result)

    def test_unknown_operator(self):
        with pytest.raises(ValueError):
            filter_rows(ROWS, "name", "regex", ".*")

    def test_missing_column_returns_no_match(self):
        result = filter_rows(ROWS, "nonexistent", "eq", "x")
        assert result == []


# ── select_columns ───────────────────────────────────────────────────────────

class TestSelectColumns:
    def test_basic_select(self):
        headers, rows = select_columns(ROWS, ["name", "city"])
        assert headers == ["name", "city"]
        assert all(set(r.keys()) == {"name", "city"} for r in rows)

    def test_single_column(self):
        headers, rows = select_columns(ROWS, ["name"])
        assert headers == ["name"]

    def test_preserves_row_count(self):
        _, rows = select_columns(ROWS, ["name"])
        assert len(rows) == len(ROWS)


# ── sort_rows ────────────────────────────────────────────────────────────────

class TestSortRows:
    def test_sort_string_asc(self):
        result = sort_rows(ROWS, "name")
        names = [r["name"] for r in result]
        assert names == sorted(names, key=str.lower)

    def test_sort_string_desc(self):
        result = sort_rows(ROWS, "name", descending=True)
        names = [r["name"] for r in result]
        assert names == sorted(names, key=str.lower, reverse=True)

    def test_sort_numeric_asc(self):
        result = sort_rows(ROWS, "age", numeric=True)
        ages = [int(r["age"]) for r in result]
        assert ages == sorted(ages)

    def test_sort_numeric_desc(self):
        result = sort_rows(ROWS, "age", numeric=True, descending=True)
        ages = [int(r["age"]) for r in result]
        assert ages == sorted(ages, reverse=True)


# ── summarize ────────────────────────────────────────────────────────────────

class TestSummarize:
    def test_basic_summary(self):
        s = summarize(HEADERS, ROWS)
        assert s["total_rows"] == 5
        assert s["total_columns"] == 4
        assert s["columns"] == HEADERS

    def test_column_summary(self):
        s = summarize(HEADERS, ROWS, column="score")
        assert s["count"] == 4   # Dave has empty score
        assert s["missing"] == 1
        assert s["min"] == 72.0
        assert s["max"] == 95.0

    def test_column_mean(self):
        s = summarize(HEADERS, ROWS, column="score")
        expected_mean = (88.5 + 72 + 95 + 88.5) / 4
        assert abs(s["mean"] - expected_mean) < 1e-9

    def test_non_numeric_column(self):
        s = summarize(HEADERS, ROWS, column="name")
        assert s["count"] == 0
        assert "note" in s


# ── dedupe_rows ──────────────────────────────────────────────────────────────

class TestDedupeRows:
    def test_no_dupes(self):
        unique, dupes = dedupe_rows(ROWS)
        assert dupes == 0
        assert len(unique) == len(ROWS)

    def test_dedupe_all_columns(self):
        duped = ROWS + [ROWS[0]]
        unique, dupes = dedupe_rows(duped)
        assert dupes == 1
        assert len(unique) == len(ROWS)

    def test_dedupe_by_column(self):
        unique, dupes = dedupe_rows(ROWS, columns=["city"])
        assert len(unique) == 3  # Boston, New York, Chicago
        assert dupes == 2

    def test_dedupe_by_age(self):
        unique, dupes = dedupe_rows(ROWS, columns=["age"])
        assert len(unique) == 3  # 30, 25, 35
        assert dupes == 2


# ── rename_column ────────────────────────────────────────────────────────────

class TestRenameColumn:
    def test_basic_rename(self):
        headers, rows = rename_column(HEADERS, ROWS, "name", "full_name")
        assert "full_name" in headers
        assert "name" not in headers
        assert all("full_name" in r for r in rows)
        assert all("name" not in r for r in rows)

    def test_values_preserved(self):
        _, rows = rename_column(HEADERS, ROWS, "name", "full_name")
        original_names = [r["name"] for r in ROWS]
        new_names = [r["full_name"] for r in rows]
        assert original_names == new_names

    def test_unknown_column_raises(self):
        with pytest.raises(ValueError):
            rename_column(HEADERS, ROWS, "nonexistent", "new_name")
