import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyDp4hgXtXDuDnRsOdOMtjSUsmI_GASLdRs"

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)

messages = [HumanMessage(content="Tell me a fun fact about the ocean.")]

response = llm(messages)

print(response.content)
