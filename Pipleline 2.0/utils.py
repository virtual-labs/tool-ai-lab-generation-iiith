"""
Utility functions for AI Pipeline Studio
"""
import streamlit as st
import os
import http.server
import socketserver
import threading
import socket
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI

# Agent imports
from Agents.CodingAgent import CodingAgent
from Agents.HumanReviewAgentForRequirement import HumanReviewAgentForRequirement
from Agents.ImplementationAgent import ImplementationAgent
from Agents.RequirementsAgent import RequirementsAgent
from Agents.DocumentationAgent import DocumentationAgent
from Agents.WebsiteDesignAgent import WebsiteDesignAgent


def init_llm():
    """Initialize the language model"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1,
        max_tokens=100000,
        google_api_key=os.getenv('GOOGLE_API_KEY')
    )


def init_session_state():
    """Initialize all session state variables"""
    session_vars = {
        "dark_mode": False,
        "requirements_output": "",
        "reviewed_requirements": "",
        "implementation_output": "",
        "code_loop": 0,
        "coding_agent_output": "",
        "documentation_output": "",
        "website_output": "",
        "server_started": False,
        "uploaded_file": None,
        "chat_history": [],
        "current_step": "requirements",
        "selected_model": "gemini-2.0-flash-exp",
        "rag_enabled": False,
        "rag_documents": [],
        "rag_n_results": 5
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value


def get_progress():
    """Calculate overall progress based on completed steps"""
    steps = {
        "requirements": st.session_state.requirements_output != "",
        "review": st.session_state.reviewed_requirements != "",
        "implementation": st.session_state.implementation_output != "",
        "code": st.session_state.coding_agent_output != "",
        "documentation": st.session_state.documentation_output != "",
        "website": st.session_state.website_output != ""
    }
    completed = sum(steps.values())
    return (completed / len(steps)) * 100


def initialize_rag():
    """Initialize RAG components"""
    try:
        # First ensure the RAG environment is properly set up
        from rag import setup_rag_environment
        setup_rag_environment()
        
        # Then initialize the document store
        if "document_store" not in st.session_state:
            from rag.document_store import DocumentStore
            st.session_state.document_store = DocumentStore()
        
        return True
    except Exception as e:
        st.error(f"Failed to initialize RAG: {str(e)}")
        return False


def generate_requirements():
    """Generate initial requirements from an uploaded PDF"""
    if st.session_state.uploaded_file is None:
        st.error("Please upload a PDF file first!")
        return ""
    
    req_agent = RequirementsAgent(str(st.session_state.uploaded_file))
    req_agent.set_llm(st.session_state.llm)
    req_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        req_agent.enable_rag(st.session_state.document_store)
    
    req_agent.enhance_prompt()
    return req_agent.get_output()


def review_requirements(user_review, base_text):
    """Process human review of requirements"""
    if user_review.strip() == "":
        return base_text
    
    review_agent = HumanReviewAgentForRequirement(user_review, base_text)
    review_agent.set_llm(st.session_state.llm)
    review_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        review_agent.enable_rag(st.session_state.document_store)
    
    review_agent.enhance_prompt()
    return review_agent.get_output()


def generate_implementation(requirements_text):
    """Generate implementation output from reviewed requirements"""
    impl_agent = ImplementationAgent(requirements_text)
    impl_agent.set_llm(st.session_state.llm)
    impl_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        impl_agent.enable_rag(st.session_state.document_store)
    
    return impl_agent.get_output()


def generate_code(impl_text, code_review):
    """Generate code via the CodingAgent"""
    coding_agent = CodingAgent(impl_text, code_review)
    coding_agent.set_llm(st.session_state.llm)
    coding_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        coding_agent.enable_rag(st.session_state.document_store)
    
    coding_agent.enhance_prompt()
    return coding_agent.get_output()


def generate_documentation(code_text):
    """Generate documentation using the DocumentationAgent"""
    context = (
        f"Requirements:\n{st.session_state.reviewed_requirements}\n\n"
        f"Implementation Plan:\n{st.session_state.implementation_output}\n\n"
        f"Code:\n{code_text}"
    )
    doc_agent = DocumentationAgent(context)
    doc_agent.set_llm(st.session_state.llm)
    doc_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        doc_agent.enable_rag(st.session_state.document_store)
    
    doc_agent.enhance_prompt()
    return doc_agent.get_output()


def generate_website(simulation_code, website_feedback=None, previous_website_code=None):
    """Generate a complete Virtual Lab Website"""
    website_agent = WebsiteDesignAgent(simulation_code, website_feedback, previous_website_code)
    website_agent.set_llm(st.session_state.llm)
    website_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        website_agent.enable_rag(st.session_state.document_store)
    
    website_agent.enhance_prompt()
    return website_agent.get_output()


def start_http_server(directory, port=8000):
    """Start a HTTP server in a separate thread"""
    if st.session_state.server_started:
        return True
        
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.close()
        
        handler = Handler
        httpd = socketserver.TCPServer(("", port), handler)
        
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        st.session_state.server_started = True
        return True
        
    except OSError as e:
        if e.errno in [98, 10048]:  # Port already in use
            st.session_state.server_started = True
            return True
        st.error(f"Server error: {str(e)}")
        return False


def save_and_serve_code(code_content):
    """Save code to file and start server if needed"""
    try:
        current_dir = Path(__file__).parent
        code_file_path = current_dir / "code.html"
        
        with open(code_file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        
        if start_http_server(current_dir):
            return f"http://localhost:8000/code.html"
        return None
            
    except Exception as e:
        st.error(f"Error saving code file: {str(e)}")
        return None
