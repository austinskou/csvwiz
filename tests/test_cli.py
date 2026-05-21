"""Tests for csvwiz CLI changes: --delimiter support for the head subcommand."""

import sys
from unittest.mock import MagicMock, call, patch

import pytest

from csvwiz.cli import build_parser


# ── build_parser: head --delimiter argument ───────────────────────────────────


class TestBuildParserHeadDelimiter:
    """Tests for the --delimiter argument added to the head subcommand."""

    def test_head_accepts_delimiter_argument(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--delimiter", ";"])
        assert args.delimiter == ";"

    def test_head_delimiter_default_is_comma(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv"])
        assert args.delimiter == ","

    def test_head_delimiter_tab_character(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--delimiter", "\t"])
        assert args.delimiter == "\t"

    def test_head_delimiter_pipe_character(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--delimiter", "|"])
        assert args.delimiter == "|"

    def test_head_delimiter_semicolon(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--delimiter", ";"])
        assert args.delimiter == ";"

    def test_head_delimiter_space(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--delimiter", " "])
        assert args.delimiter == " "

    def test_head_delimiter_coexists_with_n_argument(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--n", "5", "--delimiter", "|"])
        assert args.n == 5
        assert args.delimiter == "|"

    def test_head_delimiter_default_when_n_is_set(self):
        """Delimiter should default to comma even when --n is explicitly provided."""
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--n", "20"])
        assert args.delimiter == ","

    def test_head_stores_file_alongside_delimiter(self):
        parser = build_parser()
        args = parser.parse_args(["head", "myfile.csv", "--delimiter", ";"])
        assert args.file == "myfile.csv"
        assert args.delimiter == ";"

    def test_head_command_name_is_head(self):
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--delimiter", "|"])
        assert args.command == "head"

    def test_summary_subcommand_does_not_have_delimiter(self):
        """summary command doesn't have --delimiter; getattr fallback is used in main()."""
        parser = build_parser()
        args = parser.parse_args(["summary", "data.csv"])
        assert not hasattr(args, "delimiter")

    def test_head_delimiter_single_char_any_value(self):
        """--delimiter accepts any string value, not restricted to single chars."""
        parser = build_parser()
        args = parser.parse_args(["head", "data.csv", "--delimiter", "::"])
        assert args.delimiter == "::"


# ── main(): delimiter is forwarded to ops.read_csv ───────────────────────────


class TestMainPassesDelimiterToReadCsv:
    """Tests that main() passes the delimiter argument to ops.read_csv."""

    def _run_main_with_args(self, argv, mock_read_csv_return=None):
        """Helper: run main() with patched sys.argv and ops.read_csv."""
        if mock_read_csv_return is None:
            mock_read_csv_return = (["col1"], [{"col1": "val"}])

        with (
            patch("sys.argv", argv),
            patch("csvwiz.cli.ops.read_csv", return_value=mock_read_csv_return) as mock_read,
            patch("csvwiz.cli.fmt.print_table"),
        ):
            from csvwiz.cli import main
            main()
            return mock_read

    def test_head_passes_default_delimiter_to_read_csv(self):
        mock_read = self._run_main_with_args(["csvwiz", "head", "data.csv"])
        mock_read.assert_called_once_with("data.csv", delimiter=",")

    def test_head_passes_custom_delimiter_to_read_csv(self):
        mock_read = self._run_main_with_args(["csvwiz", "head", "data.csv", "--delimiter", ";"])
        mock_read.assert_called_once_with("data.csv", delimiter=";")

    def test_head_passes_tab_delimiter_to_read_csv(self):
        mock_read = self._run_main_with_args(["csvwiz", "head", "data.csv", "--delimiter", "\t"])
        mock_read.assert_called_once_with("data.csv", delimiter="\t")

    def test_head_passes_pipe_delimiter_to_read_csv(self):
        mock_read = self._run_main_with_args(["csvwiz", "head", "data.csv", "--delimiter", "|"])
        mock_read.assert_called_once_with("data.csv", delimiter="|")

    def test_summary_uses_getattr_fallback_comma(self):
        """Commands without --delimiter use getattr fallback of ',' in main()."""
        headers = ["name", "age"]
        rows = [{"name": "Alice", "age": "30"}]
        with (
            patch("sys.argv", ["csvwiz", "summary", "data.csv"]),
            patch("csvwiz.cli.ops.read_csv", return_value=(headers, rows)) as mock_read,
            patch("csvwiz.cli.ops.summarize", return_value={"total_rows": 1, "total_columns": 2, "columns": headers}),
            patch("csvwiz.cli.fmt.print_summary"),
        ):
            from csvwiz.cli import main
            main()
            mock_read.assert_called_once_with("data.csv", delimiter=",")

    def test_file_not_found_exits_with_code_1(self):
        with (
            patch("sys.argv", ["csvwiz", "head", "missing.csv"]),
            patch("csvwiz.cli.ops.read_csv", side_effect=FileNotFoundError),
            patch("csvwiz.cli.fmt.print_error"),
            pytest.raises(SystemExit) as exc_info,
        ):
            from csvwiz.cli import main
            main()
        assert exc_info.value.code == 1

    def test_file_not_found_prints_error_message(self):
        with (
            patch("sys.argv", ["csvwiz", "head", "missing.csv"]),
            patch("csvwiz.cli.ops.read_csv", side_effect=FileNotFoundError),
            patch("csvwiz.cli.fmt.print_error") as mock_err,
            pytest.raises(SystemExit),
        ):
            from csvwiz.cli import main
            main()
        mock_err.assert_called_once()
        assert "missing.csv" in mock_err.call_args[0][0]

    def test_generic_exception_exits_with_code_1(self):
        with (
            patch("sys.argv", ["csvwiz", "head", "bad.csv"]),
            patch("csvwiz.cli.ops.read_csv", side_effect=Exception("parse error")),
            patch("csvwiz.cli.fmt.print_error"),
            pytest.raises(SystemExit) as exc_info,
        ):
            from csvwiz.cli import main
            main()
        assert exc_info.value.code == 1

    def test_generic_exception_prints_error_message(self):
        with (
            patch("sys.argv", ["csvwiz", "head", "bad.csv"]),
            patch("csvwiz.cli.ops.read_csv", side_effect=Exception("parse error")),
            patch("csvwiz.cli.fmt.print_error") as mock_err,
            pytest.raises(SystemExit),
        ):
            from csvwiz.cli import main
            main()
        mock_err.assert_called_once()
        assert "parse error" in mock_err.call_args[0][0]

    def test_head_delimiter_forwarded_as_keyword_argument(self):
        """Ensure delimiter is passed as a keyword arg, not positional."""
        headers = ["a"]
        rows = [{"a": "1"}]
        with (
            patch("sys.argv", ["csvwiz", "head", "data.csv", "--delimiter", ";"]),
            patch("csvwiz.cli.ops.read_csv", return_value=(headers, rows)) as mock_read,
            patch("csvwiz.cli.fmt.print_table"),
        ):
            from csvwiz.cli import main
            main()
            _, kwargs = mock_read.call_args
            assert "delimiter" in kwargs
            assert kwargs["delimiter"] == ";"
