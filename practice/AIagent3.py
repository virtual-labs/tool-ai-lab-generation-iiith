from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a : int, b : int):
    """This is an addition function"""
    return a + b

tools = [add]

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0).bind_tools(tools)

def model_call(state : AgentState) -> AgentState:
    system_prompt = SystemMessage(content = 
        "You are an AI assistant."
    )           
    response = model.invoke([system_prompt] + state["messages"])
    return {"messages" : [response]}

def should_continue(state : AgentState): 
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    
    
graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

    
graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent", 
    should_continue,
    {
        "continue" : "tools",
        "end" : END,
    },
)

graph.add_edge("tools", "our_agent")

app = graph.compile()

result = app.invoke({"messages": "Add 3 + 4. Add 4 + 0"})
print(result["messages"])

