import getpass
import os

from re import A
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()


if "GOOGLE_API_KEY" not in os.environ and not os.environ.get(
    "GOOGLE_API_KEY", ""
).startswith("AIza"):
    print("Google AI API key not found in environment variables.")
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")


@tool
def addition(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


@tool
def subtraction(a: int, b: int) -> int:
    """Subtracts two numbers."""
    return a - b


@tool
def multiplication(a: int, b: int) -> int:
    """Multiplies two numbers."""
    return a * b


tools = [addition, subtraction, multiplication]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ["GOOGLE_API_KEY"],
).bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(
        content="You are a helpful assistant that can perform calculations and answer questions."
    )
    response = llm.invoke([system_prompt] + list(state["messages"]))

    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last_message: BaseMessage = state["messages"][-1]
    # Check if last_message has 'tool_calls' attribute before accessing it
    if not isinstance(last_message, ToolMessage) and not hasattr(
        last_message, "tool_calls"
    ):
        return "end"
    if not isinstance(last_message, ToolMessage) and not getattr(
        last_message, "tool_calls", None
    ):
        return "end"
    return "continue"


graph = StateGraph(AgentState)
graph.add_node("agent", model_call)
graph.add_node("tools", ToolNode(tools=tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
graph.add_edge("tools", "agent")
agent = graph.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


def run():
    inputs = {
        "messages": [
            ("user", "Add 5 and 3, and 467 and 5567; then multiply the results.")
        ]
    }
    print_stream(agent.stream(inputs, stream_mode="values"))


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
