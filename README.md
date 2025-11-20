# Stock Dividend Collector

This project contains a Python script to fetch and display historical stock dividend information from Yahoo Finance.

## `chatgpt_stock_dividend_collect.py`

### Purpose

This script is a command-line tool for retrieving cash dividend data for Taiwanese stocks for a specified year.

### How to Use

1.  **Prerequisites:**
    *   You must have Python installed on your system.
    *   You need to install the `requests` library:
        ```bash
        pip install requests
        ```

2.  **Run the script:**
    *   Open a terminal or command prompt.
    *   Navigate to the directory containing the script:
        ```bash
        cd C:\Users\DONACHEN\source\repos\STOCK_DIVIDEND_COLLECT\StockDividendCollector
        ```
    *   Execute the script using Python:
        ```bash
        python chatgpt_stock_dividend_collect.py
        ```

3.  **Follow the prompts:**
    *   The script will first ask you to enter one or more stock codes. These must be valid Taiwanese stock tickers ending in `.TW` or `.TWO` (for OTC stocks). Separate multiple codes with a space.
        > **Enter stock codes (e.g., 2330.TW 8406.TWO):**
    *   Next, it will ask for the year you are interested in.
        > **Enter the year (e.g., 2023):**

### Expected Outcome

After you provide the inputs, the script will contact Yahoo Finance and print the dividend information for each stock.

**Example Output:**

```
--- Dividend information for 2330.TW in 2023 ---
Dividend Date: 2023-03-22, Dividend: 2.75
Dividend Date: 2023-06-21, Dividend: 2.75
Dividend Date: 2023-09-20, Dividend: 3.0
Dividend Date: 2023-12-20, Dividend: 3.0

Summary for 2330.TW in 2023:
Total Dividends: 11.5
```
