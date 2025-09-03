import os
from typing import Optional, Dict, Any
from typing_extensions import TypedDict
from pydantic import BaseModel
import requests
from langchain_core.tools import tool

ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")

class StockInput(BaseModel):

    symbol: str
    """
    The companies symbol in the stock market. EX: 'APPL'
    """

@tool("stock_data", args_schema=StockInput, return_direct=True)
def stock_data(symbol: str) -> dict:
    """
    Get daily stock prices of symbol
    """
    alphavantage_api_key = ALPHAVANTAGE_API_KEY
    if not alphavantage_api_key:
        raise ValueError("Missing ALPHAVANTAGE_API_KEY secre.")
    
    alphavantage_url = f"https://alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={alphavantage_api_key}"
    alphavantage_response = requests.get(alphavantage_url)
    if not alphavantage_response.ok:
        raise ValueError("Failed to get AlphaVantage data.")
    
    stocks = alphavantage_response.json()
    stocks = stocks["Time Series (Daily)"]
    
    return {
        "symbol": symbol,
        "stocks": stocks
    }