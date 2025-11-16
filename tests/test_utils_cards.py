import pandas as pd
from datetime import datetime, timedelta

from src.utils import (
    get_cards_info,
    group_transfers_between_cards,
    get_top_transactions,
    format_top_transactions_to_list,
)


# testing get_cards_info


# ok
def test_get_cards_info_basic():
    df = pd.DataFrame({
        "Номер карты": ["1111222233334444", "1111222233334444", "5555666677778888"],
        "Сумма операции с округлением": [100.123, 200.456, 300.111],
        "Кэшбэк": [10.1, 5.3, 7.0],
    })

    result = get_cards_info(df)

    assert len(result) == 2

    card1 = next(r for r in result if r["last_digits"] == "4444")
    card2 = next(r for r in result if r["last_digits"] == "8888")

    assert card1["total_spent"] == round(100.123 + 200.456, 2)
    assert card1["cashback"] == round(10.1 + 5.3, 2)
    assert card2["total_spent"] == round(300.111, 2)


# empty data
def test_get_cards_info_empty():
    df = pd.DataFrame(columns=["Номер карты", "Сумма операции с округлением", "Кэшбэк"])
    result = get_cards_info(df)
    assert result == []


# testing group_transfers_between_cards


# something gets removed
def test_group_transfers_between_cards_basic():
    t0 = datetime(2024, 1, 1, 12, 0, 0)

    df = pd.DataFrame({
        "Описание": ["Перевод", "Перевод"],
        "MCC": [None, None],
        "Номер карты": [None, None],
        "Дата операции": [t0, t0 + timedelta(seconds=1)],
        "Сумма платежа": [-500, 500],
    })

    result = group_transfers_between_cards(df)

    assert len(result) == 1
    assert result.iloc[0]["Сумма платежа"] == 500


# nothing to be removed
def test_group_transfers_no_duplicates():
    df = pd.DataFrame({
        "Описание": ["A", "B"],
        "MCC": [None, None],
        "Номер карты": [None, None],
        "Дата операции": [datetime.now(), datetime.now()],
        "Сумма платежа": [100, -200],
    })

    result = group_transfers_between_cards(df)

    assert len(result) == 2


# testing get_top_transactions


# main test (4 transactions)
def test_get_top_transactions_basic():
    df = pd.DataFrame({
        "Дата операции": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"
        ]),
        "Сумма платежа": [100, -300, 50, -200],
        "Статус": ["OK", "OK", "FAILED", "OK"],
        "Описание": ["AMATORY", "STIGMATA", "ORIGAMI", "TENKORR"],
        "MCC": ["01", "100", "112", "911"]
    })

    result = get_top_transactions(df, top_n=2)

    # Самые большие суммы по модулю = -300 и -200
    assert len(result) == 2
    assert result.iloc[0]["Сумма платежа"] == -300
    assert result.iloc[1]["Сумма платежа"] == -200


# additional test (10 transactions)
def test_get_top_transactions_extended():
    df = pd.DataFrame({
        "Дата операции": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07",
            "2024-01-08", "2024-01-09", "2024-01-10"
        ]),
        "Сумма платежа": [100, -300, 50, -200, 1, 2, 3, 4, 5, 2007],
        "Статус": ["OK", "OK", "OK", "OK", "OK", "OK", "OK", "OK", "OK", "OK"],
        "Описание": ["AMATORY", "STIGMATA", "ORIGAMI", "TENKORR", "METALLICA", "BMTH", "ANNISOKAY",
                     "помогите", "я", "устал"],
        "MCC": ["01", "100", "112", "911", "1", "2", "3", "4", "5", "6"],
    })

    result = get_top_transactions(df, top_n=3)

    assert len(result) == 3
    assert result.iloc[0]["Сумма платежа"] == 2007
    assert result.iloc[1]["Сумма платежа"] == -300
    assert result.iloc[2]["Сумма платежа"] == -200


# empty data
def test_get_top_transactions_empty():
    df = pd.DataFrame(columns=["Сумма платежа", "Статус"])
    result = get_top_transactions(df)
    assert result.empty


# no successful ('OK') transactions
def test_get_top_transactions_no_ok():
    df = pd.DataFrame({
        "Сумма платежа": [100, 200],
        "Статус": ["ERR", "FAIL"]
    })
    result = get_top_transactions(df)
    assert result.empty


# testing format_top_transactions_to_list


# correct
def test_format_top_transactions_to_list():
    df = pd.DataFrame({
        "Дата операции": [pd.Timestamp("2024-01-01")],
        "Сумма платежа": [123.45],
        "Категория": ["Еда"],
        "Описание": ["Пятёрочка"]
    })

    result = format_top_transactions_to_list(df)

    assert len(result) == 1
    assert result == [{'date': '01.01.2024', 'amount': 123.45, 'category': 'Еда', 'description': 'Пятёрочка'}]


# empty
def test_format_top_transactions_empty():
    df = pd.DataFrame()
    assert format_top_transactions_to_list(df) == []
