import PyPDF2
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from BaseAgent import BaseAgent


class ImplementationAgent(BaseAgent):
    role = "Implementation Agent"
    basic_prompt_template = """
    You are an expert ImplementationAgent.
    Based on the approved requirements provided below, develop a detailed implementation plan.
    Your plan should include a high-level design, key modules, and specific coding instructions.
    Note that the final product must be a single self-contained HTML file (with inline CSS and JavaScript).
    Now, give me a work based structure on how to implement the requirements provided.
    """

    approved_requirements = None

    def _extract_text_content(self, response):
        """
        Extract text content from various response types (string, dict, AIMessage, etc.)
        """
        # If it's a string already, return it
        if isinstance(response, str):
            return response
        
        # If it's a dict with 'text' key
        if isinstance(response, dict) and 'text' in response:
            return response['text']
        
        # If it's a LangChain message object
        if hasattr(response, 'content'):
            return response.content
        
        # If it has __str__ method, use it as a fallback
        return str(response)

    def __init__(self, approved_requirements):
        # Extract text content from the approved_requirements object
        self.approved_requirements = self._extract_text_content(approved_requirements).strip() if approved_requirements else ""
        # Format the prompt with the approved requirements.
        super(ImplementationAgent, self).__init__(self.role, basic_prompt=self.basic_prompt_template, context=None)

    def get_output(self):
        if not self.llm:
            raise ValueError("LLM is not set.")

        final_prompt_template = (
            "You are an expert in {role}.\n\n"
            "Prompt: {prompt}\n\n"
            "Requirements: {context}\n\n"
        )

        prompt = PromptTemplate(
            input_variables=["role", "prompt", "context"],
            template=final_prompt_template
        )

        # Fix: Create the sequence first, then invoke it
        chain = prompt | self.llm
        output = chain.invoke({
            "role": self.role,
            "context": self.approved_requirements,
            "prompt": self.enhanced_prompt if self.enhanced_prompt else self.basic_prompt
        })
        
        # Use the _extract_text_content method from BaseAgent
        return self._extract_text_content(output)


if __name__ == "__main__":
    approved_requirements = """
*   Simulate the lifecycle of processes, including creation and state transitions (e.g., running, waiting).
*   Model the context switching mechanism between simulated processes.
*   Simulate the association and manipulation of per-process data structures (e.g., Process Control Block) during lifecycle events and context switches.
*   Simulate the restoration of process context (data) when a process resumes execution after a context switch.
*   Display a collection of simulated processes visually.
*   Visualize the current state (e.g., running, waiting) for each simulated process.
*   Display the Process Control Block (PCB) details for each simulated process.
*   Display other relevant data structures associated with each simulated process.
*   Provide user controls to manually trigger the creation of a new process within the simulation.
*   Provide user controls to manually initiate a context switch for a selected process (specifically from a running to a waiting state).
*   Allow the user to manually step through and drive the simulation of the process lifecycle and context switching events.
*   Log the sequence of user actions performed via the controls and the resulting simulation states.
*   Implement validation logic to check if user-driven actions correctly manipulate the per-process data structures during context switching and execution steps.
    """

    impl_agent = ImplementationAgent(approved_requirements)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1,
        max_tokens=100000
    )
    impl_agent.set_llm(llm)
    impl_agent.set_prompt_enhancer_llm(llm)

    print(impl_agent.enhance_prompt())
    print("*" * 50)
    print(impl_agent.get_output())
