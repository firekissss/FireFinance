import json
from unittest.mock import MagicMock

import pandas as pd

from src.views import main_page_view, reports_page_view, services_page_view


# main_page_view
def test_main_page_view_success(monkeypatch, df_mock, caplog):
    monkeypatch.setattr("src.views.import_transactions_from_file", lambda _: df_mock)
    monkeypatch.setattr("src.views.filter_by_date_interval", lambda df, s, e: df)
    monkeypatch.setattr("src.views.get_top_transactions", lambda df: df.head(2))
    monkeypatch.setattr("src.views.get_user_currencies", lambda: ["USD", "EUR"])
    monkeypatch.setattr("src.views.get_user_stocks", lambda: ["AAPL"])
    monkeypatch.setattr("src.views.get_stock_prices", lambda stocks: [{"ticker": "AAPL", "price": 100}])
    monkeypatch.setattr("src.views.get_currency_rates", lambda base, lst: [{"currency": "USD", "rate": 90}])
    monkeypatch.setattr("src.views.get_greeting_by_current_time", lambda: "Добрый день!")
    monkeypatch.setattr("src.views.get_cards_info", lambda df: [{"card": "test"}])
    monkeypatch.setattr("src.views.format_top_transactions_to_list", lambda df: [{"sum": -100}, {"sum": -50}])

    caplog.set_level("DEBUG")

    result_json = main_page_view("2025-11-30 10:00:00")
    result = json.loads(result_json)

    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result

    assert any("Main page view generated successfully" in r.message for r in caplog.records)


# services_page_view
def test_services_page_view(monkeypatch, df_mock, caplog):
    monkeypatch.setattr("src.views.import_transactions_from_file", lambda _: df_mock)
    monkeypatch.setattr(
        "src.views.analyze_cashback_categories", lambda df, y, m, sort_by: json.dumps({"Еда": 150}, ensure_ascii=False)
    )

    caplog.set_level("DEBUG")

    result_raw = services_page_view(2025, 11)
    result = json.loads(result_raw)

    assert "Еда" in result
    assert result["Еда"] == 150

    assert any("Services page view generated successfully" in r.message for r in caplog.records)


# reports_page_view
def test_reports_page_view(monkeypatch, df_mock, caplog):
    monkeypatch.setattr("src.views.import_transactions_from_file", lambda _: df_mock)

    # чтобы не трогать реальный декоратор report_to_file
    spending_mock = MagicMock(return_value=df_mock)

    monkeypatch.setattr("src.views.spending_by_category", spending_mock)

    # фейковый декоратор, который делает то же самое, что и обычный, только ничего не делает xD
    def fake_report_to_file(arg):
        # случай 1 — вызывается с параметром report_to_file("filename")(spending_by_category)
        if isinstance(arg, str):

            def decorator(func):
                def inner(*args, **kwargs):
                    return func(*args, **kwargs)

                return inner

            return decorator

        # случай №2 — вызывается без параметра report_to_file(spending_by_category)
        elif callable(arg):
            func = arg

            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        else:
            raise TypeError("Sorry you're not a winner")

    monkeypatch.setattr("src.views.report_to_file", fake_report_to_file)

    caplog.set_level("DEBUG")

    result = reports_page_view("Еда", "2025-11-30")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(df_mock)

    spending_mock.assert_called_once()

    assert any("Reports page view generated successfully" in r.message for r in caplog.records)
