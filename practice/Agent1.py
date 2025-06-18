from typing import Dict, TypedDict
from langgraph.graph import StateGraph
from IPython.display import Image, display
 
 # We build state with a class, (shared data structure), 
 # and that keeps track of all information
class AgentState(TypedDict):
    message : str
     
# Nodes are normal python functions
#input is state, and output is state
def greeting_node(state: AgentState) -> AgentState:
    """Simple node that adds a greeting message"""
    
    state['message'] = "Hey" + state['message'] + ", how is your day?"
    
    return state

# Build a graph using the nodes using StateGraph, 
# The parameter passed is the state schema
# Make sure to store it in a variable
graph = StateGraph(AgentState)

#add node(key (can be anything), name of function)
graph.add_node("greeter", greeting_node)

graph.set_entry_point("greeter")
graph.set_finish_point("greeter")

# Remember to compile with variable
app = graph.compile()

# Draw LangGraph diagram
# TODO: see why image is not displaying
display(Image(app.get_graph().draw_mermaid_png()))


result = app.invoke({"message" : "Bob"})

print(result['message'])

    