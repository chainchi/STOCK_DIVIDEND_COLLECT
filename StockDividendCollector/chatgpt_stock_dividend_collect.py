import requests
import datetime

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


if __name__ == "__main__":
    stock_input = input("Enter stock codes with suffix, separated by commas (e.g., 2330.TW,00772B.TWO): ").strip().upper()
    stock_list = [s.strip() for s in stock_input.split(',') if s.strip()]

    year_input = input("Enter year (YYYY): ").strip()
    if not year_input.isdigit():
        print("Invalid year. Must be numeric.")
    else:
        year = int(year_input)
        summary = {}  # to store total dividend per stock

        for stock_code in stock_list:
            # Validate stock code format
            if '.' not in stock_code:
                print(f"Invalid format: {stock_code}. Must include '.' like 2330.TW or 00772B.TWO")
                continue
            code, suffix = stock_code.rsplit('.', 1)
            if not code.isalnum() or suffix not in ['TW', 'TWO']:
                print(f"Invalid stock code: {stock_code}. Format example: 2330.TW or 00772B.TWO")
                continue

            dividends, total = fetch_dividend_yahoo(stock_code, year)
            summary[stock_code] = total

            if dividends:
                print(f"\nDividend info for stock {stock_code} in {year}:")
                for d in dividends:
                    print(f"Date: {d['Date']}, Cash Dividend: {d['Amount']:.2f}")
                print(f"Total Dividend for {stock_code} in {year}: {total:.2f}\n")

        # Print summary
        if summary:
            print("===== Dividend Summary =====")
            for stock, total in summary.items():
                print(f"{stock}: Total Dividend = {total:.2f}")
            print("============================")
