import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import argparse

class SalesAnalyzer:
    """Main class for sales data analysis"""
    
    def __init__(self, filepath):
        """Initialize the analyzer with data from CSV file
        
        Args:
            filepath (str): Path to the CSV file containing sales data
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found at: {filepath}. Current directory: {os.getcwd()}")
        self.df = pd.read_csv(filepath)
        self.original_rows = len(self.df)
        
        # Ensure outputs directory exists
        self.output_dir = 'outputs'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize log for storing analysis details
        self.log_data = {
            'Step': [],
            'Details': []
        }
        
        # Log initial data info
        self.log_data['Step'].append('Data Loading')
        self.log_data['Details'].append(f"Data loaded successfully: {self.original_rows} rows")
        
    def validate_columns(self, required_columns):
        """Validate if required columns exist in the dataset
        
        Args:
            required_columns (list): List of required column names or patterns
        """
        missing_cols = []
        for col in required_columns:
            if not any(col.lower() in c.lower() for c in self.df.columns):
                missing_cols.append(col)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    
    def display_basic_info(self):
        """Store basic information about the dataset in log"""
        info = []
        info.append(f"Dataset shape: {self.df.shape}")
        info.append(f"\nColumn Names and Types:\n{self.df.dtypes.to_string()}")
        info.append(f"\nFirst 10 rows:\n{self.df.head(10).to_string()}")
        info.append(f"\nBasic statistics:\n{self.df.describe().to_string()}")
        
        self.log_data['Step'].append('Basic Data Information')
        self.log_data['Details'].append('\n'.join(info))
        
    def clean_data(self):
        """Clean the dataset by handling missing values, duplicates, and invalid data"""
        # Check for missing values
        missing_values = self.df.isnull().sum()
        missing_info = missing_values[missing_values > 0].to_string()
        self.log_data['Step'].append('Missing Values')
        self.log_data['Details'].append(f"Missing values per column:\n{missing_info}")
        
        # Remove duplicates
        duplicates_before = self.df.duplicated().sum()
        self.df = self.df.drop_duplicates()
        self.log_data['Step'].append('Duplicates Removed')
        self.log_data['Details'].append(f"Duplicates removed: {duplicates_before}")
        
        # Handle missing values - fill numeric with median, categorical with mode
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                if self.df[col].dtype in ['float64', 'int64']:
                    self.df[col] = self.df[col].fillna(self.df[col].median())
                else:
                    mode_val = self.df[col].mode()
                    if not mode_val.empty:
                        self.df[col] = self.df[col].fillna(mode_val[0])
        
        # Remove rows with negative or zero quantities/prices (not profit)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if 'quantity' in col.lower() or 'price' in col.lower() or 'sales' in col.lower():
                self.df = self.df[self.df[col] > 0]
        
        rows_after_cleaning = len(self.df)
        self.log_data['Step'].append('Data Cleaning Summary')
        self.log_data['Details'].append(f"Rows after cleaning: {rows_after_cleaning}\nRows removed: {self.original_rows - rows_after_cleaning}")
    
    def add_derived_columns(self):
        """Add new columns with calculated metrics
        Assumes columns exist: Sales, Cost, Profit (or similar)
        """
        # Validate required columns
        try:
            self.validate_columns(['sales', 'cost', 'quantity', 'date'])
        except ValueError as e:
            self.log_data['Step'].append('Column Validation Error')
            self.log_data['Details'].append(str(e))
        
        # Try to find relevant columns (flexible column naming)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        cost_col = next((col for col in self.df.columns if 'cost' in col.lower()), None)
        profit_col = next((col for col in self.df.columns if 'profit' in col.lower()), None)
        quantity_col = next((col for col in self.df.columns if 'quantity' in col.lower() or 'qty' in col.lower()), None)
        
        log_info = []
        if sales_col and cost_col and not profit_col:
            # Calculate profit if not exists
            self.df['Profit'] = self.df[sales_col] - self.df[cost_col]
            profit_col = 'Profit'
            log_info.append("Profit column created")
            
        if sales_col and profit_col:
            self.df['Profit_Margin_Percentage'] = (self.df[profit_col] / self.df[sales_col] * 100).round(2)
            log_info.append("Profit Margin Percentage column created")
            
        if sales_col and quantity_col:
            # Calculate average price per unit
            self.df['Average_Unit_Price'] = (self.df[sales_col] / self.df[quantity_col]).round(2)
            log_info.append("Average Unit Price column created")
            
        # Try to parse date column and extract month/year
        date_col = next((col for col in self.df.columns if 'date' in col.lower()), None)
        if date_col:
            try:
                self.df[date_col] = pd.to_datetime(self.df[date_col], infer_datetime_format=True, errors='coerce')
                if self.df[date_col].isnull().all():
                    raise ValueError("All dates are invalid or could not be parsed")
                self.df['Year'] = self.df[date_col].dt.year
                self.df['Month'] = self.df[date_col].dt.month
                self.df['Month_Name'] = self.df[date_col].dt.month_name()
                self.df['Quarter'] = self.df[date_col].dt.quarter
                log_info.append("Date-based columns created (Year, Month, Month_Name, Quarter)")
            except Exception as e:
                log_info.append(f"Could not parse date column: {e}")
        
        log_info.append(f"New columns added. Total columns now: {len(self.df.columns)}")
        self.log_data['Step'].append('Derived Columns')
        self.log_data['Details'].append('\n'.join(log_info))
        
    def analyze_top_products(self, top_n=10):
        """Identify and analyze top-selling products
        
        Args:
            top_n (int): Number of top products to display
        """
        # Find product and sales columns
        product_col = next((col for col in self.df.columns if 'product' in col.lower() or 'item' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        quantity_col = next((col for col in self.df.columns if 'quantity' in col.lower() or 'qty' in col.lower()), None)
        
        if not product_col or not sales_col:
            self.log_data['Step'].append('Top Products Analysis')
            self.log_data['Details'].append("Required columns (product or sales) not found")
            return None
        
        # Aggregate by product
        agg_dict = {sales_col: 'sum'}
        if quantity_col:
            agg_dict[quantity_col] = 'sum'
        else:
            agg_dict['Count'] = 'count'  # Fallback to count if no quantity
        
        product_sales = self.df.groupby(product_col).agg(agg_dict).reset_index()
        product_sales = product_sales.sort_values(by=sales_col, ascending=False).head(top_n)
        product_sales.columns = ['Product', 'Total_Sales', 'Total_Quantity' if quantity_col else 'Count']
        
        # Round numeric columns
        for col in product_sales.select_dtypes(include=[np.number]).columns:
            product_sales[col] = product_sales[col].round(2)
        
        self.log_data['Step'].append('Top Products Analysis')
        self.log_data['Details'].append(f"Top {top_n} Best Selling Products:\n{product_sales.to_string(index=False)}")
        
        # Save to CSV
        try:
            product_sales.to_csv(os.path.join(self.output_dir, 'top_products.csv'), index=False)
            self.log_data['Step'].append('Top Products Save')
            self.log_data['Details'].append(f"Results saved to '{os.path.join(self.output_dir, 'top_products.csv')}'")
        except Exception as e:
            self.log_data['Step'].append('Top Products Save Error')
            self.log_data['Details'].append(f"Error saving to CSV: {e}")
        
        return product_sales
    
    def analyze_loyal_customer(self, top_n=10):
        """Identify loyal customers based on purchase frequency and total spending
        
        Args:
            top_n (int): Number of customers to display
        """
        # Find customer and sales columns
        customer_col = next((col for col in self.df.columns if 'customer' in col.lower() or 'client' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        
        if not customer_col or not sales_col:
            self.log_data['Step'].append('Loyal Customers Analysis')
            self.log_data['Details'].append("Required columns (customer or sales) not found")
            return None
        
        # Aggregate by customer
        customer_analysis = self.df.groupby(customer_col).agg(
            {
                sales_col: ['sum', 'count', 'mean']
            }
        ).reset_index()
        
        customer_analysis.columns = ['Customer', 'Total_Spending', 'Purchase_Count', 'Average_Purchase']
        customer_analysis = customer_analysis.sort_values(by='Total_Spending', ascending=False).head(top_n)
        
        # Round numeric columns
        for col in customer_analysis.select_dtypes(include=[np.number]).columns:
            customer_analysis[col] = customer_analysis[col].round(2)
        
        self.log_data['Step'].append('Loyal Customers Analysis')
        self.log_data['Details'].append(f"Top {top_n} Loyal Customers:\n{customer_analysis.to_string(index=False)}")
        
        # Save to CSV
        try:
            customer_analysis.to_csv(os.path.join(self.output_dir, 'loyal_customers.csv'), index=False)
            self.log_data['Step'].append('Loyal Customers Save')
            self.log_data['Details'].append(f"Results saved to '{os.path.join(self.output_dir, 'loyal_customers.csv')}'")
        except Exception as e:
            self.log_data['Step'].append('Loyal Customers Save Error')
            self.log_data['Details'].append(f"Error saving to CSV: {e}")
        
        return customer_analysis
    
    def analyze_profitability_trend(self):
        """Analyze profitability trends over time"""
        # Check if we have the required columns
        if 'Month_Name' not in self.df.columns or 'Profit' not in self.df.columns:
            self.log_data['Step'].append('Profitability Trend Analysis')
            self.log_data['Details'].append("Required columns (Month_Name or Profit) not found. Run add_derived_columns() first")
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
        
        # Round numeric columns
        for col in monthly_profit.select_dtypes(include=[np.number]).columns:
            if col not in ['Year', 'Month']:
                monthly_profit[col] = monthly_profit[col].round(2)
        
        self.log_data['Step'].append('Profitability Trend Analysis')
        self.log_data['Details'].append(monthly_profit.to_string(index=False))
        
        # Save to CSV
        try:
            monthly_profit.to_csv(os.path.join(self.output_dir, 'profitability_trend.csv'), index=False)
            self.log_data['Step'].append('Profitability Trend Save')
            self.log_data['Details'].append(f"Results saved to '{os.path.join(self.output_dir, 'profitability_trend.csv')}'")
        except Exception as e:
            self.log_data['Step'].append('Profitability Trend Save Error')
            self.log_data['Details'].append(f"Error saving to CSV: {e}")
        
        return monthly_profit
    
    def analyze_by_category(self):
        """Analyze total sales by product category"""
        # Find category and sales columns
        category_col = next((col for col in self.df.columns if 'category' in col.lower() or 'type' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        profit_col = 'Profit' if 'Profit' in self.df.columns else None
        
        if not category_col or not sales_col:
            self.log_data['Step'].append('Category Analysis')
            self.log_data['Details'].append("Required columns (category or sales) not found")
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
        total_sales = category_sales['Total_Sales'].sum()
        category_sales['Sales_Percentage'] = (category_sales['Total_Sales'] / total_sales * 100).round(2)
        
        # Round numeric columns
        for col in category_sales.select_dtypes(include=[np.number]).columns:
            if col != 'Transaction_Count':
                category_sales[col] = category_sales[col].round(2)
                
        self.log_data['Step'].append('Category Analysis')
        self.log_data['Details'].append(category_sales.to_string(index=False))
        
        # Save to CSV
        try:
            category_sales.to_csv(os.path.join(self.output_dir, 'category_analysis.csv'), index=False)
            self.log_data['Step'].append('Category Analysis Save')
            self.log_data['Details'].append(f"Results saved to '{os.path.join(self.output_dir, 'category_analysis.csv')}'")
        except Exception as e:
            self.log_data['Step'].append('Category Analysis Save Error')
            self.log_data['Details'].append(f"Error saving to CSV: {e}")
        
        return category_sales
        
    def analyze_by_region_and_month(self):
        """Analyze highest and lowest sales by region and month"""
        # Find region and sales columns
        region_col = next((col for col in self.df.columns if 'region' in col.lower() or 'state' in col.lower() or 'city' in col.lower()), None)
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        
        if not region_col or not sales_col:
            self.log_data['Step'].append('Region and Month Analysis')
            self.log_data['Details'].append("Required columns (region or sales) not found")
            return None
        
        # Aggregate by region and month
        regional_monthly = self.df.groupby([region_col, 'Month_Name', 'Month']).agg(
            {
                sales_col: 'sum',
            }
        ).reset_index()
        
        regional_monthly.columns = ['Region', 'Month_Name', 'Month', 'Total_Sales']
        regional_monthly = regional_monthly.sort_values(by=['Region', 'Month'])
        
        # Round numeric columns
        regional_monthly['Total_Sales'] = regional_monthly['Total_Sales'].round(2)
        
        self.log_data['Step'].append('Regional Monthly Sales')
        self.log_data['Details'].append(regional_monthly.to_string(index=False))
        
        # Find highest and lowest by region
        region_summary = self.df.groupby(region_col).agg(
            {
                sales_col: ['sum', 'max', 'min', 'mean']
            }
        ).reset_index()
        
        region_summary.columns = ['Region', 'Total_Sales', 'Highest_Sale', 'Lowest_Sale', 'Average_Sale']
        region_summary = region_summary.sort_values(by='Total_Sales', ascending=False)
        
        # Round numeric columns
        for col in region_summary.select_dtypes(include=[np.number]).columns:
            region_summary[col] = region_summary[col].round(2)
            
        self.log_data['Step'].append('Region Summary')
        self.log_data['Details'].append(region_summary.to_string(index=False))
        
        # Find highest and lowest by month
        month_summary = self.df.groupby(['Month', 'Month_Name']).agg(
            {
                sales_col: ['sum', 'max', 'min', 'mean']
            }
        ).reset_index()
        
        month_summary.columns = ['Month', 'Month_Name', 'Total_Sales', 'Highest_Sale', 'Lowest_Sale', 'Average_Sale']
        month_summary = month_summary.sort_values(by='Month')
        
        # Round numeric columns
        for col in month_summary.select_dtypes(include=[np.number]).columns:
            if col != 'Month':
                month_summary[col] = month_summary[col].round(2)
                
        self.log_data['Step'].append('Month Summary')
        self.log_data['Details'].append(month_summary.to_string(index=False))
        
        # Save to CSV
        try:
            regional_monthly.to_csv(os.path.join(self.output_dir, 'regional_monthly_sales.csv'), index=False)
            region_summary.to_csv(os.path.join(self.output_dir, 'region_summary.csv'), index=False)
            month_summary.to_csv(os.path.join(self.output_dir, 'month_summary.csv'), index=False)
            print(f"Results saved to CSV files in '{self.output_dir}'")
        except Exception as e:
            self.log_data['Step'].append('Region and Month Save Error')
            self.log_data['Details'].append(f"Error saving to CSV: {e}")
        
        return regional_monthly, region_summary, month_summary
    
    def general_final_report(self):
        """Generate a comprehensive final report with all key metrics"""
        print("\n" + "=" * 50)
        print("Final Comprehensive Report")
        print("=" * 50)
        
        sales_col = next((col for col in self.df.columns if 'sales' in col.lower() or 'revenue' in col.lower()), None)
        profit_col = 'Profit' if 'Profit' in self.df.columns else None
        
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
        try:
            self.df.to_csv(os.path.join(self.output_dir, 'final_sales_data.csv'), index=False)
            report_df.to_csv(os.path.join(self.output_dir, 'final_report.csv'), index=False)
            self.log_data['Step'].append('Final Report Save')
            self.log_data['Details'].append(f"Final cleaned and enriched dataset saved to '{os.path.join(self.output_dir, 'final_sales_data.csv')}'\nFinal report saved to '{os.path.join(self.output_dir, 'final_report.csv')}'")
        except Exception as e:
            self.log_data['Step'].append('Final Report Save Error')
            self.log_data['Details'].append(f"Error saving to CSV: {e}")
        
        # Save analysis log
        try:
            pd.DataFrame(self.log_data).to_csv(os.path.join(self.output_dir, 'analysis_log.csv'), index=False)
        except Exception as e:
            print(f"Error saving analysis log: {e}")
        
        return report_df
    
def main():
    """Main function to run the sales analysis"""
    parser = argparse.ArgumentParser(description='Sales Data Analysis')
    parser.add_argument('--file', default='data/sample - superstore.csv', help='Path to CSV file')
    args = parser.parse_args()
    
    # Initialize analyzer with CSV file
    analyzer = SalesAnalyzer(args.file)
    
    # Step 1: Store basic info
    analyzer.display_basic_info()
    
    # Step 2: Clean data
    analyzer.clean_data()
    
    # Step 3: Add derived columns
    analyzer.add_derived_columns()
    
    # Step 4: Analyze top products
    analyzer.analyze_top_products(top_n=10)
    
    # Step 5: Analyze loyal customers
    analyzer.analyze_loyal_customer(top_n=10)
    
    # Step 6: Analyze profitability trend
    analyzer.analyze_profitability_trend()
    
    # Step 7: Analyze by category
    analyzer.analyze_by_category()
    
    # Step 8: Analyze by region and month
    analyzer.analyze_by_region_and_month()
    
    # Step 9: Generate final report
    analyzer.general_final_report()
    
if __name__ == "__main__":
    main()