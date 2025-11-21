# Stock Dividend Collector

This project contains two tools for collecting stock dividend information.

## C# Dividend Collector (`StockDividendCollector`)

This is a .NET console application that fetches and displays dividend data for a given stock symbol and year. It now also retrieves the Chinese name of the stock.

### How to Run

1.  Navigate to the project directory.
2.  Run the application using the `dotnet run` command.
    ```sh
    dotnet run
    ```
3.  The application will prompt you to enter a stock symbol (e.g., 2330) and a year.

## Python Dividend Collector (`chatgpt_stock_dividend_collect.py`)

This is a Python script that fetches dividend data from Yahoo Finance and can optionally fetch the Chinese stock name using Selenium.

### Prerequisites

- Python 3
- Required libraries: `requests`, `selenium`
  ```sh
  pip install requests selenium
  ```
- A compatible version of ChromeDriver must be in the `bin/Debug/net9.0` directory.

### How to Run

This is a command-line tool. Run it from your terminal.

**Usage:**
```sh
python chatgpt_stock_dividend_collect.py --year <YEAR> --stocks <STOCK1.TW> [<STOCK2.TWO> ...] [--no-name]
```

**Arguments:**
*   `-y, --year`: (Required) The year to fetch dividend data for.
*   `-s, --stocks`: (Required) One or more stock codes with their exchange suffix (e.g., `.TW` for TWSE, `.TWO` for TPEx).
*   `--no-name`: (Optional) Use this flag to disable fetching the Chinese stock name. This makes the script run much faster as it does not need to launch a browser.

**Examples:**

*   **Get dividends and Chinese names:**
    ```sh
    python chatgpt_stock_dividend_collect.py --year 2025 --stocks 2330.TW 2454.TW
    ```

*   **Get dividends only (fast mode):**
    ```sh
    python chatgpt_stock_dividend_collect.py --year 2025 --stocks 2330.TW 2454.TW --no-name
    ```
