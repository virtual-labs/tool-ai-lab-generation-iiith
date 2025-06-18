import getpass
import os

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


# This is the global variable to store document content
document_content = ""


@tool
def update(content: str) -> str:
    """Updates the document with the provided content."""
    global document_content
    document_content = content
    return f"Document updated successfully. The current content is:\n{document_content}"


@tool
def save(filename: str) -> str:
    """Saves the current document content to a text file and finish the process.
    If the filename does not end with '.txt', it appends '.txt' to the filename.
    If the file already exists, it will be overwritten.

    Args:
        filename (str): The name of the text file to save the document content.
    """
    global document_content
    if not filename.endswith(".txt"):
        filename += ".txt"
    try:
        with open(filename, "w") as file:
            file.write(document_content)
        return f"Document saved successfully to {filename}."
    except Exception as e:
        return f"Error saving document: {str(e)}"


tools = [update, save]
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
        content="""
You are Drafter, a helpful writing assistant. You are going to help the user update and modify a document.

- If the user want to update or modify the document, use the `update` tool with the complete updated content of the document.
- If the user wants to save and finish the process, use the `save` tool with the filename to save the document.
- Make sure to always show the current document state after modifications.

The current document content is: {document_content}
"""
    )
    if not state["messages"]:
        user_input = input(
            "I'm ready to help you update a document. What would you like to create or modify? "
        )
    else:
        user_input = input("What would you like to do with the document? ")

    user_input = HumanMessage(content=user_input)
    all_messages = [system_prompt] + list(state["messages"]) + [user_input]

    response = llm.invoke(all_messages)

    return {"messages": list(state["messages"]) + [user_input, response]}


def should_continue(state: AgentState) -> str:
    messages = list(state["messages"])
    if not messages:
        return "continue"
    for message in reversed(messages):
        # Check if last_message has 'tool_calls' attribute before accessing it
        if not isinstance(message, ToolMessage) and "saved" in message.content:
            print("Document saved successfully. Ending the process.")
            return "end"

    return "continue"


graph = StateGraph(AgentState)
graph.add_node("agent", model_call)
graph.add_node("tools", ToolNode(tools=tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("tools", should_continue, {"continue": "agent", "end": END})
graph.add_edge("agent", "tools")
agent = graph.compile()


def print_stream(stream):
    for s in stream:
        if not s["messages"]:
            continue
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


def run():
    inputs = {"messages": []}
    print_stream(agent.stream(inputs, stream_mode="values"))


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
