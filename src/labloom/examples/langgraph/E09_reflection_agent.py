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
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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

generation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a twitter techie influencer assistant tasked with writing excellent and viral twitter posts."
         "Generate the best twitter post possible for the user's request."
         "If the user provides critique, respond with revised version of the previous attempts."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a viral twitter influencer grading a tweet. Generate critique and recommendations for the user's tweet."
         "Always provide detailed recommendations, including request length, virality, style, etc."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ["GOOGLE_API_KEY"],
)

generate_chain = generation_prompt | llm
reflect_chain = reflection_prompt | llm


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def generate_tweet(state: AgentState) -> AgentState:
    response = generate_chain.invoke(
        {
            "messages": state["messages"],
        }
    )
    return {
        "messages": list(state["messages"]) + [AIMessage(content=response.content)],
    }

def reflect_tweet(state: AgentState) -> AgentState:
    response = reflect_chain.invoke(
        {
            "messages": state["messages"],
        }
    )
    return {
        "messages": list(state["messages"]) + [HumanMessage(content=response.content)],
    }

def should_continue(state: AgentState) -> str:
    messages = list(state["messages"])
    if len(messages) > 2:
        return "end"
    return "reflect"


graph = StateGraph(AgentState)
graph.add_node("generate", generate_tweet)
graph.add_node("reflect", reflect_tweet)
graph.add_edge(START, "generate")
graph.add_edge("reflect", "generate")
graph.add_conditional_edges("generate", should_continue, {
    "end": END,
    "reflect": "reflect",
})
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
    inputs = {"messages": [HumanMessage(content="Write a viral tweet about IIITH's SERC")]}
    print_stream(agent.stream(inputs, stream_mode="values"))


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
