from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, TypedDict, Annotated, Sequence

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.ui import AnyUIMessage, ui_message_reducer, push_ui_message
from langchain_google_genai import ChatGoogleGenerativeAI


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]


async def stock(state: AgentState):
    class StockOutput(TypedDict):
        symbol: str

    stock: StockOutput = (
        await ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.6)
            .with_structured_output(StockOutput)
            .with_config({"tags": ["nostream"]})
            .ainvoke(state["messages"])
    )

    message = AIMessage(
        id=str(uuid.uuid4()),
        content=f"Here's the stock for {stock['symbol']}"
    )

    # Emit UI elements associated with the message
    push_ui_message("stock", stock, message=message)
    return { "messages": [message] }

workflow = StateGraph(AgentState)
workflow.add_node(stock)
workflow.add_edge("__start__", "stock")
graph = workflow.compile()