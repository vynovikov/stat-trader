from typing import List, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from domain.models.segment import Segment


class Vectorizer:
    """
    A class responsible for converting prepared market data and patterns into vector
    representations suitable for machine learning models and clustering.
    """

    def __init__(self, feature_columns: Optional[List[str]] = None):
        """
        Initialize the Vectorizer.

        Args:
            feature_columns: List of column names to use for vectorization.
                           If None, all numeric columns will be used.
        """
        self.feature_columns = feature_columns
        self.scaler = StandardScaler()

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform the DataFrame into a vector representation.

        Args:
            df: DataFrame containing prepared features (technical indicators, etc.)

        Returns:
            numpy array of vectors
        """
        # If no specific features are specified, use all numeric columns
        if self.feature_columns is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            self.feature_columns = list(numeric_cols)

        # Extract features and convert to numpy array
        features = df[self.feature_columns].values

        # Handle NaN values - for now we'll just fill with 0
        # In the future, this could be made more sophisticated
        features = features.astype(float)
        features = np.nan_to_num(features)

        return features

    def add_ma(self, df: pd.DataFrame, *ma_sizes: int) -> pd.DataFrame:
        """
        Add Moving Average columns to the DataFrame for specified window sizes.

        Args:
            df: DataFrame containing price data
            ma_sizes: Variable number of integers specifying MA window sizes

        Returns:
            DataFrame with added MA columns
        """
        result_df = df.copy()

        for size in ma_sizes:
            column_name = f"MA_{size}"
            result_df[column_name] = df["Close"].rolling(window=size).mean()

        return result_df

    def vectorize_pattern(self, segment: Segment, normalize: bool = True) -> np.ndarray:
        """
        Convert a single segment into a matrix of pattern vectors.

        Args:
            segment: Object containing pattern information
            normalize: Whether to normalize the features using StandardScaler
                      NOTE: Individual normalization is disabled - vectors should be
                      normalized together after collection for proper scaling

        Returns:
            numpy array where each row is a pattern vector
        """
        # Extract pattern vector from segment
        pattern_vector = segment.get_pattern_vector()
        pattern_vector = np.array(pattern_vector).reshape(
            1, -1
        )  # Reshape to 2D array for consistency

        # NOTE: Individual normalization removed - it was causing all vectors
        # to become identical since each scaler was trained on a single vector
        # Normalization should be done on the entire dataset after collection

        return pattern_vector

    def get_feature_importance(self, pattern_vectors: np.ndarray) -> dict:
        """
        Calculate the relative importance of each feature based on its variance.

        Args:
            pattern_vectors: Matrix of pattern vectors

        Returns:
            Dictionary mapping feature names to their importance scores
        """
        # Calculate variance for each feature
        variances = np.var(pattern_vectors, axis=0)

        # Define feature names
        feature_names = [
            "volatility",
            "volume_profile",
            "price_range",
            "momentum",
            "pattern_duration",
            "avg_body_size",
            "avg_shadow_size",
            "direction_changes",
        ]

        # Normalize variances to get relative importance
        total_variance = np.sum(variances)
        importance_scores = variances / total_variance

        return dict(zip(feature_names, importance_scores))
