import os
from typing import Optional, Dict, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel
import requests
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from langchain_core.messages import ToolMessage

ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")

class StockInput(BaseModel):

    symbol: str
    """
    The companies symbol in the stock market. EX: 'APPL'
    """
    tool_call_id: Annotated[str, InjectedToolCallId]

@tool("stock_data", args_schema=StockInput, return_direct=True)
def stock_data(symbol: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> dict:
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
    
    return Command(update={
        "stocks": stocks,
        "symbol": symbol,
        "messages": [ToolMessage("Successfully looked up data information", tool_call_id=tool_call_id)]
    })