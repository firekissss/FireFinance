import json
from datetime import datetime

from src.utils import get_greeting_by_current_time, get_cards_info, import_transactions_from_file, \
    filter_by_date_interval, get_date_interval, get_top_transactions, get_currency_rates, get_user_currencies, \
    get_user_stocks, get_stock_prices, format_top_transactions_to_list


def main_page_view(input_date: str, input_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    main page view function
    :param input_date: the end date of analyzing data. the start date will be the first day of month given
    :param input_format: format of input data, "%Y-%m-%d %H:%M:%S" if not specified
    :return: json string that can be used by web-page main view
    """
    date_formatted = datetime.strptime(input_date, input_format)
    date_start, date_end = get_date_interval(date_formatted)

    dataframe = import_transactions_from_file("../data/example_operations.xlsx")
    filtered_dataframe = filter_by_date_interval(dataframe, date_start, date_end)
    top_5_transactions = get_top_transactions(filtered_dataframe)  # pd.dataframe

    currencies = get_user_currencies()
    stocks = get_user_stocks()

    greeting = get_greeting_by_current_time() # str
    cards_info = get_cards_info(filtered_dataframe) # list[dict]
    top_5_transactions_list = format_top_transactions_to_list(top_5_transactions) # list
    currency_rates = get_currency_rates("RUB", currencies) # list[dict[str, Any]]
    stock_prices = get_stock_prices(stocks) # list[dict[str, Any]]

    json_response = json.dumps(
        {
            "greeting": greeting,
            "cards": cards_info,
            "top_transactions": top_5_transactions_list,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }, ensure_ascii=False, indent=2
    )

    return json_response



