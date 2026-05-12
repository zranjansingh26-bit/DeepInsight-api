"""Tests for the file parser engine."""

import io
import pandas as pd
import pytest

from engines.file_parser import parse_bytes, get_file_extension


class TestGetFileExtension:
    """Tests for file extension extraction."""

    def test_csv(self):
        assert get_file_extension("data.csv") == "csv"

    def test_xlsx(self):
        assert get_file_extension("report.xlsx") == "xlsx"

    def test_json(self):
        assert get_file_extension("data.json") == "json"

    def test_unsupported(self):
        with pytest.raises(ValueError, match="Unsupported"):
            get_file_extension("image.png")

    def test_no_extension(self):
        with pytest.raises(ValueError, match="Invalid"):
            get_file_extension("noextension")

    def test_empty(self):
        with pytest.raises(ValueError):
            get_file_extension("")


class TestParseBytes:
    """Tests for parse_bytes function."""

    def test_csv_parsing(self, csv_bytes):
        """Should parse CSV bytes into a DataFrame."""
        df = parse_bytes(csv_bytes, "csv")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert len(df.columns) > 0

    def test_json_parsing(self, sample_df):
        """Should parse JSON bytes into a DataFrame."""
        json_bytes = sample_df.to_json().encode("utf-8")
        df = parse_bytes(json_bytes, "json")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_df)

    def test_unsupported_extension(self):
        """Should raise ValueError for unsupported type."""
        with pytest.raises(ValueError, match="Unsupported"):
            parse_bytes(b"data", "txt")
