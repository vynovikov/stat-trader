import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import pandas as pd

from services.data_preprocessing.preprocessor.preprocessor import DataPreprocessor

# Define paths
raw_data_path = Path("data/candles/BTCUSDT/raw/BTCUSDT_5m_last_two_months.csv")
complete_ma_path = Path(
    "data/candles/BTCUSDT/ma_added/BTCUSDT_5m_last_two_months_ma.csv"
)

# Read the CSV file
df = pd.read_csv(raw_data_path)

# Create preprocessor instance and add moving averages
preprocessor = DataPreprocessor()
df_with_ma = preprocessor.add_moving_averages(
    df, periods=[50, 200], price_column="close"
)

# Create dataset with only complete MA rows
df_complete = preprocessor.remove_incomplete_ma_rows(df_with_ma)
df_complete.to_csv(complete_ma_path, index=False)
print(f"Saved dataset with only complete MA rows to {complete_ma_path}")
#
