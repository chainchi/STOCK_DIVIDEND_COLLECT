using System;
using System.Net.Http;
using HtmlAgilityPack;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;

#nullable enable

namespace StockDividendCollector
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Enter the stock symbol (e.g., 2330):");
            string? stockSymbol = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(stockSymbol))
            {
                Console.WriteLine("Stock symbol cannot be empty.");
                return;
            }

            int year;
            while (true)
            {
                Console.WriteLine("Enter the year (e.g., 2023):");
                if (int.TryParse(Console.ReadLine(), out year))
                {
                    break;
                }
                else
                {
                    Console.WriteLine("Invalid year. Please enter a valid number.");
                }
            }

            string chineseName = GetStockChineseName(stockSymbol);
            Console.WriteLine($"Getting dividend information for {stockSymbol} ({chineseName}) in {year}...");

            var dividendData = GetDividendData(stockSymbol, year);

            var stockInfo = new StockInfo
            {
                Symbol = stockSymbol,
                ChineseName = chineseName,
                Dividends = dividendData
            };

            if (stockInfo.Dividends.Any())
            {
                Console.WriteLine("Dividend Data:");
                foreach (var dividend in stockInfo.Dividends)
                {
                    Console.WriteLine($"Date: {dividend.Date.ToShortDateString()}, Dividend: {dividend.DividendAmount}");
                }
            }
            else
            {
                Console.WriteLine($"No dividend data found for {stockSymbol} ({stockInfo.ChineseName}) in {year}.");
            }
        }

        static string GetStockChineseName(string stockSymbol)
        {
            try
            {
                var url = $"https://goodinfo.tw/tw/StockInfo.asp?stock_id={stockSymbol}";
                var web = new HtmlWeb();
                var doc = web.Load(url);

                var titleNode = doc.DocumentNode.SelectSingleNode("//title");
                if (titleNode != null)
                {
                    string titleText = titleNode.InnerText;
                    // The format is usually "STOCK_ID STOCK_NAME - Goodinfo! Taiwan Stock Information"
                    var parts = titleText.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                    if (parts.Length > 1)
                    {
                        // The name is typically the second part, right after the stock symbol.
                        return parts[1];
                    }
                }
            }
            catch (Exception ex)
            {
                // If any error occurs (e.g., network issue, parsing error), return a default message.
                Console.WriteLine($"Could not retrieve Chinese name for {stockSymbol}: {ex.Message}");
            }

            return "N/A";
        }


        static List<Dividend> GetDividendData(string stockSymbol, int year)
        {
            var dividends = new List<Dividend>();
            // Adjust the symbol for Yahoo Finance if it's a Taiwanese stock
            string yahooSymbol = stockSymbol.EndsWith(".TW") ? stockSymbol : $"{stockSymbol}.TW";
            var url = $"https://finance.yahoo.com/quote/{yahooSymbol}/history?period1={GetUnixTimestamp(new DateTime(year, 1, 1))}&period2={GetUnixTimestamp(new DateTime(year, 12, 31))}&interval=1d&filter=div&frequency=1d";
            
            var web = new HtmlWeb();
            HtmlDocument? doc = null;
            try
            {
                doc = web.Load(url);
            }
            catch (HttpRequestException httpEx)
            {
                Console.WriteLine($"Network error: {httpEx.Message}. Could not retrieve data for {stockSymbol}.");
                return dividends;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while loading the page: {ex.Message}");
                return dividends;
            }
            
            if (doc == null)
            {
                return dividends;
            }

            var table = doc.DocumentNode.SelectSingleNode("//table[contains(@class, 'W(100%) M(0)')]");
            if (table != null)
            {
                var rows = table.SelectNodes(".//tr[contains(@class, 'BdT Bdc($seperatorColor)')]");
                if (rows != null)
                {
                    foreach (var row in rows)
                    {
                        var cells = row.SelectNodes(".//td").ToList();
                        if (cells.Count > 1 && cells[1].InnerText.Contains("Dividend"))
                        {
                            var dateText = cells[0].InnerText;
                            var dividendText = cells[1].InnerText.Split(' ')[0];

                            if (DateTime.TryParse(dateText, out DateTime date) && decimal.TryParse(dividendText, NumberStyles.Any, CultureInfo.InvariantCulture, out decimal dividendAmount))
                            {
                                dividends.Add(new Dividend { Date = date, DividendAmount = dividendAmount });
                            }
                        }
                    }
                }
            }
            return dividends;
        }

        static long GetUnixTimestamp(DateTime date)
        {
            return (long)(date.ToUniversalTime() - new DateTime(1970, 1, 1)).TotalSeconds;
        }
    }

    public class StockInfo
    {
        public string Symbol { get; set; } = string.Empty;
        public string ChineseName { get; set; } = string.Empty;
        public List<Dividend> Dividends { get; set; } = new List<Dividend>();
    }

    public class Dividend
    {
        public DateTime Date { get; set; }
        public decimal DividendAmount { get; set; }
    }
}
