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
        
    def clean_data(self):
        """Clean the dataset by handeling missing values, duplicates, and invalid data"""
        print("\n" * "=" * 50)
        print("Data cleaning")
        print("=" * 50)
        
        # Check for missing values
        missing_values = self.df.isnull().sum()
        print(f"\nMissing values per column: ")
        print(missing_values[missing_values > 0])
        
        # Remove duplicates
        duplicates_befor = self.df.duplicated().sum()
        self.df = self.df.drop_duplicates()
        print(f"\nDuplicates removed: {duplicates_befor}")
        
        # Handle missing values - fill numeric with median, categorical with mode
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                if self.df[col].dtype in ['Float64', 'int64']:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                else:
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
                    
        # Remove rows with negative or zero sales/quantities (if these columns exist)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if 'quantity' in col.lower() or 'sales' in col.lower() or 'price' in col.lower():
                self.df = self.df[self.df[col] > 0]
                
            rows_after_cleaning = len(self.df)
            print(f"\nrows after cleaning: {rows_after_cleaning}")
            print(f"\nRows removed: {self.original_rows - rows_after_cleaning}")
            