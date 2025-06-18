from email import message
from typing import TypedDict, List
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    """
    Represents the state of an agent in the state graph.
    This is a simple example state that can be extended with more complex data.
    """

    name: str
    values: List[int]
    result: str


def process_values(state: AgentState) -> AgentState:
    """
    A simple state function that processes a list of integers and returns their sum.
    """
    state["result"] = (
        f"Hey {state['name']}, the sum of your values is {sum(state['values'])}!"
    )
    return state


# Create a StateGraph
graph = StateGraph(AgentState)
graph.add_node("processor", process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile()


def run():
    print(app.get_graph().draw_mermaid())
    result = app.invoke(
        {
            "name": input("Enter your name: "),
            "values": [
                int(x)
                for x in input("Enter a list of numbers (comma-separated): ").split(",")
            ],
        }
    )
    print(result["result"])


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
