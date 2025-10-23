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
    
    def analyze_profitability_trend(self):
        """
        Analyze profitability trends over time
        """
        print("\n" + "=" * 50)
        print("Profitability Trend Analysis")
        print("=" * 50)
        
        # Check if we have the required columns
        if 'Month_Name' not in self.df.columns or 'Profit' not in self.df.columns:
            print("Required columns not found. Make sure to run add_derived_columns() first")
            return None
        
        # Aggregate by month
        monthly_profit = self.df.groupby(['Year', 'Month', 'Month_Name']).agg(
            {
                'Profit': ['sum', 'mean'],
                'Profit_Margin_Percentage': 'mean'
            }
        ).reset_index()
        
        monthly_profit.columns = ['Year', 'Month', 'Month_Name', 'Total_Profit', 'Average_Profit', 'Avg_Profit_Margin']
        monthly_profit = monthly_profit.sort_values(by=['Year', 'Month'])
        monthly_profit['Total_Profit'] = monthly_profit['Total_Profit'].round(2)
        monthly_profit['Average_Profit'] = monthly_profit['Average_Profit'].round(2)
        monthly_profit['Avg_Profit_Margin'] = monthly_profit['Avg_Profit_Margin'].round(2)
        
        print(monthly_profit.to_string(index=False))
        
        # Save to CSV
        monthly_profit.to_csv('profitability_trend.csv', index=False)
        print(f"\nResults saved to 'profitability_trend.csv'")
        
        return monthly_profit
    
    def analyze_by_category(self):
        """
        Analyze total sales by product  category
        """
        print("\n" + "=" * 50)
        print("Sales Analysis By Category")
        print("=" * 50)
        
        # Find category and sales columns
        category_col = next((col for col in self.df.columns if 'category' in col.lower() or 'type' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        profit_col = 'Profit' if 'profit' in self.df.columns else None
        
        if not category_col or not sales_col:
            print("Required columns not found")
            return None
        
        # Aggregate by category
        agg_dict = {sales_col: ['sum', 'mean', 'count']}
        if profit_col:
            agg_dict[profit_col] = 'sum'
            
        category_sales = self.df.groupby(category_col).agg(agg_dict).reset_index()
        
        # Flatten column names
        if profit_col:
            category_sales.columns = ['Category', 'Total_Sales', 'Average_Sales', 'Transaction_Count', 'Total_Profit']
        else:
            category_sales.columns = ['Category', 'Total_Sales', 'Average_Sales', 'Transaction_Count']
            
        category_sales = category_sales.sort_values(by='Total_Sales', ascending=False)
        
        # Calculate percentage of total sales
        category_sales['Sales_Percentage'] = (category_sales['Total_Sales'] / category_sales['Total_Sales'].sum() * 100).round(2)
        
        # Round numeric columns
        for col in category_sales.select_dtypes(include=[np.number]).columns:
            if col != 'Transaction_Count':
                category_sales[col] = category_sales[col],round(2)
                
        print(category_sales.to_string(index=False))
        
        # Save to CSV
        category_sales.to_csv('category_analysis.csv', index=False)
        print(f"\nResults saved to 'category_analysis.csv'")
        
        return category_sales
        
    def analyze_be_region_and_month(self):
        """
        Analyze highest and lowest sales by region and month 
        """
        print("\n" + "=" * 50)
        print("Sales Analysis By Region And Month")
        print("=" * 50)
        
        # Find region and sales columns
        region_col = next((col for col in self.df.columns if 'region' in col.lower() or 'state' in col.lower() or 'city' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        
        if not region_col or not sales_col:
            print("Required columns not found")
            return None
        
        # Aggregate by region and month
        regional_monthly = self.df.groupby([region_col, 'Month_Name', 'Month']).agg(
            {
                sales_col: 'sum',
            }
        ).reset_index()
        
        regional_monthly.columns = ['Region', 'Month_Name', 'Month', 'Total_Sales']
        regional_monthly = regional_monthly.sort_values(by=['Region', 'Month'])
        
        print("\nRegional Monthly Sales: ")
        print(regional_monthly.to_string(index=False))
        
        # Find highest and lowest by region
        print("\n" + "=" * 50)
        print("Highest And Lowest By Region")
        print("=" * 50)
        
        region_summary = self.df.groupby(region_col).agg(
            {
                sales_col: ['sum', 'max', 'min', 'mean']
            }
        ).reset_index()
        
        region_summary.columns = ['Region', 'Total_Sales', 'Highest_Sale', 'Lowest_Sale', 'Average_Sale']
        region_summary = region_summary.sort_values(by='Total_Sales', ascending=False)
        
        for col in region_summary.select_dtypes(include=[np.number]).columns:
            region_summary[col] = region_summary[col].round(2)
            
        print(region_summary.to_string(index=False))
        
        # Find highest and lowest by month
        print("\n" + "=" * 50)
        print("Highest And Lowest By Month")
        print("=" * 50)
        
        month_summary = self.df.groupby(['Month', 'Month_Name']).agg(
            {
                sales_col: ['sum', 'max', 'min', 'mean']
            }
        ).reset_index()
        
        month_summary.columns = ['Month', 'Month_Name', 'Total_Sale','Highest_Sale', 'Lowest_Sale', 'Average_Sale']
        month_summary = month_summary.sort_values(by='Month')
        
        for col in month_summary.select_dtypes(include=[np.number]).columns:
            if col != 'Month':
                month_summary[col] = month_summary[col].round(2)
                
        print(month_summary.to_string(index=False))
        
        # Save To CSV
        regional_monthly.to_csv('regional_monthly_sales.csv', index=False)
        region_summary.to_csv('region_summary.csv', index=False)
        month_summary.to_csv('  month_summary.csv', index=False)
        print(f"\nResults saved to CSV files")
        
        return regional_monthly, region_summary, month_summary
    
    def general_final_report(self):
        """
        Generate a comprehensive final report with all key metrics
        """
        print("\n" + "=" * 50)
        print("Final Comprehensive Report")
        print("=" * 50)
        
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        profit_col = 'Profit' if 'profit' in self.df.columns else None
        
        report = {
            'Metric': [],
            'Value': []
        }
        
        # Overall statistics
        report['Metric'].append('Total Transactions')
        report['Value'].append(len(self.df))
        
        if sales_col:
            report['Metric'].append('Total Sales Revenue')
            report['Value'].append(f"${self.df[sales_col].sum():,.2f}")
            
            report['Metric'].append('Average Transaction Value')
            report['Value'].append(f"${self.df[sales_col].mean():,.2f}")
            
            report['Metric'].append('Highest Single Transaction')
            report['Value'].append(f"${self.df[sales_col].max():,.2f}")
            
            report['Metric'].append('Lowest Single Transaction')
            report['Value'].append(f"${self.df[sales_col].min():,.2f}")
            
        if profit_col:
            report['Metric'].append('Total Profit')
            report['Value'].append(f"${self.df[profit_col].sum():,.2f}")
            
            report['Metric'].append('Average Profit per Transaction')
            report['Value'].append(f"${self.df[profit_col].mean():,.2f}")
            
            if 'Profit_Margin_Percentage' in self.df.columns:
                report['Metric'].append('Average Profit Margin')
                report['Value'].append(f"{self.df['Profit_Margin_Percentage'].mean():.2f}%")
                
        report_df = pd.DataFrame(report)
        print(report_df.to_string(index=False))
        
        # Save the cleaned and enriched dataset
        self.df.to_csv('final_sales_data.csv', index=False)
        print(f"\nFinal cleaned and enriched dataset saved to 'final_sales_data.csv'")
        
        # Save th report
        report_df.to_csv('final_report.csv', index=False)
        print(f"Final report saved to 'final_report.csv'")
        
        return report_df
    
    