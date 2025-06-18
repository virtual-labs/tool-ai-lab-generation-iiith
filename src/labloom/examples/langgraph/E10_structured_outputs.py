import getpass
import os

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from dotenv import load_dotenv

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
)

class Place(BaseModel):
    """Information about a place."""
    name: str = Field(..., description="The name of the place.")
    capital: str = Field(..., description="The capital city of the place.")
    population: int = Field(..., description="The population of the place.")
    area: float = Field(..., description="The area of the place in square kilometers.")

place_llm = llm.with_structured_output(Place)

class Joke(TypedDict):
    """A joke with a setup and punchline."""
    setup: Annotated[str, ..., "The setup of the joke."]
    punchline: Annotated[str, ..., "The punchline of the joke."]
    rating: Annotated[float|None, ..., "A rating for the joke, from 1 to 5."]

joke_llm = llm.with_structured_output(Joke) # type: ignore



def run():
    print(place_llm.invoke("Tell me about Andhra Pradesh, India."))
    print(joke_llm.invoke("Tell me a joke about Python programming."))


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
