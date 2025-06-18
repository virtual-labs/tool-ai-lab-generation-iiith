from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    """
    Represents the state of an agent in the state graph.
    This is a simple example state that can be extended with more complex data.
    """

    number1: int
    number2: int
    operation: str
    finalNumber: int


def adder(state: AgentState) -> AgentState:
    """
    A simple state function that adds two numbers.
    """
    state["finalNumber"] = state["number1"] + state["number2"]
    return state


def subtractor(state: AgentState) -> AgentState:
    """
    A simple state function that subtracts two numbers.
    """
    state["finalNumber"] = state["number1"] - state["number2"]
    return state


def decide_next(state: AgentState) -> str:
    """
    A decision function that determines the next node based on the operation.
    """
    if state["operation"] == "+":
        return "addition"
    elif state["operation"] == "-":
        return "subtraction"
    else:
        raise ValueError("Invalid operation. Use '+' or '-'.")


# Create a StateGraph
graph = StateGraph(AgentState)
graph.add_node("adder", adder)
graph.add_node("subtractor", subtractor)
graph.add_node("router", lambda state: state)  # Router node to decide next step
graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router", decide_next, {"addition": "adder", "subtraction": "subtractor"}
)
graph.add_edge("adder", END)
graph.add_edge("subtractor", END)
app = graph.compile()


def run():
    print(app.get_graph().draw_mermaid())
    result = app.invoke(
        {
            "number1": int(input("Enter the first number: ")),
            "number2": int(input("Enter the second number: ")),
            "operation": input("Enter the operation (+ or -): "),
        }
    )
    print(result["finalNumber"])


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
