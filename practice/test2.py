
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Define prompt template with a variable
template = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple terms."
)

# Initialize Gemini chat model
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# Create a chain combining prompt template and model
chain = LLMChain(llm=llm, prompt=template)

# Run the chain with a value for 'topic'
response = chain.run(topic="blockchain")

# Display result
print(response)
