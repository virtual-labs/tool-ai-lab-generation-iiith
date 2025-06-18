import numbers
from turtle import st
from typing import List, TypedDict
import random
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    """
    Represents the state of an agent in the state graph.
    This is a simple example state that can be extended with more complex data.
    """

    name: str
    numbers: List[int]
    counter: int


def greeter(state: AgentState) -> AgentState:
    """
    A simple state function that greets the user.
    """
    state["name"] = input("Enter your name: ")
    print(f"Hello, {state['name']}!")
    return state


def random_node(state: AgentState) -> AgentState:
    """Generate a random number beterrn 1-10"""
    state["numbers"].append(random.randint(1, 10))
    state["counter"] += 1

    return state


def should_continue(state: AgentState) -> str:
    """
    A decision function that determines whether to continue based on the counter.
    """
    if state["counter"] < 5:
        return "continue"
    else:
        return "end"


# Create a StateGraph
graph = StateGraph(AgentState)
graph.add_node("greeter", greeter)
graph.add_node("random_node", random_node)
graph.add_edge("greeter", "random_node")

graph.add_conditional_edges(
    "random_node", should_continue, {"continue": "random_node", "end": END}
)
graph.set_entry_point("greeter")
app = graph.compile()


def run():
    print(app.get_graph().draw_mermaid())
    result = app.invoke({"name": "", "numbers": [], "counter": 0})
    print(result["numbers"])
    print(result["counter"])


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
