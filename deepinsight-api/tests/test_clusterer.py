"""Tests for the clusterer engine."""

import pytest
import pandas as pd
import numpy as np

from engines.clusterer import run_clustering


class TestRunClustering:
    def test_basic_clustering(self, numeric_only_df):
        result = run_clustering(numeric_only_df)
        assert "error" not in result
        assert result["optimal_k"] >= 2
        assert result["silhouette_score"] > -1
        assert len(result["labels"]) == len(numeric_only_df)
        assert len(result["pca_components"]) == len(numeric_only_df)

    def test_too_few_rows(self):
        df = pd.DataFrame({"a": [1]})
        result = run_clustering(df)
        assert "error" in result

    def test_no_numeric(self):
        df = pd.DataFrame({"a": ["x", "y", "z"]})
        result = run_clustering(df)
        assert "error" in result

    def test_cluster_stats(self, numeric_only_df):
        result = run_clustering(numeric_only_df)
        stats = result["cluster_stats"]
        total = sum(s["size"] for s in stats.values())
        assert total == len(numeric_only_df)
