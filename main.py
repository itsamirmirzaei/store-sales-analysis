"""
A comprehensive sales analysis project using pandas to extract insights from retail data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SalesAnalyzer:
    """Main class for sales data analysis"""
    
    def __init__(self, filepath):
        """Initial the analyzer with data from CSV file
        
        Args:
            filepath (str): Path to the CSV file containing sales data
        """
        print("Loading data...")
        self.df = pd.read_csv(filepath)
        self.original_rows = len(self.df)
        print(f"Data loaded successfully: {self.original_rows} rows")
        
    def display_basic_info(self):
        """Display basic information about the dataset"""
        print("\n" * "=" * 50)
        print("Basic data information")
        print("=" * 50)
        print(f"\nDataset shape: {self.df.shape}")
        print(f"\nColumn Names and Types: ")
        print(self.df.dtypes)
        print(f"\nFirst 10 rows: ")
        print(self.df.head(10))
        print(f"\nBasic statistics: ")
        print(self.df.describe())