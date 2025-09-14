
import os
import requests

class FinancialAPI:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ALPHAVANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("AlphaVantage API key must be provided.")

    def get_stocks(self, symbol: str):
        """Fetch daily time series data for a given stock symbol."""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        if not response.ok:
            raise ValueError("Failed to get AlphaVantage data.")
        return response.json()
