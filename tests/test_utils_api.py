import pytest
from unittest.mock import patch

from src.utils import (
    get_currency_rates,
    get_stock_prices,
)


# testing get_currency_rates


# ok
@patch("src.utils.fetch_from_apilayer")
def test_get_currency_rates_success(mock_api):
    # API возвращает прямые котировки, например USDRUB = 100
    mock_api.return_value = {
        "quotes": {
            "USDEUR": 0.9,
            "USDJPY": 150,
        }
    }

    result = get_currency_rates("USD", ["EUR", "JPY"])

    assert result == [
        {"currency": "EUR", "rate": round(1 / 0.9, 2)},
        {"currency": "JPY", "rate": round(1 / 150, 2)},
    ]

    mock_api.assert_called_once()


# empty list of currencies
def test_get_currency_rates_empty_symbols():
    result = get_currency_rates("USD", [])
    assert result == []


# api didnt give us the quotes
@patch("src.utils.fetch_from_apilayer")
def test_get_currency_rates_no_quotes(mock_api):
    mock_api.return_value = {}  # quotes отсутствует

    with pytest.raises(RuntimeError):
        get_currency_rates("USD", ["EUR"])


# api didn't give the rate to some of the currencies from our list
@patch("src.utils.fetch_from_apilayer")
def test_get_currency_rates_missing_currency(mock_api):
    mock_api.return_value = {
        "quotes": {"USDEUR": 0.9}
    }

    # USDJPY отсутствует
    with pytest.raises(RuntimeError):
        get_currency_rates("USD", ["EUR", "JPY"])


# testing get_stock_prices


# ok
@patch("src.utils.fetch_from_marketstack")
def test_get_stock_prices_success(mock_api):
    mock_api.return_value = {
        "data": [
            {"symbol": "AAPL", "close": 150.12},
            {"symbol": "TSLA", "close": 700.55},
        ]
    }

    result = get_stock_prices(["AAPL", "TSLA"])

    assert result == [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "TSLA", "price": 700.55},
    ]

    mock_api.assert_called_once()


# empty list
def test_get_stock_prices_empty_symbols():
    assert get_stock_prices([]) == []


# no data in api response
@patch("src.utils.fetch_from_marketstack")
def test_get_stock_prices_no_data(mock_api):
    mock_api.return_value = {}

    with pytest.raises(RuntimeError):
        get_stock_prices(["AAPL"])


# no 'close' or 'symbol' param in response
@patch("src.utils.fetch_from_marketstack")
def test_get_stock_prices_missing_fields(mock_api):
    mock_api.return_value = {
        "data": [
            {"symbol": "AAPL"},  # нет close
            {"symbol": None, "close": 100}  # нет имени
        ]
    }

    result = get_stock_prices(["AAPL"])

    # both strings are going to hell
    assert result == []
