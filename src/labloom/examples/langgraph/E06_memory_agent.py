import getpass
import os

from re import A
from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()


if "GOOGLE_API_KEY" not in os.environ and not os.environ.get(
    "GOOGLE_API_KEY", ""
).startswith("AIza"):
    print("Google AI API key not found in environment variables.")
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ["GOOGLE_API_KEY"],
)


class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]


def processor(state: AgentState) -> AgentState:
    ai_msg = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=ai_msg.content))
    return state


graph = StateGraph(AgentState)
graph.add_node("processor", processor)
graph.add_edge(START, "processor")
graph.add_edge("processor", END)
agent = graph.compile()


def run():
    conversation_history: List[Union[HumanMessage, AIMessage]] = []
    user_input = input("Enter your message: ")
    while user_input.lower() != "exit":
        conversation_history.append(HumanMessage(content=user_input))
        state = {"messages": conversation_history}
        state = agent.invoke(state)
        print("AI response:", state["messages"][-1].content)
        user_input = input("Enter your message (or type 'exit' to quit): ")


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
