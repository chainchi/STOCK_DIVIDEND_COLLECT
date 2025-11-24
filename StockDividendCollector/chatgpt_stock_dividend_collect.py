import requests
import datetime
import argparse
import os

def load_stock_names(filepath):
    """
    Loads stock names from a file into a dictionary.
    The file format is expected to be: Chinese Name <whitespace> Stock Code
    """
    stock_names = {}
    if not os.path.exists(filepath):
        print(f"Warning: Stock name file not found at {filepath}")
        return stock_names

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Replace full-width spaces with regular spaces and split
            parts = line.replace('　', ' ').split()
            if len(parts) >= 2:
                stock_code = parts[-1]
                # The name is everything except the last part
                chinese_name = ' '.join(parts[:-1]).strip().replace('"', '')
                stock_names[stock_code] = chinese_name
    return stock_names

def get_latest_price_yahoo(stock_code_with_suffix):
    """
    Fetch the latest trading price and time for a stock from Yahoo Finance.
    Returns a tuple of (price, date_string).
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_code_with_suffix}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        
        chart = data.get('chart', {}).get('result', [])
        if not chart or 'meta' not in chart[0]:
            print(f"No price data found for stock {stock_code_with_suffix}.")
            return None, None

        price = chart[0]['meta'].get('regularMarketPrice')
        timestamp = chart[0]['meta'].get('regularMarketTime')
        price_date = "N/A"
        if timestamp:
            price_date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        
        return price, price_date

    except Exception as e:
        print(f"Error fetching price for {stock_code_with_suffix}: {e}")
        return None, None

def fetch_dividend_yahoo(stock_code_with_suffix, year):
    """
    Fetch historical cash dividends for a TW stock (TWSE or OTC) from Yahoo Finance JSON.
    Returns a tuple: (list of dividends, total amount)
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_code_with_suffix}"
    params = {
        "range": "max",
        "interval": "1d",
        "events": "div"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()

        chart = data.get('chart', {}).get('result', [])
        if not chart:
            print(f"No data found for stock {stock_code_with_suffix}.")
            return [], 0.0

        div_events = chart[0].get('events', {}).get('dividends', {})
        if not div_events:
            print(f"No dividend info found for stock {stock_code_with_suffix} in {year}.")
            return [], 0.0

        filtered = []
        total_dividend = 0.0
        for div in div_events.values():
            date_ts = div['date']
            date = datetime.datetime.fromtimestamp(date_ts)
            if date.year == year:
                amount = div['amount']
                filtered.append({
                    "Date": date.strftime("%Y-%m-%d"),
                    "Amount": amount
                })
                total_dividend += amount

        return filtered, total_dividend

    except requests.exceptions.HTTPError as http_err:
        if r.status_code == 404:
            print(f"Error: Stock {stock_code_with_suffix} not found on Yahoo Finance (404).")
        else:
            print(f"HTTP error occurred: {http_err}")
        return [], 0.0
    except Exception as e:
        print(f"Error fetching data for {stock_code_with_suffix}: {e}")
        return [], 0.0

def str_display_width(s):
    """Calculates the display width of a string, accounting for wide characters."""
    width = 0
    for char in s:
        # CJK Unified Ideographs, half/full-width forms
        if ('\u4e00' <= char <= '\u9fff' or
            '\u3000' <= char <= '\u303f' or
            '\uff00' <= char <= '\uffef'):
            width += 2
        else:
            width += 1
    return width

def main(args):
    year = args.year
    stock_list = args.stocks
    summary = {}
    
    # Load Chinese names from the local file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    stock_name_file = os.path.join(script_dir, 'stock_list.txt')
    stock_names_map = load_stock_names(stock_name_file)

    for stock_code in stock_list:
        print(f"Processing {stock_code}...")
        # Validate stock code format
        if '.' not in stock_code:
            print(f"Invalid format: {stock_code}. Must include '.' like 2330.TW or 00772B.TWO")
            continue
        
        # Look up the Chinese name from the map
        chinese_name = stock_names_map.get(stock_code, "N/A")
        
        dividends, total = fetch_dividend_yahoo(stock_code, year)
        price, price_date = get_latest_price_yahoo(stock_code)
        summary[stock_code] = (total, chinese_name, price, price_date)

        if dividends:
            print(f"\nDividend info for stock {stock_code} ({chinese_name}) in {year}:")
            for d in dividends:
                print(f"Date: {d['Date']}, Cash Dividend: {d['Amount']:.2f}")
            print(f"Total Dividend for {stock_code} in {year}: {total:.2f}\n")

    # --- Start of new summary printing logic ---
    if summary:
        print("\n===== Dividend Summary =====")
        
        # Find the price date for the header from the first available entry
        price_header_date = ""
        for _, _, _, p_date in summary.values():
            if p_date and p_date != "N/A":
                price_header_date = p_date
                break
        
        price_header_text = f"Price ({price_header_date})" if price_header_date else "Price"

        # Prepare data and calculate max widths
        header_data = {"stock": "Stock", "name": "Name", "price": price_header_text, "dividend": "Dividend", "yield": "Yield"}
        print_data = [header_data]
        
        max_widths = {key: str_display_width(value) for key, value in header_data.items()}

        for stock, (total, name, price, price_date) in summary.items():
            price_str = f"{price:.2f}" if price is not None else "N/A"
            dividend_str = f"{total:.2f}"
            yield_str = "N/A"
            if total > 0 and price is not None and price > 0:
                yield_val = (total / price) * 100
                yield_str = f"{yield_val:.2f}%"

            row = {"stock": stock, "name": name, "price": price_str, "dividend": dividend_str, "yield": yield_str}
            print_data.append(row)

            for key, value in row.items():
                # We use the header key for max_widths, as 'price' header is dynamic
                max_widths[key] = max(max_widths[key], str_display_width(value))

        # Print header
        header_line = (
            f"{header_data['stock']:<{max_widths['stock']}}  "
            f"{header_data['name']:<{max_widths['name']}}  "
            f"{header_data['price']:>{max_widths['price']}}  "
            f"{header_data['dividend']:>{max_widths['dividend']}}  "
            f"{header_data['yield']:>{max_widths['yield']}}"
        )
        print(header_line)
        print("-" * str_display_width(header_line))

        # Print data rows (skipping header in data)
        for row in print_data[1:]:
            stock_padding = max_widths['stock'] - str_display_width(row['stock'])
            name_padding = max_widths['name'] - str_display_width(row['name'])
            
            line = (
                f"{row['stock']}{' ' * stock_padding}  "
                f"{row['name']}{' ' * name_padding}  "
                f"{row['price']:>{max_widths['price']}}  "
                f"{row['dividend']:>{max_widths['dividend']}}  "
                f"{row['yield']:>{max_widths['yield']}}"
            )
            print(line)
            
        print("============================")
    # --- End of new summary printing logic ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch stock dividends and get their Chinese names from a local file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-s', '--stocks', 
        nargs='+', 
        required=True,
        help="One or more stock codes with suffix (e.g., 2330.TW 0050.TW)"
    )
    parser.add_argument(
        '-y', '--year', 
        type=int, 
        required=True,
        help="The year to fetch dividend data for (e.g., 2023)"
    )
    
    args = parser.parse_args()
    main(args)
