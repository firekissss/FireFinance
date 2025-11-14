from typing import Optional

import pandas as pd

from utils import calculate_date_range, prepare_transactions_data, filter_transactions_by_category_and_date


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
    # Calculate date range
    end_date, start_date = calculate_date_range(date, months_period)

    # Prepare and filter data
    df = prepare_transactions_data(transactions)
    filtered = filter_transactions_by_category_and_date(df, category, start_date, end_date)

    return filtered