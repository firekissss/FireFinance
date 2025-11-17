from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.mark.parametrize(
    "category, months_period",
    [
        ("Супермаркеты", 3),
        ("Фастфуд", 1),
    ],
)
def test_spending_by_category_filters_correctly(transactions_dataframe, fixed_date_range, category, months_period):
    with (
        patch("src.reports.calculate_date_range") as mock_date_range,
        patch("src.reports.filter_transactions_by_category_and_date") as mock_filter,
    ):
        mock_date_range.return_value = fixed_date_range

        expected_filtered = transactions_dataframe[transactions_dataframe["Категория"] == category]
        mock_filter.return_value = expected_filtered

        result = spending_by_category(transactions_dataframe, category, months_period=months_period, date="2007-03-30")

        mock_date_range.assert_called_once_with("2007-03-30", months_period)
        mock_filter.assert_called_once_with(transactions_dataframe, category, fixed_date_range[1], fixed_date_range[0])

        pd.testing.assert_frame_equal(result, expected_filtered)


def test_spending_by_category_logs(transactions_dataframe, fixed_date_range, caplog):
    caplog.set_level("DEBUG")
    category = "Супермаркеты"

    with (
        patch("src.reports.calculate_date_range") as mock_date_range,
        patch("src.reports.filter_transactions_by_category_and_date") as mock_filter,
    ):
        mock_date_range.return_value = fixed_date_range
        expected_filtered = transactions_dataframe[transactions_dataframe["Категория"] == category]
        mock_filter.return_value = expected_filtered

        result = spending_by_category(transactions_dataframe, category, months_period=3, date="2025-11-15")

        # проверка логов
        assert any("Starting spending_by_category analysis" in rec.message for rec in caplog.records)
        assert any("Input transactions shape" in rec.message for rec in caplog.records)
        assert any("Calculated date range" in rec.message for rec in caplog.records)
        assert any("Successfully filtered transactions" in rec.message for rec in caplog.records)
        assert any("Filtered transactions sample" in rec.message for rec in caplog.records)

        pd.testing.assert_frame_equal(result, expected_filtered)
