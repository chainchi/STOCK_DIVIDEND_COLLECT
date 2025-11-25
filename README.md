# Stock Dividend Collector

A Python script to fetch, calculate, and display stock dividend information, including the latest price and various performance metrics, in a clean, formatted command-line output.

## Features

- Fetches historical cash dividend data from Yahoo Finance for a specified year.
- Retrieves the latest stock price and its trading date.
- Calculates the annual dividend yield.
- Calculates the annual price change percentage (first trading day to last trading day of the year).
- Displays a main summary table with stock code, name, current price (with date), total dividend, yield, optional shares owned, and calculated total dividend value.
- Generates a text-based bar chart for Dividend Yield, showing price change alongside.
- Generates a text-based bar chart for Combined Performance (`Yield + Price Change`).
- Generates a text-based bar chart for Yield vs. Price Change (`Yield - Price Change`).
- Supports reading stock codes and optional share counts from a custom input file or directly from command-line arguments.
- Uses an optional `stock_list.txt` file for Chinese name lookups, which can be overridden by names in an input file.

## Prerequisites

- Python 3.x
- The `requests` library. Install it via pip:
  ```bash
  pip install requests
  ```

## Setup

### `stock_list.txt` (Optional for Chinese Names)

A `stock_list.txt` file can be placed in the same directory as the script (`StockDividendCollector/`). This file is used to provide Chinese names for stock codes. If not provided, or if a stock is not found in it, "N/A" will be used.

The format for each line is:
`[Chinese Name] [Stock Code]`

**Example `stock_list.txt`:**
```
中信金 2891.TW
國泰永續高股息 00878.TW
台積電 2330.TW
```

### Input File (for Stock Codes and Shares)

You can provide an input file (e.g., `my_portfolio.txt`) with a list of stocks to process. This file can also optionally include the Chinese name and the number of shares you own.

The script intelligently parses each line. It looks for a stock code (e.g., `XXXX.TW` or `XXXX.TWO`), and if an integer is present, it considers it as shares. Any remaining text is treated as the Chinese name.

**Example Input File (`my_portfolio.txt`):**
```
# Comments are ignored
2891.TW 中信金 1000  # Stock code, name, and shares
00878.TW 2000         # Stock code and shares
國泰永續高股息 00878.TW # Name first, then stock code (shares would be optional)
0050.TW 元大0050      # Stock code and name
2330.TW              # Just stock code
```

## How to Use

This is a command-line tool. Run it from your terminal and provide the required arguments.

- Navigate to the project's root directory.
- You **must** specify the year using `-y` or `--year`.
- You **must** provide stock codes either directly via the command line (`-s` or `--stocks`) or from an input file (`-i` or `--input-file`). You cannot use both `-s` and `-i` at the same time.

### Using Command-Line Stocks

```bash
python StockDividendCollector/chatgpt_stock_dividend_collect.py -s 2891.TW 00878.TW -y 2023
```

### Using an Input File

```bash
python StockDividendCollector/chatgpt_stock_dividend_collect.py -i StockDividendCollector/my_portfolio.txt -y 2023
```
*(Replace `StockDividendCollector/my_portfolio.txt` with the actual path to your file.)*

## Example Output

The script will process the stocks and display a summary table followed by various performance charts:

```
=== Dividend Summary (2023) ===
Stock     Name            Price (2025-11-24)  Dividend  Yield  Shares  Total Value
-----------------------------------------------------------------------------------
2891.TW   中信金                       44.10      1.00  2.27%    1000     1,000.03
00878.TW  國泰永續高股息               20.56      1.24  6.03%    2000     2,480.00
0050.TW   元大0050                   59.55      1.12  1.89%
2330.TW   N/A                      1375.00     11.50  0.84%
===================================================================================

=== Dividend Yield Chart (2023) ===
00878.TW (國泰永續高股息)             | ######################################## 6.03% (Change: +34.73%)
2891.TW (中信金)                      | ############### 2.27% (Change: +27.99%)
0050.TW (元大0050)                    | ############### 1.89% (Change: +14.88%)
2330.TW (N/A)                         | ####### 0.84% (Change: +20.35%)
==========================================================

=== Combined Performance Chart (2023) ===
00878.TW (國泰永續高股息)             | ************************************************** +40.77%
2891.TW (中信金)                      | ************************************* +30.26%
2330.TW (N/A)                         | ************************* +21.19%
0050.TW (元大0050)                    | ************************ +16.77%
==========================================================

=== Yield vs. Price Change Chart (2023) ===
0050.TW (元大0050)                    | ~~~~~~ -13.00%
2330.TW (N/A)                         | ~~~~~~~~~~~~~~~~~~ -19.51%
00878.TW (國泰永續高股息)             | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -28.70%
2891.TW (中信金)                      | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -25.72%
==========================================================
```
*(Note: The Chinese names may appear garbled in some terminals that do not fully support UTF-8 display. Bar lengths and values are illustrative.)*
