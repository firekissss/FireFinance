from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import analyze_df_structure, filter_by_date_interval, import_transactions_from_file


# testing import_transactions_from_file


# success import
def test_import_transactions_from_file_success(tmp_path):
    df = pd.DataFrame({
        "Дата операции": ["01.01.2024", "02.01.2024"],
        "Сумма платежа": [100, 200]
    })
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)

    result = import_transactions_from_file(str(file_path))

    assert len(result) == 2
    assert list(result.columns) == ["Дата операции", "Сумма платежа"]
    assert pd.api.types.is_datetime64_any_dtype(result["Дата операции"])


# wrong extension
def test_import_transactions_from_file_wrong_extension():
    with pytest.raises(ValueError):
        import_transactions_from_file("bring_me_the_horizon.txt")


# file not found
def test_import_transactions_file_not_found():
    with pytest.raises(RuntimeError):
        import_transactions_from_file("samsung.xlsx")


# empty file
@patch("pandas.read_excel", side_effect=pd.errors.EmptyDataError)
def test_import_transactions_empty_file(_mock_read):
    result = import_transactions_from_file("xiaomi.xlsx")
    assert isinstance(result, pd.DataFrame)
    assert result.empty


# incorrect data gets removed
def test_import_transactions_invalid_dates(tmp_path):
    df = pd.DataFrame({
        "Дата операции": ["01.01.2024", "invalid_date"],
        "Сумма платежа": [100, 200]
    })
    file_path = tmp_path / "iphone.xlsx"
    df.to_excel(file_path, index=False)

    result = import_transactions_from_file(str(file_path))

    assert len(result) == 1
    assert result.iloc[0]["Сумма платежа"] == 100


# testing filter_by_date_interval


# ok
def test_filter_by_date_interval():
    df = pd.DataFrame({
        "Дата операции": pd.to_datetime([
            "2024-01-01", "2024-02-01", "2024-03-01"
        ]),
        "Сумма": [1, 2, 3]
    })

    start = datetime(2024, 2, 1)
    end = datetime(2024, 3, 1)

    result = filter_by_date_interval(df, start, end)

    assert len(result) == 2
    assert result["Сумма"].tolist() == [2, 3]


# empty data
def test_filter_by_date_interval_empty_df():
    df = pd.DataFrame(columns=["Дата операции"])
    result = filter_by_date_interval(df, datetime(2024, 1, 1), datetime(2024, 1, 31))
    assert result.empty


# testing analyze_df_structure


def test_analyze_df_structure():
    df = pd.DataFrame({
        "A": [1, None, 3],
        "B": ["x", "y", "z"]
    })

    info = analyze_df_structure(df)

    assert info["columns"] == ["A", "B"]
    assert info["dtypes"]["A"] == df["A"].dtype
    assert info["missing_ratio"]["A"] == 1 / 3
    assert len(info["example_rows"]) == 3
    assert info["example_rows"][0]["A"] == 1
