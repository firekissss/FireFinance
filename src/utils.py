import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from src.api_client import fetch_from_apilayer, fetch_from_marketstack

# default paths
PATH_TO_BANNER = "../banner.txt"
PATH_TO_USER_SETTINGS = "../user_settings.json"


# for main page

def print_banner(path_to_banner=PATH_TO_BANNER):
    """
    prints a banner of the project ("FIREFINANCE" giant letters)
    :param path_to_banner: where is the banner. "../banner.txt" by default
    """
    with open(path_to_banner, "r", encoding="utf-8") as f:
        print(f.read())


def load_user_settings(filepath: str | Path = PATH_TO_USER_SETTINGS) -> dict:
    """
    loads user settings from json file
    :param filepath: path to settings file. "../user_settings.json" if not specified
    :return: dict with user settings
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_user_currencies(filepath: str | Path = PATH_TO_USER_SETTINGS) -> list[str]:
    """
    returns list of user currencies from user settings file
    :param filepath: path to settings file. "../user_settings.json" if not specified
    :return: list of user currencies
    """
    settings = load_user_settings(filepath)
    return settings.get("user_currencies", [])


def get_user_stocks(filepath: str | Path = PATH_TO_USER_SETTINGS) -> list[str]:
    """
    returns list of user stocks from user settings file
    :param filepath: path to settings file. "../user_settings.json" if not specified
    :return: list of user stocks
    """
    settings = load_user_settings(filepath)
    return settings.get("user_stocks", [])


def get_greeting_by_current_time() -> str:
    """
    returns greeting depending on what time is it now
    :return: greeting string
    """
    current_time = datetime.now().hour

    if 6 <= current_time < 12:
        return "Доброе утро"
    elif 12 <= current_time < 18:
        return "Добрый день"
    elif 18 <= current_time < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_date_interval(input_date: datetime) -> tuple[datetime, datetime]:
    """
    returns date and time interval - from the beginning of the month in which
    the incoming date falls to the incoming date.
    :param input_date: datetime object
    :return: start and end dates as datetime objects
    """
    date_end = input_date
    date_start = date_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    return date_start, date_end


def import_transactions_from_file(file_path: str) -> pd.DataFrame:
    """
    imports transactions from .xlsx file and formats date column "Дата операции"
    to datetime for correct operations
    :param file_path: path to xlsx file
    :return: pd.DataFrame with transactions
    """
    if not file_path.endswith('.xlsx'):
        raise ValueError(f"Неподдерживаемый тип файла: {file_path}. Поддерживается только .xlsx.")
    try:
        df = pd.read_excel(file_path)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Дата операции"])  # строки в колонке почти всегда содержат дату, проверка страховочная

    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception as e:
        raise RuntimeError(f"Ошибка при открытии или чтении файла {file_path}: {e}") from e

    return df


def filter_by_date_interval(input_dataframe: pd.DataFrame, date_start: datetime, date_end: datetime) -> pd.DataFrame:
    """
    filters dataframe based on date interval
    :param input_dataframe: pd.DataFrame with transactions
    :param date_start: start date (datetime object)
    :param date_end: end date (datetime object)
    :return: filtered dataframe
    """
    return input_dataframe[
        (input_dataframe["Дата операции"] >= date_start) & (input_dataframe["Дата операции"] <= date_end)
        ]


def analyze_df_structure(df: pd.DataFrame) -> dict:
    """
    for info purpose analysis during development. never actually used in any other functions
    :param df: input dataframe
    :return: description of input dataframe
    """
    return {
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.to_dict(),
        "missing_ratio": df.isna().mean().to_dict(),
        "example_rows": df.head(3).to_dict(orient="records")
    }


def get_cards_info(df: pd.DataFrame) -> list[dict]:
    """
    returns list of cards info
    :param df: input dataframe
    :return: list of dictionaries with cards info
    """
    grouped = (
        df.groupby("Номер карты", as_index=False)
        .agg({"Сумма операции с округлением": "sum", "Кэшбэк": "sum"})
    )
    result = [
        {
            "last_digits": str(card)[-4:],
            "total_spent": round(total, 2),
            "cashback": round(cashback, 2)
        }
        for card, total, cashback in zip(
            grouped["Номер карты"],
            grouped["Сумма операции с округлением"],
            grouped["Кэшбэк"]
        )
    ]

    return result


def group_transfers_between_cards(df: pd.DataFrame) -> pd.DataFrame:
    """
    groups duplicates of transactions caused by inter-card transfers.
    use in get_top_transactions only if not sure what this function does.
    :param df: input dataframe with duplicates
    :return: dataframe with grouped transactions (only positive payments left)
    """
    # группируем по описанию, MCC и номеру карты
    # если MCC и карта пустые у обеих операций, значит это, возможно, перевод между своими счетами
    to_drop = set()
    for descr, group in df.groupby("Описание"):
        if group["MCC"].isna().all() and group["Номер карты"].isna().all() and len(group) > 1:
            # проверяем каждую пару по времени
            times = group["Дата операции"].sort_values()
            for i, t1 in enumerate(times):
                near = group[
                    (group["Дата операции"] - t1).dt.total_seconds().abs() <= 2
                    ]
                if len(near) == 2:
                    # две операции — оставляем положительную
                    idx_pos = near.loc[near["Сумма платежа"] > 0].index
                    idx_neg = near.loc[near["Сумма платежа"] < 0].index
                    if len(idx_pos) == 1 and len(idx_neg) == 1:
                        to_drop.update(idx_neg.tolist())
    # убираем дубликаты-переводы
    if to_drop:
        df = df.drop(index=list(to_drop))

    return df


def get_top_transactions(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Returns the top N transactions by column "Сумма платежа",
    considering only successful ("OK") operations.
    Removes duplicates that match the description, time (≤ 2 sec),
    and with blank fields "MCC" and "Номер карыт" — leaving the option with a positive amount.
    requires group_transfers_between_cards func from src.utils
    :param df: input dataframe
    :param top_n: the amount of transactions to return
    :return: dataframe with top N transactions
    """
    if len(df) == 0:
        return df

    # фильтруем только успешные операции
    df = df[df["Статус"] == "OK"].copy()
    if len(df) == 0:
        return df

    # выборка из top_n*2 операций.
    abs_sum = df["Сумма платежа"].abs().to_numpy()
    if len(df) <= top_n * 2:
        top_df = df.copy()
    else:
        top_idx = np.argpartition(abs_sum, -top_n * 2)[-top_n * 2:]
        top_df = df.iloc[top_idx].copy()

    top_df = group_transfers_between_cards(top_df)

    # сортировка по модулю суммы и дате (подготовка к возврату)
    top_df["abs_sum"] = top_df["Сумма платежа"].abs()
    top_df = top_df.sort_values(
        by=["abs_sum", "Дата операции"],
        ascending=[False, False],
        kind="mergesort"
    ).drop(columns=["abs_sum"])

    # возврат ровно top_n строк
    return top_df.head(top_n).reset_index(drop=True)


def format_top_transactions_to_list(df: pd.DataFrame) -> list[dict]:
    """
    Transfers DataFrame with columns:
    'Дата операции', 'Сумма платежа', 'Категория', 'Описание'
    to JSON-string of this format:
    {
      "top_transactions": [
        {"date": "...", "amount": ..., "category": "...", "description": "..."},
        ...
      ]
    }
    :param df: input dataframe
    :return: list of dictionaries with top N transactions
    """
    transactions = [
        {
            "date": pd.to_datetime(row["Дата операции"]).strftime("%d.%m.%Y")
            if pd.notna(row["Дата операции"]) else "",
            "amount": float(row["Сумма платежа"]),
            "category": str(row.get("Категория", ""))
            if pd.notna(row.get("Категория", "")) else "",
            "description": str(row.get("Описание", ""))
            if pd.notna(row.get("Описание", "")) else ""
        }
        for _, row in df.iterrows()
    ]

    return transactions


def get_currency_rates(base_currency: str, symbols: list[str]) -> list[dict[str, Any]]:
    """
    Returns the current rates of the specified currencies relative to base_currency.
    The result is a list of format dictionaries:
    [
        {"currency": "USD", "rate": 100},
        {"currency": "EUR", "rate": 200}
    ]
    :param base_currency: the currency to get the rate of
    :param symbols: the currencies to get the rate of
    :return: a list of format dictionaries:
    """
    params = {
        "source": base_currency,
        "currencies": ",".join(symbols)
    }

    data = fetch_from_apilayer("live", params)
    quotes = data.get("quotes")
    if not quotes:
        raise RuntimeError("Ответ не содержит поля 'quotes'")

    # Пример: quotes = {"USDRUB": 100, "USDEUR": 200}
    rates = []
    for symbol in symbols:
        key = f"{base_currency}{symbol}"
        rate = quotes.get(key)
        if rate is None:
            raise RuntimeError(f"Нет курса для валюты {symbol}")
        rates.append({"currency": symbol, "rate": round(1 / rate, 2)})

    return rates


def get_stock_prices(symbols: list[str]) -> list[dict[str, Any]]:
    """
    Returns current closing prices (in USD) of stocks from the symbols list.
    Example: ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
    The result is a list of format dictionaries:
    [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
    ]
    :param symbols: the stocks to get the prices of
    :return: a list of format dictionaries:
    """
    params = {
        "symbols": ",".join(symbols),
        "limit": len(symbols)
    }

    data = fetch_from_marketstack("eod/latest", params)
    stocks = data.get("data")
    if not stocks:
        raise RuntimeError("Ответ не содержит поля 'data'")

    prices = []
    for stock in stocks:
        symbol = stock.get("symbol")
        price = stock.get("close")
        if symbol and price is not None:
            prices.append({"stock": symbol, "price": float(price)})

    return prices


# for services

def filter_data_by_date(data: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    """
    Filters data by specified year and month.

    Args:
        data (pd.DataFrame): Input data
        year (int): Year for filtering
        month (int): Month for filtering (1-12)

    Returns:
        pd.DataFrame: Filtered data
    """
    mask = (data['Дата операции'].dt.year == year) & (data['Дата операции'].dt.month == month)
    return data[mask].copy()


def clean_cashback_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans data from invalid cashback values.

    Args:
        data (pd.DataFrame): Data to clean

    Returns:
        pd.DataFrame: Cleaned data
    """
    cleaned_data = data.dropna(subset=['Кэшбэк'])

    cleaned_data = cleaned_data[
        cleaned_data['Кэшбэк'].apply(lambda x: isinstance(x, (int, float)))
    ]

    return cleaned_data


def calculate_cashback_by_category(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculates cashback sum by categories.

    Args:
        data (pd.DataFrame): Data for calculation

    Returns:
        Dict[str, float]: Dictionary with categories and cashback amounts
    """
    cashback_by_category = data.groupby('Категория')['Кэшбэк'].sum()
    return {category: round(float(amount), 2) for category, amount in cashback_by_category.items()}


def sort_results(result_dict: Dict[str, float], sort_by: str) -> Dict[str, float]:
    """
    Sorts results according to sort_by parameter.

    Args:
        result_dict (Dict[str, float]): Dictionary with results
        sort_by (str): Sorting parameter ('cat' or 'sum')

    Returns:
        Dict[str, float]: Sorted dictionary
    """
    if sort_by == 'sum':
        return dict(sorted(result_dict.items(), key=lambda x: x[1], reverse=True))
    else:  # 'cat' или любое другое значение
        return dict(sorted(result_dict.items()))
