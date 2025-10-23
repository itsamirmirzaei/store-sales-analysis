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
        """Clean the dataset by handling missing values, duplicates, and invalid data"""
        print("\n" * "=" * 50)
        print("Data cleaning")
        print("=" * 50)
        
        # Check for missing values
        missing_values = self.df.isnull().sum()
        print(f"\nMissing values per column: ")
        print(missing_values[missing_values > 0])
        
        # Remove duplicates
        duplicates_before = self.df.duplicated().sum()
        self.df = self.df.drop_duplicates()
        print(f"\nDuplicates removed: {duplicates_before}")
        
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
    
    def add_derived_columns(self):
        """Add new columns with calculated metrics
        Assumes columns exist: Sales, Cost, Profit (or similar)
        """
        print("\n" * "=" * 50)
        print("Creating derived columns")
        print("=" * 50)
        
        # Try to find relevant columns (flexible column naming)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        cost_col = next((col for col in self.df.columns if 'cost' in col.lower()), None)
        profit_col = next((col for col in self.df.columns if 'profit' in col.lower()), None)
        quantity_col = next((col for col in self.df.columns if 'quantity' in col.lower() or 'qty' in col.lower()), None)
        
        if sales_col and cost_col and not profit_col:
            # Calculate profit if not exists
            self.df['Profit'] = self.df[sales_col] - self.df[cost_col]
            profit_col = 'Profit'
            print("Profit column created")
            
        if sales_col and profit_col:
            # Calculate average price per unit
            self.df['Average_Unit_Price'] = (self.df[sales_col] / self.df[quantity_col]).round(2)
            print("Average Unit Price column created")
            
        # Try to parse date column and extract month/year
        date_col = next((col for col in self.df.columns if 'date' in col.lower()), None)
        if date_col:
            try:
                self.df[date_col] = pd.to_datetime(self.df[date_col])
                self.df['Year'] = self.df[date_col].dt.year
                self.df['Month'] = self.df[date_col].dt.month
                self.df['Month_Name'] = self.df[date_col].dt.month_name()
                self.df['Quarter'] = self.df[date_col].dt.quarter
                print("Date-based columns created (Year, Month, Month_name, Quarter)")
            except:
                print("Could not parse date column")
        
        print(f"\nNew columns added. Total column now: {len(self.df.columns)}")
        
    def analyze_top_products(self, top_n=10):
        """
        Identify and analyze top-selling products
        
        Args:
            top_n (int): Number of top products to display
        """
        print("\n" + "=" * 50)
        print(f"Top {top_n} Best Selling Products")
        print("=" * 50)
        
        # Find product and sales columns
        product_col = next((col for col in self.df.columns if 'product' in col.lower() or 'item' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        quantity_col = next((col for col in self.df.columns if 'quantity' in col.lower() or 'qty' in col.lower()), None)
        
        if not product_col or not sales_col:
            print("Required columns not found")
            return None
        
        # Aggregate by product
        product_sales = self.df.groupby(product_col).agg(
            {
                sales_col: 'sum',
                quantity_col: 'sum' if quantity_col else 'count'
            }
        ).reset_index()
        
        # Sort and get top products
        product_sales = product_sales.sort_values(by=sales_col, ascending=False).head(top_n)
        product_sales.columns = ['Product', 'Total_Sales', 'Total_Quantity']
        
        print(product_sales.to_string(index=False))
        
        # Save to CSV
        product_sales.to_csv('top_products_csv', index=False)
        print(f"\nResults saved to 'top_products_csv'")
        
        return product_sales
    
    def analyze_loyal_customer(self, top_n=10):
        """
        Identify loyal customers based on purchase frequency and total spending
        
        Args:
            top_n (int): Number of customers to display
        """
        print("\n" + "=" * 50)
        print(f"Top {top_n} Loyal Customers")
        print("=" * 50)
        
        # Find customer and sales columns
        customer_col = next((col for col in self.df.columns if 'customer' in col.lower() or 'client' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        
        if not customer_col or not sales_col:
            print("Required columns not found")
            return None
        
        # Aggregate by customer
        customer_analysis = self.df.groupby(customer_col).agg(
            {
                sales_col: ['sum', 'count', 'mean']
            }
        ).reset_index()
        
        customer_analysis.columns = ['Customer', 'Total_Spending', 'Purchase_Count', 'Average_Purchase']
        customer_analysis = customer_analysis.sort_values(by='Total_Spending', ascending=False).head(top_n)
        customer_analysis['Total_Spending'] = customer_analysis['Total_Spending'].round(2)
        customer_analysis['Average_Purchase'] = customer_analysis['Average_Purchase'].round(2)
        
        print(customer_analysis.to_string(index=False))
        
        # Save to CSV
        customer_analysis.to_csv('loyal_customers.csv', index=False)
        print(f"Results saved to 'loyal_customers.csv'")
        
        return customer_analysis
    
    