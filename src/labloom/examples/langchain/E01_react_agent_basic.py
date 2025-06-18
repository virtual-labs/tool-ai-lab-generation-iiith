import os
import getpass
from re import search
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, tool, AgentType
from langchain_community.tools import DuckDuckGoSearchResults


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

@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Returns the current system time in the specified format."""
    from datetime import datetime
    return datetime.now().strftime(format)

search_tool = DuckDuckGoSearchResults()

agent = initialize_agent(
    tools=[search_tool, get_system_time],
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)


def run():
    print(agent.get_graph().draw_mermaid())
    result = agent.invoke({"input": input("Enter your query: ")})
    print(result["output"])


if __name__ == "__main__":
    run()
    # Uncomment the line below to run in interactive mode
    # agent.interactive()
