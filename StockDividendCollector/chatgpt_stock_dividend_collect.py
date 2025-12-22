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

def get_price_change_yahoo(stock_code_with_suffix, year):
    """
    Fetches the first and last trading day prices for a given year and calculates the percentage change.
    """
    start_date = int(datetime.datetime(year, 1, 1).timestamp())
    end_date = int(datetime.datetime(year, 12, 31).timestamp())

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_code_with_suffix}"
    params = {
        "period1": start_date,
        "period2": end_date,
        "interval": "1d"
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()

        chart = data.get('chart', {}).get('result', [])
        if not chart or 'indicators' not in chart[0]:
            return None

        quotes = chart[0]['indicators']['quote'][0]
        close_prices = quotes.get('close', [])
        
        # Filter out None values which can appear for non-trading days
        valid_prices = [p for p in close_prices if p is not None]

        if len(valid_prices) < 2:
            return None # Not enough data to compare

        first_price = valid_prices[0]
        last_price = valid_prices[-1]

        price_change = ((last_price - first_price) / first_price) * 100
        return price_change

    except Exception as e:
        print(f"Error fetching price change for {stock_code_with_suffix}: {e}")
        return None

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

def generate_yield_chart(summary, year):
    """Generates and prints a text-based bar chart for dividend yields."""
    
    print(f"\n=== Dividend Yield Chart ({year}) ===")
    
    chart_data = {}
    max_yield = 0.0
    for stock, (total, name, price, price_date, shares, price_change, _, _, _, _) in summary.items(): # Added placeholders
        yield_val = 0.0
        if total > 0 and price is not None and price > 0:
            yield_val = (total / price) * 100
        
        if yield_val > 0:
            chart_data[stock] = {"yield": yield_val, "name": name, "price_change": price_change}
            if yield_val > max_yield:
                max_yield = yield_val

    if not chart_data or max_yield == 0:
        print("No yield data available to generate a chart.")
        print("================================================================")
        return

    # Calculate max width for the label part (e.g., "00878.TW (Name)")
    max_label_width = 0
    for stock, data in chart_data.items():
        label = f"{stock} ({data['name']})"
        max_label_width = max(max_label_width, str_display_width(label))

    max_bar_width = 40 # Reduced to make space for the new text
    
    # Sort stocks by yield
    sorted_stocks = sorted(chart_data.items(), key=lambda item: item[1]['yield'], reverse=True)

    for stock, data in sorted_stocks:
        yield_val = data['yield']
        name = data['name']
        price_change = data['price_change']
        
        label = f"{stock} ({name})"
        label_padding = max_label_width - str_display_width(label)
        
        bar_length = int((yield_val / max_yield) * max_bar_width)
        bar = '#' * bar_length

        price_change_str = ""
        if price_change is not None:
            price_change_str = f"(Change: {price_change:+.2f}%)"
        
        print(f"{label}{' ' * label_padding}                             | {bar} {yield_val:.2f}% {price_change_str}")
        
    print("==========================================================")

def generate_combined_performance_chart(summary, year):
    """Generates and prints a text-based bar chart for combined yield and price change."""
    
    print(f"\n=== Combined Performance Chart ({year}) ===")
                 
    chart_data = {}
    max_combined_performance = 0.0
    for stock, (total, name, price, price_date, shares, price_change, _, _, _, _) in summary.items(): # Added placeholders
        yield_val = 0.0
        if total > 0 and price is not None and price > 0:
            yield_val = (total / price) * 100
        
        # Only include stocks that have a positive yield (and are thus in the first chart)
        if yield_val > 0:
            combined_performance = None
            if price_change is not None:
                combined_performance = yield_val + price_change
            
            if combined_performance is not None:
                chart_data[stock] = {"performance": combined_performance, "name": name}
                if abs(combined_performance) > max_combined_performance:
                    max_combined_performance = abs(combined_performance)

    if not chart_data or max_combined_performance == 0:
        print("No combined performance data available to generate a chart.")
        print("================================================================")
        return

    # Calculate max width for the label part
    max_label_width = 0
    for stock, data in chart_data.items():
        label = f"{stock} ({data['name']})"
        max_label_width = max(max_label_width, str_display_width(label))

    max_bar_width = 50 # characters
    
    # Sort stocks by combined performance
    sorted_stocks = sorted(chart_data.items(), key=lambda item: item[1]['performance'], reverse=True)

    for stock, data in sorted_stocks:
        performance_val = data['performance']
        name = data['name']
        
        label = f"{stock} ({name})"
        label_padding = max_label_width - str_display_width(label)
        
        bar_length = int((abs(performance_val) / max_combined_performance) * max_bar_width)
        
        bar_char = '*'
        if performance_val < 0:
            bar_char = '-' # Use a different char for negative performance, or direction
        
        bar = bar_char * bar_length
        
        print(f"{label}{' ' * label_padding}                             | {bar} {performance_val:+.2f}%") # Use + to show sign for positive numbers
        
    print("==========================================================")

def generate_subtracted_performance_chart(summary, year):
    """Generates a bar chart for yield rate minus price change."""
    
    print(f"\n=== Yield Rate minus Price Change Rate Chart ({year}) ===")
                  
    chart_data = {}
    max_subtracted_performance = 0.0
    for stock, (total, name, price, price_date, shares, price_change, _, _, _, _) in summary.items(): # Added placeholders
        yield_val = 0.0
        if total > 0 and price is not None and price > 0:
            yield_val = (total / price) * 100
        
        # Only include stocks that have a positive yield
        if yield_val > 0:
            subtracted_performance = None
            if price_change is not None:
                subtracted_performance = yield_val - price_change
            
            if subtracted_performance is not None:
                chart_data[stock] = {"performance": subtracted_performance, "name": name}
                if abs(subtracted_performance) > max_subtracted_performance:
                    max_subtracted_performance = abs(subtracted_performance)

    if not chart_data or max_subtracted_performance == 0:
        print("No data available to generate a chart.")
        print("=============================================================")
        return

    max_label_width = 0
    for stock, data in chart_data.items():
        label = f"{stock} ({data['name']})"
        max_label_width = max(max_label_width, str_display_width(label))

    max_bar_width = 50
    
    sorted_stocks = sorted(chart_data.items(), key=lambda item: item[1]['performance'], reverse=True)

    for stock, data in sorted_stocks:
        performance_val = data['performance']
        name = data['name']
        
        label = f"{stock} ({name})"
        label_padding = max_label_width - str_display_width(label)
        
        bar_length = int((abs(performance_val) / max_subtracted_performance) * max_bar_width)
        
        bar_char = '~'
        if performance_val < 0:
            bar_char = '-'
        
        bar = bar_char * bar_length
        
        print(f"{label}{' ' * label_padding}                             | {bar} {performance_val:+.2f}%")
        
    print("==========================================================")

def main(args):
    year = args.year
    stock_list_from_args = args.stocks 
    input_file_path = args.input_file

    summary = {} # Initialize summary here
    final_stock_codes_to_process = []
    stock_names_from_input_file = {}
    shares_map = {}
    bought_price_map = {}
    low_rate_threshold_map = {} # Renamed for clarity
    high_rate_threshold_map = {} # Renamed for clarity

    # Load master Chinese names from the local file (stock_list.txt)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    master_stock_name_file = os.path.join(script_dir, 'stock_list.txt')
    master_stock_names_map = load_stock_names(master_stock_name_file)

    if input_file_path:
        # If an input file is provided, read codes from it
        try:
            with open(input_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.replace('　', ' ').split()
                    identified_stock_code = None
                    
                    # Find the stock code first
                    for part in parts:
                        if '.' in part and (part.endswith('.TW') or part.endswith('.TWO')):
                            identified_stock_code = part
                            break
                    
                    if identified_stock_code:
                        final_stock_codes_to_process.append(identified_stock_code)
                        
                        # Process all other parts
                        name_parts = []
                        numeric_parts = []
                        for part in parts:
                            if part == identified_stock_code:
                                continue
                            part = part.replace(',', '').strip()
                            if not part: continue

                            try:
                                numeric_parts.append(float(part))
                            except ValueError:
                                name_parts.append(part)

                        if name_parts:
                            stock_names_from_input_file[identified_stock_code] = ' '.join(name_parts).replace('"', '')

                        # Correctly assign numeric parts
                        shares_val, bought_price_val, thresh1, thresh2 = None, None, None, None
                        temp_numerics = list(numeric_parts)

                        # Find shares (must be an integer, assumes one per line)
                        for num in temp_numerics:
                            if num == int(num):
                                shares_val = int(num)
                                temp_numerics.remove(num)
                                break
                        
                        # Assign remaining floats
                        if temp_numerics: bought_price_val = temp_numerics.pop(0)
                        if temp_numerics: thresh1 = temp_numerics.pop(0)
                        if temp_numerics: thresh2 = temp_numerics.pop(0)

                        if shares_val is not None: shares_map[identified_stock_code] = shares_val
                        if bought_price_val is not None: bought_price_map[identified_stock_code] = bought_price_val
                        
                        # Correctly assign high and low thresholds
                        if thresh1 is not None and thresh2 is not None:
                            high_rate_threshold_map[identified_stock_code] = max(thresh1, thresh2)
                            low_rate_threshold_map[identified_stock_code] = min(thresh1, thresh2)
                        elif thresh1 is not None:
                            if thresh1 > 0: high_rate_threshold_map[identified_stock_code] = thresh1
                            else: low_rate_threshold_map[identified_stock_code] = thresh1
                    else:
                        print(f"Warning: Skipping line in input file, no valid stock code found: {line}")
                        
        except FileNotFoundError:
            print(f"Error: Input file not found: {input_file_path}")
            return
        except Exception as e:
            print(f"Error reading input file {input_file_path}: {e}")
            return
    elif stock_list_from_args:
        final_stock_codes_to_process = stock_list_from_args
    
    final_stock_names_map = master_stock_names_map.copy()
    final_stock_names_map.update(stock_names_from_input_file)

    for stock_code in final_stock_codes_to_process:
        print(f"Processing {stock_code}...")
        if '.' not in stock_code:
            print(f"Invalid format: {stock_code}. Must include '.' like 2330.TW or 00772B.TWO")
            continue
        
        chinese_name = final_stock_names_map.get(stock_code, "N/A")
        shares = shares_map.get(stock_code)
        bought_price = bought_price_map.get(stock_code)
        low_rate_threshold = low_rate_threshold_map.get(stock_code)
        high_rate_threshold = high_rate_threshold_map.get(stock_code)
        
        dividends, total = fetch_dividend_yahoo(stock_code, year)
        price, price_date = get_latest_price_yahoo(stock_code)
        price_change = get_price_change_yahoo(stock_code, year)
        
        summary[stock_code] = (total, chinese_name, price, price_date, shares, price_change, bought_price, low_rate_threshold, high_rate_threshold, dividends)

        if dividends:
            print(f"\nDividend info for stock {stock_code} ({chinese_name}) in {year}:")
            for d in dividends:
                print(f"Date: {d['Date']}, Cash Dividend: {d['Amount']:.2f}")
            print(f"Total Dividend for {stock_code} in {year}: {total:.2f}\n")

    if summary:
        print(f"\n=== Dividend Summary ({year}) ===")
                    
        price_header_date = ""
        # Update unpacking to ignore the new last element (dividends)
        for _, _, _, p_date, _, _, _, _, _, _ in summary.values():
            if p_date and p_date != "N/A":
                price_header_date = p_date
                break
        
        price_header_text = f"Price ({price_header_date})" if price_header_date else "Price"

        header_data = {
            "stock": "Stock", "name": "Name", "price": price_header_text, 
            "dividend": "Dividend", "yield": "Yield", "shares": "Shares", 
            "total_value": "Total Value", "net_pl": "P/L", "percent_pl": "P/L %",
            "signal": "Signal"
        }
        print_data = [header_data]
        
        max_widths = {key: str_display_width(value) for key, value in header_data.items()}

        for stock, (total, name, price, price_date, shares, price_change, bought_price, low_rate_threshold, high_rate_threshold, dividends_list) in summary.items():
            price_str = f"{price:.2f}" if price is not None else "N/A"
            dividend_str = f"{total:.2f}"
            yield_str = "N/A"
            if total > 0 and price is not None and price > 0:
                yield_val = (total / price) * 100
                yield_str = f"{yield_val:.2f}%"

            shares_str = str(shares) if shares is not None else ""
            total_value_str = ""
            if total > 0 and shares is not None:
                total_value = total * shares
                total_value_str = f"{total_value:,.2f}"

            net_pl_str = "N/A"
            percent_pl_str = "N/A"
            percent_pl = None
            if bought_price is not None and price is not None and shares is not None:
                net_pl = (price - bought_price) * shares
                net_pl_str = f"{net_pl:,.2f}"
                if bought_price > 0:
                    percent_pl = ((price - bought_price) / bought_price) * 100
                    percent_pl_str = f"{percent_pl:+.2f}%"
            
            signal_str = ""
            if percent_pl is not None:
                if high_rate_threshold is not None and percent_pl >= high_rate_threshold:
                    signal_str = "Take-Profit"
                elif low_rate_threshold is not None and percent_pl <= low_rate_threshold:
                    signal_str = "Cut-Loss"

            row = {
                "stock": stock, "name": name, "price": price_str, "dividend": dividend_str, 
                "yield": yield_str, "shares": shares_str, "total_value": total_value_str,
                "net_pl": net_pl_str, "percent_pl": percent_pl_str, "signal": signal_str
            }
            print_data.append(row)

            for key, value in row.items():
                max_widths[key] = max(max_widths.get(key, 0), str_display_width(str(value)))

        header_line = (
            f"{header_data['stock']:<{max_widths['stock']}}  "
            f"{header_data['name']:<{max_widths['name']}}  "
            f"{header_data['price']:>{max_widths['price']}}  "
            f"{header_data['dividend']:>{max_widths['dividend']}}  "
            f"{header_data['yield']:>{max_widths['yield']}}  "
            f"{header_data['shares']:>{max_widths['shares']}}  "
            f"{header_data['total_value']:>{max_widths['total_value']}}  "
            f"{header_data['net_pl']:>{max_widths['net_pl']}}  "
            f"{header_data['percent_pl']:>{max_widths['percent_pl']}}  "
            f"{header_data['signal']:<{max_widths['signal']}}"
        )
        print(header_line)
        print("-" * str_display_width(header_line))

        for row in print_data[1:]:
            stock_padding = max_widths['stock'] - str_display_width(row['stock'])
            name_padding = max_widths['name'] - str_display_width(row['name'])
            
            line = (
                f"{row['stock']}{' ' * stock_padding}  "
                f"{row['name']}{' ' * name_padding}  "
                f"{row['price']:>{max_widths['price']}}  "
                f"{row['dividend']:>{max_widths['dividend']}}  "
                f"{row['yield']:>{max_widths['yield']}}  "
                f"{row['shares']:>{max_widths['shares']}}  "
                f"{row['total_value']:>{max_widths['total_value']}}  "
                f"{row['net_pl']:>{max_widths['net_pl']}}  "
                f"{row['percent_pl']:>{max_widths['percent_pl']}}  "
                f"{row['signal']:<{max_widths['signal']}}"
            )
            print(line)
            
        print("===================================================================================")
        
        generate_yield_chart(summary, year)
        generate_combined_performance_chart(summary, year)
        generate_subtracted_performance_chart(summary, year)
        
        # --- JSON Output for Web Interface ---
        import json
        json_data = []
        for stock, vals in summary.items():
            # vals = (total, name, price, price_date, shares, price_change, bought_price, low, high, dividends)
            total, name, price, p_date, shares, p_change, b_price, low_t, high_t, dividends_list = vals
            
            yield_val = 0.0
            if total > 0 and price is not None and price > 0:
                yield_val = (total / price) * 100

            total_value = 0.0
            if price is not None and shares is not None:
                total_value = price * shares

            net_pl = 0.0
            percent_pl = 0.0
            if b_price is not None and price is not None and shares is not None:
                net_pl = (price - b_price) * shares
                if b_price > 0:
                    percent_pl = ((price - b_price) / b_price) * 100
            
            signal = ""
            if b_price is not None and price is not None:
                current_pl_p = percent_pl
                if high_t is not None and current_pl_p >= high_t:
                    signal = "Take-Profit"
                elif low_t is not None and current_pl_p <= low_t:
                    signal = "Cut-Loss"
            
            s_count = shares if shares else 0
            # Adjust dividend events to reflect real total profit (Amount * shares)
            adjusted_events = []
            for ev in dividends_list:
                adjusted_events.append({
                    "Date": ev["Date"],
                    "Amount": ev["Amount"] * s_count
                })

            json_data.append({
                "stock": stock,
                "name": name,
                "dividend": total,  # Dividend per share only
                "yield": yield_val,
                "price": price if price else 0,
                "price_date": p_date,
                "shares": s_count,
                "total_value": total_value,
                "net_pl": net_pl,
                "percent_pl": percent_pl,
                "signal": signal,
                "events": adjusted_events
            })
            
        print("\n---JSON_START---")
        print(json.dumps(json_data))
        print("---JSON_END---")
    # --- End of new summary printing logic ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch stock dividends and get their Chinese names from a local file or an input file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-y', '--year', 
        type=int, 
        required=True,
        help="The year to fetch dividend data for (e.g., 2023)"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-s', '--stocks', 
        nargs='+', # One or more arguments
        help="One or more stock codes with suffix (e.g., 2330.TW 0050.TW)"
    )
    group.add_argument(
        '-i', '--input-file', 
        type=str,
        help="Path to a text file containing stock codes (one per line, or in 'Name StockCode' format)."
    )
    
    args = parser.parse_args()
    main(args)
