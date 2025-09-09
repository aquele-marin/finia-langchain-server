from __future__ import annotations

from operator import add
import uuid
from dataclasses import dataclass
from typing import Any, Dict, TypedDict, Annotated, Sequence

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.ui import AnyUIMessage, ui_message_reducer, push_ui_message
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode, tools_condition

from src.agent.tools.finance import stock_data

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
    stocks: dict
    symbol: str
    moving_average: bool


async def stock(state: AgentState):
    class StockOutput(TypedDict):
        stocks: dict
        symbol: str
        message: str

    prompt_template = ChatPromptTemplate([
            (
                "system",
                "You are a helpful assistant. You're provided a list of tools, and an input from the user.\n"
                + "Your job is to determine whether or not you have a tool which can handle the users input, or respond with plain text.",
            ),
            MessagesPlaceholder("human")
        ])

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    tools = [stock_data]
    model_with_tools = model.bind_tools(tools)
    model_with_tools = model_with_tools.with_config({ "tags": ["nostream"] })
    
    agent = prompt_template | model_with_tools

    answer = (
        await agent.ainvoke(state["messages"])
    )

    message = AIMessage(
        id=str(uuid.uuid4()),
        content=answer.content
    )

    # Emit UI elements associated with the message
    if len(answer.tool_calls) == 0:
        structured_output: StockOutput = {
            "stocks": state["stocks"],
            "symbol": state["symbol"],
            "message": answer.content
        }

        if state["moving_average"]:
            push_ui_message("stockScatterPlot", structured_output, message=message)
        else:
            push_ui_message("stock", structured_output, message=message)

    return { "messages": [answer]}

workflow = StateGraph(AgentState)
tool_node = ToolNode(tools=[stock_data])
workflow.add_node("stock", stock)
workflow.add_node("tools", tool_node)
workflow.add_edge("__start__", "stock")
workflow.add_conditional_edges("stock", tools_condition)
workflow.add_edge("tools", "stock")
graph = workflow.compile()