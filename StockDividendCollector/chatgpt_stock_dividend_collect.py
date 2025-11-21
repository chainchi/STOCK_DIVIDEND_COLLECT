import requests
import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_stock_chinese_name(driver, stock_code):
    """
    Fetches the Chinese name of a stock using a pre-initialized Selenium driver.
    """
    detail_url = f"https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={stock_code}"
    try:
        driver.get(detail_url)
        # Wait up to 10 seconds for the title to be available
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
        title_text = driver.title.strip()
        
        parts = title_text.split()
        if len(parts) > 1 and parts[0] == stock_code:
            name_end_index = title_text.find(' - Goodinfo!')
            if name_end_index != -1:
                name_start_index = len(stock_code) + 1
                return title_text[name_start_index:name_end_index].strip()
                
    except Exception as e:
        print(f"Error fetching Chinese name for {stock_code} with Selenium: {e}")
        
    return "N/A"

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

def main(args):
    year = args.year
    stock_list = args.stocks
    fetch_names = not args.no_name
    summary = {}
    
    driver = None
    if fetch_names:
        # --- Selenium Driver Initialization ---
        driver_path = r".\bin\Debug\net9.0\chromedriver.exe"
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(executable_path=driver_path)
        try:
            print("Initializing browser for name fetching...")
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(60)
        except Exception as e:
            print(f"Failed to initialize Selenium driver: {e}")
            print("Continuing without fetching Chinese names.")
            fetch_names = False # Disable name fetching if driver fails
    
    try:
        for stock_code in stock_list:
            print(f"Processing {stock_code}...")
            # Validate stock code format
            if '.' not in stock_code:
                print(f"Invalid format: {stock_code}. Must include '.' like 2330.TW or 00772B.TWO")
                continue
            code, suffix = stock_code.rsplit('.', 1)
            if not code.isalnum() or suffix not in ['TW', 'TWO']:
                print(f"Invalid stock code: {stock_code}. Format example: 2330.TW or 00772B.TWO")
                continue

            chinese_name = "N/A"
            if fetch_names and driver:
                chinese_name = get_stock_chinese_name(driver, code)
            
            dividends, total = fetch_dividend_yahoo(stock_code, year)
            summary[stock_code] = (total, chinese_name)

            if dividends:
                print(f"\nDividend info for stock {stock_code} ({chinese_name}) in {year}:")
                for d in dividends:
                    print(f"Date: {d['Date']}, Cash Dividend: {d['Amount']:.2f}")
                print(f"Total Dividend for {stock_code} in {year}: {total:.2f}\n")
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()

    # Print summary
    if summary:
        print("===== Dividend Summary =====")
        for stock, (total, name) in summary.items():
            if fetch_names:
                print(f"{stock} ({name}): Total Dividend = {total:.2f}")
            else:
                print(f"{stock}: Total Dividend = {total:.2f}")
        print("============================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch stock dividends and optionally their Chinese names.",
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
    parser.add_argument(
        '--no-name', 
        action='store_true',
        help="Disable fetching of Chinese stock names to improve speed."
    )
    
    args = parser.parse_args()
    main(args)
