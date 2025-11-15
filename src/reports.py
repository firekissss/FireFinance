from typing import Optional

import pandas as pd
from logs import get_logger
from utils import calculate_date_range, filter_transactions_by_category_and_date
from decorators import log_exceptions

logger = get_logger(__name__)


@log_exceptions(logger)
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None,
                         months_period: int = 3) -> pd.DataFrame:
    """
    Returns spending transactions for specified category over last N months.

    Args:
        transactions: DataFrame with transactions data
        category: Category name to filter by
        date: End date for the period (YYYY-MM-DD format). If None, uses current date.
        months_period: Number of months to look back (default: 3)

    Returns:
        pd.DataFrame: Filtered transactions for the category over specified period
    """
    logger.info(f"Starting spending_by_category analysis for category: '{category}', "
                f"period: {months_period} months, end date: {date}")
    logger.debug(f"Input transactions shape: {transactions.shape}")

    # Calculate date range
    end_date, start_date = calculate_date_range(date, months_period)
    logger.debug(f"Calculated date range: {start_date} to {end_date}")

    # Filter data

    filtered = filter_transactions_by_category_and_date(transactions, category, start_date, end_date)

    logger.info(f"Successfully filtered transactions. Result shape: {filtered.shape}")
    logger.debug(f"Filtered transactions sample:\n{filtered.head()}")

    return filtered
