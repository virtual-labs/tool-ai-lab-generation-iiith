from sys import implementation

from Agents.CodingAgent import CodingAgent
from Agents.HumanReviewAgentForRequirement import HumanReviewAgentForRequirement
from Agents.ImplementationAgent import ImplementationAgent
from Agents.RequirementsAgent import RequirementsAgent
from Agents.VerfierAgent import VerifierAgent
from Agents.DocumentationAgent import DocumentationAgent
from BaseAgent import BaseAgent
from langchain_google_genai import ChatGoogleGenerativeAI

class Pipeline:
    llm = None
    max_loop = 3
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_tokens=100000
        )
        # Initialize document store for RAG if needed
        self.rag_enabled = False
        try:
            from rag.document_store import DocumentStore
            self.document_store = DocumentStore()
            print("RAG document store initialized")
        except Exception as e:
            print(f"Could not initialize RAG: {str(e)}")
            self.document_store = None

    def enable_rag(self, enabled=True):
        """Enable or disable RAG for all agents"""
        self.rag_enabled = enabled and self.document_store is not None
        return self.rag_enabled
    
    def _apply_rag_to_agent(self, agent):
        """Helper method to apply RAG to an agent if enabled"""
        if self.rag_enabled and self.document_store and hasattr(agent, 'enable_rag'):
            agent.enable_rag(self.document_store)
    
    def run(self):
        # Requirements Agent
        reqAgent = RequirementsAgent("1.pdf")
        reqAgent.set_llm(self.llm)
        reqAgent.set_prompt_enhancer_llm(self.llm)
        self._apply_rag_to_agent(reqAgent)
        reqAgent.enhance_prompt()
        req_Agent_output = reqAgent.get_output()
        print("[\033[91mRequirements OUTPUT\033[0m")
        print(req_Agent_output)
        
        # Human Review
        human_review_output = ""
        human_review = None
        while True:
            review_1 = input(">>> Enter your review for the requirements: Press Enter to skip: ")
            if review_1 == "":
                if human_review_output == "":
                    human_review_output = req_Agent_output
                break

            human_review = HumanReviewAgentForRequirement(req_Agent_output, review_1)
            human_review.set_llm(self.llm)
            human_review.set_prompt_enhancer_llm(self.llm)
            self._apply_rag_to_agent(human_review)
            human_review.enhance_prompt()
            human_review_output = human_review.get_output()
            print(human_review_output)
            
        print("\033[91mHuman Review Output\033[0m")
        print(human_review_output)
        
        # Implementation Agent
        implementation_agent = ImplementationAgent(human_review_output)
        implementation_agent.set_llm(self.llm)
        implementation_agent.set_prompt_enhancer_llm(self.llm)
        self._apply_rag_to_agent(implementation_agent)
        implementation_agent.enhance_prompt()
        impl_agent_output = implementation_agent.get_output()
        print("\033[91mImplementation OUTPUT\033[0m")
        print(impl_agent_output)

        # Coding Agent loop
        loop = 0
        code_review = ""
        coding_agent_output = ""
        while loop < self.max_loop:
            coding_agent = CodingAgent(impl_agent_output, code_review)
            coding_agent.set_llm(self.llm)
            coding_agent.set_prompt_enhancer_llm(self.llm)
            self._apply_rag_to_agent(coding_agent)
            coding_agent.enhance_prompt()
            coding_agent_output = coding_agent.get_output()
            with open("code.html", "w") as f:
                f.write(coding_agent_output)

            print()
            print("-"*100)
            print(coding_agent_output)
            
            code_review = input(">>> Enter your review for the code (type 'done' to proceed): ")
            if code_review.lower() == 'done':
                break
            loop += 1

        # Documentation Agent
        documentation_agent = DocumentationAgent(coding_agent_output)
        documentation_agent.set_llm(self.llm)
        documentation_agent.set_prompt_enhancer_llm(self.llm)
        self._apply_rag_to_agent(documentation_agent)
        documentation_agent.enhance_prompt()
        documentation_agent_output = documentation_agent.get_output()
        with open("documentation.md", "w") as f:
            f.write(documentation_agent_output)


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run()
