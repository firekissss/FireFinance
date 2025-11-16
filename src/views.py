import json
from datetime import datetime
from typing import Optional

from decorators import report_to_file
from reports import spending_by_category
from services import analyze_cashback_categories
from src.utils import get_greeting_by_current_time, get_cards_info, import_transactions_from_file, \
    filter_by_date_interval, get_date_interval, get_top_transactions, get_currency_rates, get_user_currencies, \
    get_user_stocks, get_stock_prices, format_top_transactions_to_list

from logs import get_logger
from decorators import log_exceptions

logger = get_logger(__name__)


@log_exceptions(logger)
def main_page_view(input_date: str, input_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    main page view function
    :param input_date: the end date of analyzing data. the start date will be the first day of month given
    :param input_format: format of input data, "%Y-%m-%d %H:%M:%S" if not specified
    :return: json string that can be used by web-page main view
    """
    logger.info(f"Generating main page view for date: {input_date}")
    logger.debug(f"Input format: {input_format}")

    date_formatted = datetime.strptime(input_date, input_format)
    date_start, date_end = get_date_interval(date_formatted)
    logger.debug(f"Date range: {date_start} to {date_end}")

    dataframe = import_transactions_from_file("../data/example_operations.xlsx")
    filtered_dataframe = filter_by_date_interval(dataframe, date_start, date_end)
    logger.debug(f"Data filtered: {len(filtered_dataframe)} transactions in period")

    top_5_transactions = get_top_transactions(filtered_dataframe)
    logger.debug(f"Top transactions prepared: {len(top_5_transactions)} transactions")

    currencies = get_user_currencies()
    stocks = get_user_stocks()
    logger.debug(f"User currencies: {currencies}, stocks: {stocks}")

    greeting = get_greeting_by_current_time()  # str
    cards_info = get_cards_info(filtered_dataframe)  # list[dict]
    top_5_transactions_list = format_top_transactions_to_list(top_5_transactions)  # list
    currency_rates = get_currency_rates("RUB", currencies)  # list[dict[str, Any]]
    stock_prices = get_stock_prices(stocks)  # list[dict[str, Any]]

    logger.debug(f"Components prepared - greeting: {greeting}, cards: {len(cards_info)}, "
                 f"transactions: {len(top_5_transactions_list)}, "
                 f"currency rates: {len(currency_rates)}, stock prices: {len(stock_prices)}")

    json_response = json.dumps(
        {
            "greeting": greeting,
            "cards": cards_info,
            "top_transactions": top_5_transactions_list,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }, ensure_ascii=False, indent=2
    )

    logger.info("Main page view generated successfully")
    return json_response


@log_exceptions(logger)
def services_page_view(year: int, month: int) -> str:
    """
    Displays services page with cashback categories analysis.

    Args:
        year: Year for analysis
        month: Month for analysis (1-12)

    Returns:
        str: JSON string with cashback analysis by categories
    """
    logger.info(f"Generating services page view for {year}-{month:02d}")

    data = import_transactions_from_file("../data/example_operations.xlsx")
    logger.debug(f"Data loaded for cashback analysis: {len(data)} transactions")

    result = analyze_cashback_categories(data, year, month, sort_by='cat')

    logger.info(f"Services page view generated successfully for {year}-{month:02d}")
    logger.debug(f"Cashback analysis result length: {len(result)} characters")

    return result


@log_exceptions(logger)
def reports_page_view(
        cat_name: str,
        date: Optional[str] = None,
        output_file: Optional[str] = None
):
    """
    Displays reports page with spending analysis by category.

    Args:
        cat_name: Category name to analyze
        date: End date for analysis period (YYYY-MM-DD format). If None, uses current date.
        output_file: Output filename for saving the report. If None, uses default filename.

    Returns:
        pd.DataFrame: Filtered transactions for the specified category and period
    """
    logger.info(f"Generating reports page view for category: '{cat_name}', date: {date}")
    logger.debug(f"Output file: {output_file}")

    data = import_transactions_from_file("../data/example_operations.xlsx")
    logger.debug(f"Data loaded for reports: {len(data)} transactions")

    # Декорируем динамически
    if output_file:
        wrapped = report_to_file(output_file)(spending_by_category)
        logger.debug(f"Report will be saved to file: {output_file}")
    else:
        wrapped = report_to_file(spending_by_category)
        logger.debug("Using default report filename")

    # Вызываем декорированную версию
    result = wrapped(data, cat_name, date)

    logger.info(f"Reports page view generated successfully for category: '{cat_name}'")
    logger.debug(f"Report result: {len(result)} transactions found")

    return result
