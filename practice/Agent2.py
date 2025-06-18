from typing import Dict, TypedDict
from langgraph.graph import StateGraph

# REMEMBER: the values, name, and result are strings
class AgentState(TypedDict):
    values: list[int]
    name: str
    result: str
    
# We are storing the result in an element inside the 
# typed dictionairy
def process_values(state: AgentState) -> AgentState:
    """This function handles multiple different inputs"""
    
    state['result'] = f"HI there {state['name']}, your sum is {sum(state['values'])}"
    
    return state

graph = StateGraph(AgentState)
graph.add_node("processor", process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile()

# IMPORTANT: the parameters that can be set to NULL are the 
# the ones that are being assigned, not used
result = app.invoke({'values' : [1, 2, 3, 4], "name" : "Steve"})
print(result['result'])
