"""Tests for the quality checker engine."""

import pandas as pd
import pytest

from engines.quality_checker import check_quality, build_column_metadata


class TestCheckQuality:
    """Tests for check_quality function."""

    def test_perfect_quality(self):
        """A DataFrame with no nulls or duplicates should score 100."""
        df = pd.DataFrame({"name": ["A", "B", "C"], "value": [1, 2, 3]})
        result = check_quality(df)
        assert result["quality_score"] == 100
        assert result["row_count"] == 3
        assert result["column_count"] == 2
        assert result["missing_cells"] == 0
        assert result["duplicate_rows"] == 0

    def test_with_nulls(self, sample_df_with_nulls):
        """Quality score should drop with null values."""
        result = check_quality(sample_df_with_nulls)
        assert result["quality_score"] < 100
        assert result["missing_cells"] > 0
        assert result["null_percentage"] > 0

    def test_with_duplicates(self):
        """Duplicate rows should penalize the score."""
        df = pd.DataFrame({
            "a": [1, 1, 2, 2, 3],
            "b": ["x", "x", "y", "y", "z"],
        })
        result = check_quality(df)
        assert result["duplicate_rows"] == 2

    def test_single_row(self):
        """Should handle DataFrames with a single row."""
        df = pd.DataFrame({"a": [1], "b": ["x"]})
        result = check_quality(df)
        assert result["quality_score"] == 100
        assert result["row_count"] == 1

    def test_all_nulls(self):
        """A fully null DataFrame should score 0."""
        df = pd.DataFrame({"a": [None, None], "b": [None, None]})
        result = check_quality(df)
        assert result["quality_score"] == 0
        assert result["null_percentage"] == 100.0


class TestColumnMetadata:
    """Tests for build_column_metadata function."""

    def test_column_count(self, sample_df):
        """Should return metadata for every column."""
        meta = build_column_metadata(sample_df)
        assert len(meta) == len(sample_df.columns)

    def test_metadata_fields(self, sample_df):
        """Each column metadata should have required fields."""
        meta = build_column_metadata(sample_df)
        for col_meta in meta:
            assert "name" in col_meta
            assert "dtype" in col_meta
            assert "null_count" in col_meta
            assert "unique_count" in col_meta
            assert "sample_values" in col_meta