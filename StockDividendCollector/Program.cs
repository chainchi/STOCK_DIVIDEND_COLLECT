using System;
using System.Net.Http;
using HtmlAgilityPack;
using System.Linq;
using System.Collections.Generic;
using System.Globalization;

namespace StockDividendCollector
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Enter the stock symbol (e.g., MSFT):");
            string stockSymbol = Console.ReadLine();

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

            Console.WriteLine($"Getting dividend information for {stockSymbol} in {year}...");

            var dividendData = GetDividendData(stockSymbol, year);

            if (dividendData.Any())
            {
                Console.WriteLine("Dividend Data:");
                foreach (var dividend in dividendData)
                {
                    Console.WriteLine($"Date: {dividend.Date.ToShortDateString()}, Dividend: {dividend.DividendAmount}");
                }
            }
            else
            {
                Console.WriteLine($"No dividend data found for {stockSymbol} in {year}.");
            }
        }

        static List<Dividend> GetDividendData(string stockSymbol, int year)
        {
            var dividends = new List<Dividend>();
            var url = $"https://finance.yahoo.com/quote/{stockSymbol}/history?period1={GetUnixTimestamp(new DateTime(year, 1, 1))}&period2={GetUnixTimestamp(new DateTime(year, 12, 31))}&interval=1d&filter=div&frequency=1d";
            
            var web = new HtmlWeb();
            HtmlDocument doc = null;
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
                        // Yahoo Finance often has an extra row for "Dividend" which can be identified by "Dividend" in the second column
                        if (cells.Count > 1 && cells[1].InnerText.Contains("Dividend"))
                        {
                            var dateText = cells[0].InnerText;
                            // The dividend amount is usually the first part of the text, e.g., "0.71 Dividend"
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

    public class Dividend
    {
        public DateTime Date { get; set; }
        public decimal DividendAmount { get; set; }
    }
}
