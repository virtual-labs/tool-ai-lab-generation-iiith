import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyDtIftiUGFBL9w3DV_YqmdU_eI9hpg6Sno"

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# Define a dummy tool
def multiply_numbers(numbers: str) -> str:
    num_list = [int(x) for x in numbers.split()]
    result = 1
    for num in num_list:
        result *= num
    return f"The product is {result}."

# Register the tool
tools = [
    Tool(
        name="MultiplyNumbers",
        func=multiply_numbers,
        description="Multiplies a list of numbers provided as a string separated by spaces."
    )
]

# Initialize Gemini chat model
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

# Create an agent with the tool
agent = initialize_agent(
    tools=tools,                   # List of tools
    llm=llm,                       # LLM instance
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Agent type
    verbose=True                   # Show reasoning steps
)

# Run the agent with a task
response = agent.run("Multiply the numbers 3 5 7")

# Display result
print(response)
