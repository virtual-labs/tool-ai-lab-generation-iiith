from typing import Dict, TypedDict
import random
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    name : str
    number : list[int]
    counter : int
    
def greeter(state : AgentState) -> AgentState:
    """Says Hi to the person"""
    
    state["name"] = f"Hi there, {state['name']}"
    state["counter"] = 0
    return state

def random_node(state:AgentState) -> AgentState:
    """Generates a random number from 0 to 10"""
    state["number"].append(random.randint(0, 10))
    state["counter"] += 1
    return state

def should_continue(state: AgentState) -> AgentState:
    """Function to decide what to do next"""
    if state["counter"] < 5:
        return "loop"
    else:
        return "exit"
    
graph = StateGraph(AgentState)

graph.add_node("greeting", greeter)
graph.add_node("random", random_node)
graph.add_edge(START, "greeting")
graph.add_edge("greeting", "random")

graph.add_conditional_edges(
    "random", 
    should_continue,
    {
        "loop" : "random",
        "exit" : END
    }
)

app = graph.compile()

result = app.invoke({"name" : "Karthik", "number" : []})
print(result)