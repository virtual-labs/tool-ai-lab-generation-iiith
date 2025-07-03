import dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()


class BaseAgent:
    llm = None
    prompt_enhancer_llm = None
    enhanced_prompt = None

    def __init__(self, role: str, basic_prompt: str, context: str = ""):
        self.role = role
        self.basic_prompt = basic_prompt
        self.context = context
        self.rag_enabled = False
        self.document_store = None

    def _extract_text_content(self, response):
        """
        Extract text content from various response types (string, dict, AIMessage, etc.)
        This centralizes the text extraction logic for all agents.
        """
        # If it's a string already, return it
        if isinstance(response, str):
            return response
        
        # If it's a dict with 'text' key
        if isinstance(response, dict) and 'text' in response:
            return response['text']
        
        # If it's a LangChain message object with content attribute
        if hasattr(response, 'content'):
            return response.content
        
        # If it has a __str__ method, use it as a fallback
        return str(response)

    def set_llm(self, llm):
        self.llm = llm

    def set_prompt_enhancer_llm(self, llm):
        self.prompt_enhancer_llm = llm
        
    def enable_rag(self, document_store):
        """Enable RAG functionality with the given document store"""
        self.rag_enabled = True
        self.document_store = document_store
        
        # Import here to avoid circular imports
        from rag.config import RAGConfig
        self.rag_config = RAGConfig
        return self
        
    def disable_rag(self):
        """Disable RAG functionality"""
        self.rag_enabled = False
        return self
        
    def is_rag_enabled(self):
        """Check if RAG is enabled"""
        return self.rag_enabled and self.document_store is not None

    def enhance_prompt(self):
        if  self.prompt_enhancer_llm is None:
            raise ValueError("Prompt enhancer LLM is not set.")

        enhanced_prompt_template = (
            "You are an expert prompt engineer for the role of '{role}'.\n\n"
            "The basic prompt that needs enhancing is:\n"
            "{basic_prompt}\n\n"
            "Using the above details, refine and improve the basic prompt by providing clear instructions, suggestions, and guidelines "
            "on how to approach the task effectively. Ensure the enhanced prompt is actionable and provides hints on what the agent should expect, "
            "but do not include any content that is part of the context since i will send it again\n\n"
        )

        prompt = PromptTemplate(
            input_variables=["role", "basic_prompt", "context"],
            template=enhanced_prompt_template
        )

        # Use RunnableSequence: prompt | llm
        chain = prompt | self.prompt_enhancer_llm
        enhanced_prompt_result = chain.invoke({
            "role": self.role,
            "basic_prompt": self.basic_prompt,
            "context": self.context
        })
        # Extract text content properly
        self.enhanced_prompt = self._extract_text_content(enhanced_prompt_result)
        return self.enhanced_prompt

    def get_output(self):
        if not self.llm:
            raise ValueError("LLM is not set.")

        # If RAG is enabled, use the RAG-enhanced output method
        if self.is_rag_enabled():
            return self.get_output_with_rag()
            
        # Standard output without RAG
        base_prompt = self.enhanced_prompt if self.enhanced_prompt else self.basic_prompt

        final_prompt_template = (
            "You are an expert in {role}.\n\n"
            "{context}\n\n"
            "Here is the task given to you: \n"
            "{base_prompt}\n"
        )

        prompt = PromptTemplate(
            input_variables=["role", "context", "base_prompt"],
            template=final_prompt_template
        )

        # Use RunnableSequence: prompt | llm
        chain = prompt | self.llm
        output = chain.invoke({
            "role": self.role,
            "context": self.context,
            "base_prompt": base_prompt
        })
        # Extract text content properly
        return self._extract_text_content(output)
        
    def get_output_with_rag(self, user_query: str = None):
        """Get output enhanced with RAG"""
        if not self.llm:
            raise ValueError("LLM is not set.")
        
        if not self.is_rag_enabled():
            raise ValueError("RAG is not enabled.")
        
        # Import here to avoid circular imports
        from rag.rag_agent import RAGAgent
        
        # Create a RAGAgent with the same configuration
        rag_agent = RAGAgent(self.role, self.basic_prompt, self.document_store)
        rag_agent.set_llm(self.llm)
        
        # Copy over all important state properties to preserve agent state
        rag_agent.context = self.context
        rag_agent.enhanced_prompt = self.enhanced_prompt
        
        # Copy over any additional properties that may have been set
        if hasattr(self, 'rag_config'):
            rag_agent.config = self.rag_config
        
        if hasattr(self, 'prompt_enhancer_llm'):
            rag_agent.set_prompt_enhancer_llm(self.prompt_enhancer_llm)
        
        # Get output with RAG
        return rag_agent.get_output_with_rag(user_query)


if __name__ == "__main__":
    role = "Requirements Agent"
    context = (
        "Requirements Document:\n"
        "Give me a 3D game for the following requirements:\n"
        "The game should be a 3D simulation of a car racing game.\n"
        "The game should have realistic physics and graphics.\n"
        "The game should support multiplayer mode.\n"
        "The game should have a leaderboard system.\n"
        "The game should have a tutorial mode for new players."
    )
    basic_prompt = (
        "You are an expert Requirements Agent. You have been provided with a detailed requirements document "
        "(extracted from a PDF) that describes a complex simulation system. Analyze the document and extract "
        "a clear, concise, and prioritized list of actionable requirements in bullet points. Format the output as plain text "
        "that can be embedded into a README file."
    )

    agent = BaseAgent(role, basic_prompt, context)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1,
        max_tokens=100000
    )

    agent.set_llm(llm)
    agent.set_prompt_enhancer_llm(llm)

    enhanced_prompt = agent.enhance_prompt()

    print("\033[93m" + enhanced_prompt + "\033[0m")

    output = agent.get_output()
    print("Final Output:\n", output)
