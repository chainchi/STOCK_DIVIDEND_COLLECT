# Stock Dividend Collector

A Python script to fetch, calculate, and display stock dividend information, including the latest price and yield, in a clean, formatted table.

## Features

- Fetches historical cash dividend data from Yahoo Finance for a given year.
- Retrieves the latest stock price and its trading date.
- Calculates the annual dividend yield.
- Uses a local `stock_list.txt` file to map stock codes to their Chinese names.
- Displays the final summary in a well-organized, aligned table.

## Prerequisites

- Python 3.x
- The `requests` library. Install it via pip:
  ```bash
  pip install requests
  ```

## Setup

### `stock_list.txt`

Before running the script, you must create a `stock_list.txt` file in the same directory as the script (`StockDividendCollector/`). This file is used to look up the Chinese name for each stock code.

The format for each line is:
`[Chinese Name] [Stock Code]`

**Example `stock_list.txt`:**
```
中信金 2891.TW
國泰永續高股息 00878.TW
台積電 2330.TW
```

## How to Use

This is a command-line tool. Run it from your terminal and provide the stock codes and the year as arguments.

- Navigate to the project's root directory.
- Use the `-s` or `--stocks` flag to provide one or more stock codes (separated by spaces).
- Use the `-y` or `--year` flag to specify the year.

**Example Command:**
```bash
python StockDividendCollector/chatgpt_stock_dividend_collect.py -s 2891.TW 00878.TW -y 2023
```

## Example Output

The script will process the stocks and display a summary table like this:

```
===== Dividend Summary =====
Stock     Name            Price (2025-11-24)  Dividend  Yield
-------------------------------------------------------------
2891.TW   中信金                       44.10      1.00   2.27%
00878.TW  國泰永續高股息               20.56      1.24   6.03%
============================
```

*(Note: The Chinese names may appear garbled in some terminals that do not fully support UTF-8 display.)*
