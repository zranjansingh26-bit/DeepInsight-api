"""Tests for the chart generator engine."""

import pytest
import pandas as pd
import numpy as np

from engines.chart_generator import (
    generate_histogram,
    generate_distribution_charts,
    generate_box_plots,
    generate_correlation_heatmap,
)


class TestHistogram:
    def test_generates_valid_chart(self, sample_df):
        chart = generate_histogram(sample_df, "revenue")
        assert isinstance(chart, dict)
        assert "data" in chart
        assert "layout" in chart

    def test_custom_title(self, sample_df):
        chart = generate_histogram(sample_df, "revenue", title="My Chart")
        assert chart["layout"]["title"]["text"] == "My Chart"


class TestDistributionCharts:
    def test_generates_charts_for_numeric(self, sample_df):
        charts = generate_distribution_charts(sample_df)
        assert isinstance(charts, list)
        assert len(charts) > 0
        for c in charts:
            assert "chart_type" in c
            assert c["chart_type"] == "histogram"


class TestBoxPlots:
    def test_generates_box_plots(self, numeric_only_df):
        chart = generate_box_plots(numeric_only_df)
        assert isinstance(chart, dict)
        assert "data" in chart

    def test_no_numeric(self):
        df = pd.DataFrame({"a": ["x", "y"], "b": ["p", "q"]})
        chart = generate_box_plots(df)
        assert chart == {}


class TestCorrelationHeatmap:
    def test_generates_heatmap(self, numeric_only_df):
        chart = generate_correlation_heatmap(numeric_only_df)
        assert isinstance(chart, dict)
        assert "data" in chart

    def test_single_column(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        chart = generate_correlation_heatmap(df)
        assert chart == {}
