from datetime import datetime

import pandas as pd

from src.utils import calculate_date_range, filter_transactions_by_category_and_date


# testing calculate_date_range


# data given
def test_calculate_date_range_with_date():
    end_date, start_date = calculate_date_range("2024-05-15", months_period=3)

    assert end_date == datetime(2024, 5, 15)
    assert start_date.year == 2024
    assert start_date.month == 2  # минус 3 месяца


# no data given, expect today date (fake today)
def test_calculate_date_range_default_date(monkeypatch):
    fake_now = datetime(2024, 10, 1, 12, 0, 0)

    class FakeDT:
        @classmethod
        def now(cls):
            return fake_now

    monkeypatch.setattr("src.utils.datetime", FakeDT)

    end_date, start_date = calculate_date_range(None, months_period=6)

    assert end_date == fake_now
    assert start_date.year == 2024
    assert start_date.month == 4  # октябрь - 6 месяцев = апрель


# testing filter_transactions_by_category_and_date


# correct
def test_filter_transactions_by_category_and_date():
    df = pd.DataFrame({
        "Категория": ["Еда", "Еда", "Транспорт"],
        "Дата операции": pd.to_datetime([
            "2024-01-10",
            "2024-02-15",
            "2024-01-20"
        ]),
        "Сумма": [100, 200, 300],
    })

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)

    result = filter_transactions_by_category_and_date(df, "Еда", start, end)

    assert len(result) == 1
    assert result.iloc[0]["Сумма"] == 100


# nothing suits the date
def test_filter_transactions_by_category_and_date_no_matches():
    df = pd.DataFrame({
        "Категория": ["Еда", "Еда"],
        "Дата операции": pd.to_datetime(["2024-01-10", "2024-02-15"]),
    })

    start = datetime(2024, 3, 1)
    end = datetime(2024, 3, 31)

    result = filter_transactions_by_category_and_date(df, "Еда", start, end)

    assert result.empty


# nothing suits the category
def test_filter_transactions_by_category_and_date_wrong_category():
    df = pd.DataFrame({
        "Категория": ["Еда", "Транспорт"],
        "Дата операции": pd.to_datetime(["2024-01-10", "2024-01-20"]),
    })

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)

    result = filter_transactions_by_category_and_date(df, "Медицина", start, end)

    assert result.empty


# borders of the given range
def test_filter_transactions_by_category_and_date_boundaries():
    df = pd.DataFrame({
        "Категория": ["Еда"],
        "Дата операции": pd.to_datetime(["2024-05-01"]),
    })

    start = datetime(2024, 5, 1)
    end = datetime(2024, 5, 1)

    result = filter_transactions_by_category_and_date(df, "Еда", start, end)

    assert len(result) == 1
