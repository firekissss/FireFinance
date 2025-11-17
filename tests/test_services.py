import json

import pandas as pd
import pytest

from src import services


@pytest.mark.parametrize("year, month, sort_by, expected_categories", [
    (2007, 3, "cat", ['Супермаркеты', 'Аптеки', 'Дом и ремонт', 'Косметика']),
    (2007, 3, "sum", ['Супермаркеты', 'Аптеки', 'Дом и ремонт', 'Косметика']),
    (2007, 2, "cat", ['Дом и ремонт']),
])
def test_analyze_cashback_categories_basic(transactions_dataframe, caplog, year, month, sort_by, expected_categories):
    caplog.set_level("DEBUG", logger="src.services")

    result_json = services.analyze_cashback_categories(transactions_dataframe, year, month, sort_by)
    result = json.loads(result_json)

    # Проверяем, что результат содержит правильные категории
    assert set(result.keys()) == set(expected_categories)

    # Проверяем, что в логах есть старт и успешное завершение
    assert any("Starting cashback analysis" in rec.message for rec in caplog.records)
    assert any("Cashback analysis completed successfully" in rec.message for rec in caplog.records)


def test_analyze_cashback_categories_no_data(caplog):
    caplog.set_level("DEBUG", logger="src.services")

    # Пустой DataFrame
    empty_df = pd.DataFrame(columns=["Дата операции", "Категория", "Сумма платежа", "Кэшбек"])
    result_json = services.analyze_cashback_categories(empty_df, 2007, 3)
    result = json.loads(result_json)

    assert result == {}
    assert any("No data found for period" in rec.message for rec in caplog.records)


def test_analyze_cashback_categories_no_valid_cashback(transactions_dataframe, monkeypatch, caplog):
    caplog.set_level("DEBUG", logger="src.services")

    # Патчим _clean_cashback_data чтобы вернуть пустой df
    monkeypatch.setattr(services, "_clean_cashback_data", lambda df: df.iloc[0:0])

    result_json = services.analyze_cashback_categories(transactions_dataframe, 2007, 3)
    result = json.loads(result_json)

    assert result == {}
    assert any("No valid cashback data after cleaning" in rec.message for rec in caplog.records)
