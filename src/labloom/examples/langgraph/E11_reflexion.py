from ast import List
import getpass
import json
import os
import datetime
from typing import Annotated, Sequence, TypedDict
from attr import has
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessageGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sqlalchemy import desc

load_dotenv()


if "GOOGLE_API_KEY" not in os.environ and not os.environ.get(
    "GOOGLE_API_KEY", ""
).startswith("AIza"):
    print("Google AI API key not found in environment variables.")
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ["GOOGLE_API_KEY"],
    verbose=True,
)

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="You are expert AI researcher.\n"
            "Current time is {current_time}.\n\n"
            "1. {first_instruction}\n"
            "2. Reflect and critique your answer. Be severe to maximize improvement and quality.\n"
            "3. After reflection, **list 1-3 search queries seperately** for research improvements. Do not include them in the reflections."
        ),
        MessagesPlaceholder(variable_name="messages"),
        SystemMessage(
            content="Answer the user's question above using the required format."
        ),
    ]
).partial(
    current_time=lambda: datetime.datetime.now().isoformat(),
)

class MoSCoWReflection(BaseModel):
    """Reflection model using MoSCoW method."""
    must_have: str = Field(..., description="What must be included in the answer.")
    should_have: str = Field(..., description="What should be included in the answer.")
    could_have: str = Field(..., description="What could be included in the answer.")
    wont_have: str = Field(..., description="What won't be included in the answer.")
    missing: str = Field(..., description="Critique of what is missing.")
    superfluous: str = Field(..., description="Critique of what is superfluous.")

class AnswerQuestion(BaseModel):
    """Answer the question"""
    answer: str = Field(..., description="~250 word detailed answer to the question.")
    search_queries: list[str] = Field(
        description="List of 1-3 search queries to improve the answer.",
    )
    reflection: MoSCoWReflection = Field(
        ...,
        description="Reflection on the answer using MoSCoW method.",
    )

class ReviseAnswer(AnswerQuestion):
    """Revise the answer based on the critique."""
    citations: list[str] = Field(
        description="Citations motivating the updated answer.",
    )

pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion, ReviseAnswer])


first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Provide a detailed ~250 word answer",
)

revisor_prompt_template = actor_prompt_template.partial(
    first_instruction=(
        "Revise your previous answer using the information\n"
        "\t - You should use the previous critique to add important information to your answer.\n"
        "\t - You MUST include numerical citations in your revised answer to ensure it can be verified.\n"
        "\t - Add a 'References' section to the bottom of your answer (which does not count towards the word limit). In the form of:\n"
        "\t\t- [1] https://example.com\n"
        "\t\t- [2] https://example.com\n"
        "\t - You should use the previous critique to remove superfluous information from your answer and make sure it is not more than 250 words.\n"
    )
)

first_responder_chain = first_responder_prompt_template | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion") | pydantic_parser
first_responder_chain = revisor_prompt_template | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer") | pydantic_parser


def tool_executor(state: list[BaseMessage]) -> list[BaseMessage]:
    search_tool = DuckDuckGoSearchResults(output_format="json")
    last_ai_message: AIMessage = state[-1]    # type: ignore

    if not hasattr(last_ai_message, "tool_calls") or not last_ai_message.tool_calls:
        return []

    tool_messages = []
    for tool_call in last_ai_message.tool_calls:
        if tool_call["name"] in ["AnswerQuestion", "ReviseAnswer"]:
            call_id = tool_call["id"]
            search_queries = tool_call["args"].get("search_queries", [])

            if isinstance(search_queries, str):
                search_queries = [search_queries]
            
            query_results = []
            for query in search_queries:
                if query:
                    search_results = search_tool.invoke({"query": query})
                    query_results.append(search_results["results"])
            tool_messages.append(
                ToolMessage(
                    content=json.dumps(query_results),
                    tool_call_id=call_id,
                )
            )
    return state


# Define the state graph for the first responder agent
graph = MessageGraph()

graph.add_node("draft", first_responder_chain)
graph.add_node("tool_executor", tool_executor)
graph.add_node("revisor", first_responder_chain)
graph.add_edge(START, "draft")
graph.add_edge("draft", "tool_executor")
graph.add_edge("tool_executor", "revisor")

def event_loop(state: list[BaseMessage]) -> str:
    count_tool_visits = sum(
        isinstance(msg, ToolMessage) for msg in state
    )
    MAX_TOOL_VISITS = 3  # Set a maximum number of tool visits
    if count_tool_visits > MAX_TOOL_VISITS:
        print("Maximum tool visits reached. Ending the conversation.")
        return END
    return "tool_executor"

graph.add_conditional_edges(
    "revisor",
    event_loop,
    {
        "tool_executor": "tool_executor",
        END: END,
    },
)

app = graph.compile()

def run():
    response = app.invoke(input("Enter your question: "))
    print("Response:", response["messages"][-1].tool_calls[0]["args"]["answer"])

if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
