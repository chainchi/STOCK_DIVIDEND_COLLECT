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

A Python script that fetches historical dividend data, current prices, and calculates profit/loss and yield for Taiwanese stocks from Yahoo Finance.

### Prerequisites

- Python 3
- Required libraries: `requests`, `pandas`
  ```sh
  pip install requests pandas
  ```
- An optional `stock_list.txt` file in the same directory can be used to provide Chinese names for stock codes.

### How to Run

This is a command-line tool. You can run it by providing a list of stocks directly or by using an input file.

**Usage:**
```sh
# Using an input file
python chatgpt_stock_dividend_collect.py --year <YEAR> --input-file <PATH_TO_FILE>

# Providing stocks directly
python chatgpt_stock_dividend_collect.py --year <YEAR> --stocks <STOCK1.TW> [<STOCK2.TWO> ...]
```

**Arguments:**
*   `-y, --year`: (Required) The year to fetch dividend data for.
*   `-i, --input-file`: (Recommended) Path to a text file containing your stock portfolio.
*   `-s, --stocks`: Alternatively, one or more stock codes with their exchange suffix (e.g., `.TW` for TWSE, `.TWO` for TPEx).

### Input File Format

The script works best with an `--input-file`. The file should be a plain text file where each line represents one stock. The format for each line is flexible:

`[Name] <Stock Code> [Shares] [Bought Price] [Threshold 1] [Threshold 2]`

-   `<Stock Code>`: **Required.** The stock ticker with its suffix (e.g., `2330.TW`).
-   `[Name]`: (Optional) The name of the stock.
-   `[Shares]`: (Optional) The number of shares you own (as an integer). Required for calculating Net P/L.
-   `[Bought Price]`: (Optional) The price at which you bought the stock. Required for all P/L and Signal calculations.
-   `[Threshold 1]` & `[Threshold 2]`: (Optional) Your high and low P/L percentage thresholds for the "Signal" column. For example, `50` for a +50% take-profit signal and `-10` for a -10% cut-loss signal. The order does not matter; the script will correctly identify the high and low values.

**Example `my_stocks.txt`:**
```
# This is a comment and will be ignored
台積電 2330.TW 1000 550.0 50 -10
中信金 2891.TW 42000 35.03 30 -5
元大台灣50 0050.TW
```

### Output

The script produces a summary table with the following columns:
*   **Stock**: The stock code.
*   **Name**: The stock name.
*   **Price**: The latest market price.
*   **Dividend**: The total cash dividend for the specified year.
*   **Yield**: The current dividend yield based on the latest price.
*   **Shares**: Number of shares owned.
*   **Total Value**: Total value of dividends for the shares owned.
*   **P/L**: Net profit or loss based on your bought price.
*   **P/L %**: Percentage profit or loss.
*   **Signal**: Displays "Take-Profit" or "Cut-Loss" if the P/L % crosses your defined thresholds.

It also generates several text-based charts in the console to visualize yield and performance.