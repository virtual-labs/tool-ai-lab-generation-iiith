from typing import TypedDict
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    """
    Represents the state of an agent in the state graph.
    This is a simple example state that can be extended with more complex data.
    """

    name: str
    message: str


def greeting_node(state: AgentState) -> AgentState:
    """
    A simple state function that modifies the state to include a greeting message.
    """
    state["message"] = "Hey " + state["name"] + ", welcome to Labloom!"
    return state


# Create a StateGraph
graph = StateGraph(AgentState)
graph.add_node("greeter", greeting_node)
graph.set_entry_point("greeter")
graph.set_finish_point("greeter")

app = graph.compile()


def run():
    print(app.get_graph().draw_mermaid())
    result = app.invoke({"name": input("Enter your name: ")})
    print(result["message"])


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
