import os
from typing import Optional, Dict, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from src.infra.financialAPI import FinancialAPI

financial = FinancialAPI()

class StockInput(BaseModel):

    symbol: str
    """
    The companies symbol in the stock market. EX: 'APPL'
    """
    moving_average: bool
    """
    Filled according to the follow:
    True: ONLY if moving average is a good way to analyze the request
    False: Any other reason.
    """
    tool_call_id: Annotated[str, InjectedToolCallId]

@tool("stock_data", args_schema=StockInput, return_direct=True)
def stock_data(symbol: str, moving_average: bool, tool_call_id: Annotated[str, InjectedToolCallId]) -> dict:
    """
    Get daily stock prices of symbol

    Used to calculate moving average of stock prices and get stock data
    """
    response = financial.get_stocks(symbol)
    
    stocks = response["Time Series (Daily)"]
    
    return Command(update={
        "stocks": stocks,
        "symbol": symbol,
        "messages": [ToolMessage("Successfully looked up data information", tool_call_id=tool_call_id)],
        "moving_average": moving_average
    })