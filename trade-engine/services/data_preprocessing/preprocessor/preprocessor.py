from typing import List, Optional, Union

import pandas as pd


class DataPreprocessor:
    """
    A class responsible for preparing and enriching market data with technical indicators
    and other features before vectorization.
    """

    def __init__(self):
        pass

    def add_moving_averages(
        self, df: pd.DataFrame, periods: List[int], price_column: str = "Close"
    ) -> pd.DataFrame:
        """
        Add multiple moving averages to the DataFrame.

        Args:
            df: DataFrame containing price data
            periods: List of periods for which to calculate MAs
            price_column: Column name to use for MA calculation (default: 'Close')

        Returns:
            DataFrame with added MA columns
        """
        result_df = df.copy()

        for period in periods:
            column_name = f"MA_{period}"
            result_df[column_name] = df[price_column].rolling(window=period).mean()

        return result_df

    def remove_incomplete_ma_rows(
        self, df: pd.DataFrame, ma_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Remove rows where any of the specified MA columns have NaN values.

        Args:
            df: DataFrame containing price data and MA columns
            ma_columns: List of MA column names to check. If None, will use all columns starting with 'MA_'

        Returns:
            DataFrame with only complete MA rows
        """
        # If no specific MA columns provided, find all MA columns
        if ma_columns is None:
            ma_columns = [col for col in df.columns if col.startswith("MA_")]

        if not ma_columns:
            raise ValueError("No MA columns found in the DataFrame")

        # Drop rows where any of the MA columns is NaN
        complete_df = df.dropna(subset=ma_columns)

        # Reset index to maintain continuous indexing
        complete_df = complete_df.reset_index(drop=True)

        print(f"Removed {len(df) - len(complete_df)} rows with incomplete MA values")
        print(f"Remaining rows: {len(complete_df)}")

        return complete_df

    def add_technical_indicators(
        self, df: pd.DataFrame, indicators: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Add various technical indicators to the DataFrame.
        This is a placeholder for future implementation of other indicators
        like RSI, MACD, Bollinger Bands, etc.

        Args:
            df: DataFrame containing price data
            indicators: List of indicator names to add

        Returns:
            DataFrame with added technical indicators
        """
        # TODO: Implement additional technical indicators as needed
        return df.copy()
