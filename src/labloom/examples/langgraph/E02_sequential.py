from email import message
from typing import Dict, TypedDict, List
from unittest import result
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    """
    Represents the state of an agent in the state graph.
    This is a simple example state that can be extended with more complex data.
    """

    name: str
    age: str
    final: str


def first_node(state: AgentState) -> AgentState:
    """
    A simple state function that processes a list of integers and returns their sum.
    """
    state["final"] = f"Hey {state['name']}!"
    return state


def second_node(state: AgentState) -> AgentState:
    """
    A simple state function that processes a list of integers and returns their sum.
    """
    state["final"] += f" You are {state['age']} years old."
    return state


# Create a StateGraph
graph = StateGraph(AgentState)
graph.add_node("first", first_node)
graph.add_node("second", second_node)
graph.add_edge("first", "second")
graph.set_entry_point("first")
graph.set_finish_point("second")

app = graph.compile()


def run():
    print(app.get_graph().draw_mermaid())
    result = app.invoke(
        {"name": input("Enter your name: "), "age": input("Enter your age: ")}
    )
    print(result["final"])


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
