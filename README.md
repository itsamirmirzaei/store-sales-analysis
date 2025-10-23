# Sales Data Analysis
This project provides a Python-based tool for analyzing sales data from a CSV file. It performs data cleaning, derives new metrics, and generates various reports such as top-selling products, loyal customers, profitability trends, and sales by category and region. All outputs are saved as CSV files in the outputs directory.

# Features
Data Cleaning: Handles missing values, duplicates, and invalid data (e.g., negative quantities or prices).
Derived Metrics: Calculates profit, profit margin, average unit price, and date-based columns (year, month, quarter).
Analysis Reports:
Top-selling products
Loyal customers based on purchase frequency and total spending
Profitability trends over time
Sales analysis by product category
Sales analysis by region and month


Final Report: Generates a comprehensive summary of key metrics.
Output: All analysis results and logs are saved as CSV files in the outputs directory.

# Requirements
Python 3.8 or higher
Required Python packages (listed in requirements.txt):pandas>=2.0.0
numpy>=1.24.0

# Usage
Prepare a CSV file with sales data. The file should include columns like:
Sales or Revenue (numeric, sales amount)
Cost (numeric, cost of goods)
Quantity or Qty (numeric, number of items sold)
Date (date format, e.g., YYYY-MM-DD)
Optional: Product, Customer, Category, Region for specific analyses


Run the script with the path to your CSV file:python sales_analyzer.py --file path/to/your/csv/file.csv

If no file path is provided, the script defaults to data/sample - superstore.csv.
Check the outputs directory for the following CSV files:
analysis_log.csv: Detailed log of analysis steps and results
top_products.csv: Top-selling products
loyal_customers.csv: Loyal customers
profitability_trend.csv: Profitability trends over time
category_analysis.csv: Sales by product category
regional_monthly_sales.csv: Sales by region and month
region_summary.csv: Summary of sales by region
month_summary.csv: Summary of sales by month
final_sales_data.csv: Cleaned and enriched dataset
final_report.csv: Comprehensive final report



Console Output
The script only outputs the following to the console:

A message confirming that results are saved: Results saved to CSV files in 'outputs'
The final comprehensive report with key metrics (e.g., total sales, profit, etc.)

All other analysis details are saved in the analysis_log.csv file.
Example
python sales_analyzer.py --file data/sample - superstore.csv

Console Output:
==================================================
Final Comprehensive Report
==================================================
Metric                        Value
Total Transactions            1000
Total Sales Revenue           $1,234,567.89
Average Transaction Value     $1,234.57
Highest Single Transaction    $10,000.00
Lowest Single Transaction     $10.00
Total Profit                 $345,678.90
Average Profit per Transaction $345.68
Average Profit Margin         28.00%
Results saved to CSV files in 'outputs'

# Notes
Ensure the input CSV file has the required columns for full functionality. Missing columns may cause some analyses to be skipped (logged in analysis_log.csv).
If the date column format is not recognized, the script will log an error in analysis_log.csv.
For large CSV files, ensure sufficient memory is available, as the entire file is loaded into memory.

# Contributing
Feel free to submit issues or pull requests to improve the project. Suggestions for additional analyses or visualizations are welcome.
