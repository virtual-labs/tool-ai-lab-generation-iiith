from typing import List, Dict, Any
import sys
import os

# Add parent directory to Python path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from BaseAgent import BaseAgent
from .document_store import DocumentStore
from langchain_core.prompts import PromptTemplate
from .config import RAGConfig

class RAGAgent(BaseAgent):
    def __init__(self, role: str, basic_prompt: str, document_store: DocumentStore):
        super().__init__(role, basic_prompt)
        self.document_store = document_store
        self.retrieved_docs = []
        self.config = RAGConfig()  # Instantiate as object instead of using class directly
    
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
    
    def reformulate_query(self, query: str) -> str:
        """
        Reformulate the query to improve retrieval quality
        """
        if not self.config.QUERY_REFORMULATION_ENABLED or not self.llm:
            return query
            
        reformulation_template = (
            "You are an expert at formulating search queries. "
            "Given an original query, create an improved version that will help retrieve the most relevant information. "
            "Keep the reformulated query focused on the same topic but make it more specific and comprehensive.\n\n"
            "Original query: {query}\n\n"
            "Improved search query:"
        )
        
        prompt = PromptTemplate(
            input_variables=["query"],
            template=reformulation_template
        )
        
        # Use RunnableSequence: prompt | llm
        chain = prompt | self.llm
        result = chain.invoke({"query": query})
        
        # Extract the text content from the result (handles AIMessage and other object types)
        reformulated_query = self._extract_text_content(result)
        
        # Fall back to original query if reformulation failed or returned empty
        if not reformulated_query or len(reformulated_query.strip() if hasattr(reformulated_query, 'strip') else reformulated_query) < 3:
            return query
            
        return reformulated_query.strip() if hasattr(reformulated_query, 'strip') else reformulated_query
    
    def search_knowledge_base(self, query: str, n_results: int = None, filter_dict: Dict = None) -> List[Dict]:
        """Search the knowledge base for relevant information"""
        if n_results is None:
            n_results = self.config.DEFAULT_SEARCH_RESULTS
            
        # Reformulate query if enabled
        if self.config.QUERY_REFORMULATION_ENABLED:
            query = self.reformulate_query(query)
            
        self.retrieved_docs = self.document_store.search_documents(
            query=query,
            n_results=n_results,
            filter_dict=filter_dict
        )
        
        # Apply re-ranking if enabled
        if self.config.RERANKING_ENABLED and self.retrieved_docs:
            self.retrieved_docs = self._rerank_documents(query, self.retrieved_docs)
            
        return self.retrieved_docs
    
    def _rerank_documents(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Re-rank documents for better relevance (placeholder for future implementation)"""
        # This would be implemented with a cross-encoder or other re-ranking method
        # For now, we'll return the documents as-is
        return documents
    
    def build_context_from_search(self, query: str, n_results: int = None) -> str:
        """Build context string from search results with improved formatting"""
        if n_results is None:
            n_results = self.config.DEFAULT_SEARCH_RESULTS
            
        search_results = self.search_knowledge_base(query, n_results)
        
        if not search_results:
            return "No relevant documents found in the knowledge base."
        
        context_parts = ["RETRIEVED INFORMATION:"]
        
        # Add a summary of retrieval stats
        context_parts.append(f"Found {len(search_results)} relevant documents. Showing most relevant information below.")
        
        # Format each document in a cleaner way
        for i, result in enumerate(search_results, 1):
            # Only include score if configured
            score_text = f" [Relevance: {result['score']:.2f}]" if self.config.SHOW_RELEVANCE_SCORE else ""
            
            context_parts.append(f"\n### DOCUMENT {i}{score_text}")
            
            # Only include metadata if configured
            if self.config.INCLUDE_METADATA:
                source = result['metadata'].get('source', 'Unknown source')
                context_parts.append(f"Source: {source}")
                
            # Add the content with clear formatting
            context_parts.append(f"\n{result['content']}\n")
        
        # Join with newlines for better readability
        return "\n".join(context_parts)
    
    def get_output_with_rag(self, user_query: str = None, search_filter: Dict = None):
        """Get output enhanced with RAG"""
        if not self.llm:
            raise ValueError("LLM is not set.")
        
        # If no specific query provided, use the basic prompt as search query
        search_query = user_query or self.basic_prompt
        
        # Retrieve relevant documents
        rag_context = self.build_context_from_search(search_query, n_results=self.config.DEFAULT_SEARCH_RESULTS)
        
        # Combine original context with RAG context
        enhanced_context = f"{self.context}\n\n{rag_context}" if self.context else rag_context
        
        # Use enhanced prompt if available
        base_prompt = self.enhanced_prompt if self.enhanced_prompt else self.basic_prompt
        
        final_prompt_template = (
            "You are an expert in {role}.\n\n"
            "CONTEXT AND KNOWLEDGE BASE:\n"
            "{enhanced_context}\n\n"
            "TASK:\n"
            "{base_prompt}\n\n"
            "Use the provided context and knowledge base information to give a comprehensive and accurate response. "
            "If the knowledge base contains relevant information, incorporate it into your response. "
            "If the knowledge base doesn't contain relevant information, rely on your general knowledge but mention this limitation."
        )
        
        prompt = PromptTemplate(
            input_variables=["role", "enhanced_context", "base_prompt"],
            template=final_prompt_template
        )
        
        # Use RunnableSequence: prompt | llm
        chain = prompt | self.llm
        output = chain.invoke({
            "role": self.role,
            "enhanced_context": enhanced_context,
            "base_prompt": base_prompt
        })
        
        # Extract text content from the output (handles AIMessage and other object types)
        return self._extract_text_content(output)