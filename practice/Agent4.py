from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    number1 : int
    operation: str
    number2 : int
    finalNumber : int
    
def adder(state:AgentState) -> AgentState:
    """Adds two numbers"""
    
    state['finalNumber'] = state['number1'] + state['number2']
    return state

def subtractor(state:AgentState) -> AgentState:
    """Subtracts two numbers"""
    
    state['finalNumber'] = state['number1'] - state['number2']
    return state

def decider_node(state : AgentState) -> AgentState:
    """This node will select the next node"""
    
    if state["operation"] == "+":
        return "addition_operation"
    
    elif state["operation"] == "-":
        return "subtraction_operation"
    

graph = StateGraph(AgentState)
graph.add_node("add_node", adder)
graph.add_node("subtract_node", subtractor)

# your input state will be your output state, 
# essentially a passthrough function
graph.add_node("router", lambda state:state)

graph.add_edge(START, "router")

# source, path_node, path map
# path map is in the form of dictionairy of edge : node
graph.add_conditional_edges(
    "router", 
    decider_node,
    {
        "addition_operation" : "add_node",
        "subtraction_operation" : "subtract_node"
    }
)

graph.add_edge("add_node", END)
graph.add_edge("subtract_node", END)

app = graph.compile()

result = app.invoke({"number1" : 3, "operation" : "-", "number2" : 5})
print(result) 