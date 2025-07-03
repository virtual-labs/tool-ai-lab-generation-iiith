import streamlit as st
import os
import webbrowser
from pathlib import Path
import http.server
import socketserver
import threading
import socket

# Local imports
from Agents.CodingAgent import CodingAgent
from Agents.HumanReviewAgentForRequirement import HumanReviewAgentForRequirement
from Agents.ImplementationAgent import ImplementationAgent
from Agents.RequirementsAgent import RequirementsAgent
from Agents.DocumentationAgent import DocumentationAgent
from Agents.WebsiteDesignAgent import WebsiteDesignAgent
from Agents.VerfierAgent import VerifierAgent  # Add missing VerifierAgent import
from langchain_google_genai import ChatGoogleGenerativeAI

# Import custom modules
from styles import get_all_styles
from ui_components import (
    render_header, render_theme_toggle, render_model_selection,
    render_progress_tracker, render_chat_interface,
    render_footer, render_status_badge, render_step_tracker, render_file_upload_for_requirements,
    # RAG UI components moved from rag/rag_ui_components.py
    render_rag_file_uploader, render_rag_document_manager, 
    render_rag_settings, process_rag_files, initialize_rag
)

# Disable ChromaDB telemetry to fix the capture() error
os.environ["CHROMADB_TELEMETRY"] = "0"

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="🚀 AI Pipeline Studio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------
# Initialize Application
# ---------------------------------------------------

# Initialize the language model instance
def init_llm(model=None, temperature=0.1, max_tokens=100000):
    return ChatGoogleGenerativeAI(
        model=model or "gemini-2.0-flash-exp",
        temperature=temperature,
        max_tokens=max_tokens,
        google_api_key=os.getenv('GOOGLE_API_KEY')
    )

# Initialize session state
def init_session_state():
    if "requirements_output" not in st.session_state:
        st.session_state.requirements_output = ""
    if "reviewed_requirements" not in st.session_state:
        st.session_state.reviewed_requirements = ""
    if "implementation_output" not in st.session_state:
        st.session_state.implementation_output = ""
    if "code_loop" not in st.session_state:
        st.session_state.code_loop = 0
    if "coding_agent_output" not in st.session_state:
        st.session_state.coding_agent_output = ""
    if "documentation_output" not in st.session_state:
        st.session_state.documentation_output = ""
    if "website_output" not in st.session_state:
        st.session_state.website_output = ""
    if 'server_started' not in st.session_state:
        st.session_state.server_started = False
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True
    if "current_step" not in st.session_state:
        st.session_state.current_step = "requirements"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gemini-2.0-flash-exp"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.1
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 100000
    if "preview_url" not in st.session_state:
        st.session_state.preview_url = None
    if "rag_enabled" not in st.session_state:
        st.session_state.rag_enabled = False
    if "rag_documents" not in st.session_state:
        st.session_state.rag_documents = []
    if "rag_n_results" not in st.session_state:
        st.session_state.rag_n_results = 5

# Agent Functions
def generate_requirements():
    """Generate initial requirements from an uploaded PDF using the RequirementsAgent."""
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
    """Let the human review the generated requirements.
       If no review is provided, the original output is kept.
    """
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
    """Generate implementation output from reviewed requirements."""
    impl_agent = ImplementationAgent(requirements_text)
    impl_agent.set_llm(st.session_state.llm)
    impl_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        impl_agent.enable_rag(st.session_state.document_store)
    
    return impl_agent.get_output()

def generate_code(impl_text, code_review):
    """Generate code via the CodingAgent given implementation output and code review feedback."""
    coding_agent = CodingAgent(impl_text, code_review)
    coding_agent.set_llm(st.session_state.llm)
    coding_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        coding_agent.enable_rag(st.session_state.document_store)
    
    coding_agent.enhance_prompt()
    return coding_agent.get_output()

def generate_documentation(code_text):
    """Generate documentation using the DocumentationAgent."""
    # Option 1: Enhanced with context (current ui.py implementation)
    context = (
        f"Requirements:\n{st.session_state.reviewed_requirements}\n\n"
        f"Implementation Plan:\n{st.session_state.implementation_output}\n\n"
        f"Code:\n{code_text}"
    )
    doc_agent = DocumentationAgent(context)
    
    # Option 2: Original implementation from original.py
    # Uncomment this and comment option 1 above if you want to match original.py exactly
    # doc_agent = DocumentationAgent(code_text)
    
    doc_agent.set_llm(st.session_state.llm)
    doc_agent.set_prompt_enhancer_llm(st.session_state.llm)
    doc_agent.enhance_prompt()
    return doc_agent.get_output()

# Add a verification function to match original.py functionality
def verify_system(code_output, requirements):
    """Verify the generated code using VerifierAgent."""
    verifier = VerifierAgent()
    verifier.integrated_system = code_output
    verifier.req_doc = requirements
    verifier.set_llm(st.session_state.llm)
    verifier.set_prompt_enhancer_llm(st.session_state.llm)
    return verifier.get_output()

def generate_website(simulation_code, website_feedback=None, previous_website_code=None):
    """Generate a complete Virtual Lab Website using the WebsiteAgent."""
    website_agent = WebsiteDesignAgent(simulation_code, website_feedback, previous_website_code)
    website_agent.set_llm(st.session_state.llm)
    website_agent.set_prompt_enhancer_llm(st.session_state.llm)
    
    # Enable RAG if configured
    if st.session_state.get("rag_enabled", False) and "document_store" in st.session_state:
        website_agent.enable_rag(st.session_state.document_store)
    
    website_agent.enhance_prompt()
    return website_agent.get_output()

def get_progress():
    """Calculate the current progress percentage based on completed steps"""
    steps_count = 6  # Total number of pipeline steps
    completed = 0
    
    if st.session_state.requirements_output:
        completed += 1
    if st.session_state.reviewed_requirements:
        completed += 1
    if st.session_state.implementation_output:
        completed += 1
    if st.session_state.coding_agent_output:
        completed += 1
    if st.session_state.documentation_output:
        completed += 1
    if st.session_state.website_output:
        completed += 1
        
    return (completed / steps_count) * 100

# Server handling functions
def start_http_server(directory, port=8000):
    """Start a HTTP server in a separate thread"""
    if st.session_state.server_started:
        return True
        
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
            
        def log_message(self, format, *args):
            # Enhanced logging to help debug issues
            if args and len(args) > 0:
                request_path = args[0].split()[1] if len(args[0].split()) > 1 else "unknown"
                print(f"Server request: {request_path} - {args}")
            super().log_message(format, *args)
    
    try:
        # Test if port is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.close()
        
        # Create server
        handler = Handler
        httpd = socketserver.TCPServer(("", port), handler)
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True  # Thread will close when main program exits
        server_thread.start()
        
        st.success(f"✅ Preview server started at http://localhost:{port}")
        st.session_state.server_started = True
        return True
        
    except OSError as e:
        if e.errno in [48, 98, 10048]:  # Address already in use (Mac: 48, Linux: 98, Windows: 10048)
            st.session_state.server_started = True
            return True
        st.error(f"Server error: {str(e)}")
        return False

def clean_code_output(code_content):
    """
    Clean HTML code by removing markdown code fences and other artifacts
    """
    if not code_content:
        return ""
    
    # Remove common markdown code block markers
    code_content = code_content.strip()
    
    # Remove ```html or ``` markers at beginning and end
    code_patterns = [
        r'^```html\s*', r'^```\s*', r'\s*```$',  # Basic markdown code fences
        r'^<pre><code[^>]*>', r'</code></pre>$',  # HTML code block markers
        r'^<code[^>]*>', r'</code>$'              # HTML inline code markers
    ]
    
    import re
    for pattern in code_patterns:
        code_content = re.sub(pattern, '', code_content, flags=re.MULTILINE)
    
    # Ensure proper HTML structure
    if not code_content.lower().strip().startswith('<!doctype') and not code_content.lower().strip().startswith('<html'):
        # If the content is just HTML fragment without proper structure, wrap it
        if '<body' not in code_content.lower():
            code_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Virtual Lab</title>
</head>
<body>
{code_content}
</body>
</html>
"""
    
    return code_content

def save_and_serve_code(code_content):
    """Save code to file and start server if needed"""
    try:
        # Clean the code content
        cleaned_code = clean_code_output(code_content)
        
        # Get the directory of the current file
        current_dir = Path(__file__).parent
        code_file_path = current_dir / "code.html"
        
        # Save the code to file
        with open(code_file_path, "w", encoding="utf-8") as f:
            f.write(cleaned_code)
        
        # Start the server if not already running
        if start_http_server(current_dir):
            return f"http://localhost:8000/code.html"
        return None
            
    except Exception as e:
        st.error(f"Error saving code file: {str(e)}")
        return None

# ---------------------------------------------------
# Initialize Application
# ---------------------------------------------------

# Initialize session state
init_session_state()

# Initialize LLM if needed
if "llm" not in st.session_state:
    st.session_state.llm = init_llm()

# Apply theme styles
st.markdown(get_all_styles(st.session_state.dark_mode), unsafe_allow_html=True)

# ---------------------------------------------------
# Sidebar Toggle State Initialization
# ---------------------------------------------------
if "sidebar_mode" not in st.session_state:
    st.session_state.sidebar_mode = "ai_config"  # or "chat" or "rag_config"

# ---------------------------------------------------
# Sidebar Content
# ---------------------------------------------------
with st.sidebar:
    # Display the appropriate sidebar content based on mode
    if st.session_state.sidebar_mode == "ai_config":
        # Model Selection (returns model, temp, max_tokens)
        selected_model, selected_temp, selected_max_tokens = render_model_selection()
        # Handle model or settings change
        if (
            selected_model != st.session_state.selected_model or
            selected_temp != st.session_state.temperature or
            selected_max_tokens != st.session_state.max_tokens
        ):
            st.session_state.selected_model = selected_model
            st.session_state.temperature = selected_temp
            st.session_state.max_tokens = selected_max_tokens
            st.session_state.llm = init_llm(
                model=selected_model,
                temperature=selected_temp,
                max_tokens=selected_max_tokens
            )
            st.success(f"✅ Model/settings updated successfully!")
    elif st.session_state.sidebar_mode == "chat":
        chat_input, send_clicked, clear_clicked = render_chat_interface()
        # Handle chat interactions
        if send_clicked and chat_input.strip():
            st.session_state.chat_history.append({
                "role": "user",
                "content": chat_input
            })
            try:
                chat_prompt = f"""You are a helpful AI assistant for an educational content pipeline generator. 
You help users create virtual labs with requirements, implementation, code, documentation, and websites.

Current pipeline status:
- Requirements: {'✅ Complete' if st.session_state.requirements_output else '❌ Pending'}
- Review: {'✅ Complete' if st.session_state.reviewed_requirements else '❌ Pending'}
- Implementation: {'✅ Complete' if st.session_state.implementation_output else '❌ Pending'}
- Code: {'✅ Complete' if st.session_state.coding_agent_output else '❌ Pending'}
- Documentation: {'✅ Complete' if st.session_state.documentation_output else '❌ Pending'}
- Website: {'✅ Complete' if st.session_state.website_output else '❌ Pending'}

User message: {chat_input}

Provide helpful, friendly guidance with emojis. Keep responses concise but informative."""
                ai_response = st.session_state.llm.invoke(chat_prompt).content
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"😅 I encountered an error: {str(e)}. Please try again!"
                })
            st.rerun()
        if clear_clicked:
            st.session_state.chat_history = []
            st.rerun()
    elif st.session_state.sidebar_mode == "rag_config":
        st.markdown("## 📚 RAG Configuration")
        st.markdown("Configure Retrieval Augmented Generation settings and upload knowledge base documents.")
        
        # Initialize RAG at the beginning of the section - with better error handling
        rag_initialized = False
        try:
            if initialize_rag():
                rag_initialized = True
        except Exception as e:
            st.error(f"Error initializing RAG: {str(e)}")
            st.info("Please install required packages: pip install langchain-community chromadb")
            
        # RAG settings
        render_rag_settings()
        
        # Upload files for RAG
        uploaded_files = render_rag_file_uploader()
        if uploaded_files:
            if st.button("📥 Process Uploaded Files", use_container_width=True):
                with st.spinner("Processing files..."):
                    # Check if document_store is initialized
                    if rag_initialized and "document_store" in st.session_state and st.session_state.document_store is not None:
                        try:
                            successful, docs_metadata = process_rag_files(uploaded_files, st.session_state.document_store)
                            st.success(f"✅ Successfully added {successful} documents to the knowledge base!")
                        except Exception as e:
                            st.error(f"Error processing files: {str(e)}")
                    else:
                        st.error("❌ Document store is not initialized properly")
                        st.info("Try reloading the page and initializing RAG again.")
        
        # Document management
        render_rag_document_manager()
        
        # Show document count
        if rag_initialized and "document_store" in st.session_state and st.session_state.document_store is not None:
            try:
                doc_count = st.session_state.document_store.get_document_count()
                st.info(f"📊 Knowledge base contains {doc_count} document chunks")
            except Exception as e:
                st.warning(f"Unable to get document count: {str(e)}")

# ---------------------------------------------------
# Main UI Layout
# ---------------------------------------------------

# Header and theme toggle
render_header()
render_theme_toggle()

# --- Sidebar toggle buttons BELOW theme toggle ---
sidebar_toggle_col1, sidebar_toggle_col2, sidebar_toggle_col3 = st.columns([1, 1, 1], gap="small")
with sidebar_toggle_col1:
    if st.button("🤖 AI Configuration", use_container_width=True, key="sidebar_ai_btn_header"):
        st.session_state.sidebar_mode = "ai_config"
with sidebar_toggle_col2:
    if st.button("💬 Support Chatbot", use_container_width=True, key="sidebar_chat_btn_header"):
        st.session_state.sidebar_mode = "chat"
with sidebar_toggle_col3:
    if st.button("📚 Knowledge Base", use_container_width=True, key="sidebar_rag_btn_header"):
        st.session_state.sidebar_mode = "rag_config"
        # Initialize RAG components if not already done
        try:
            if not initialize_rag():
                st.error("Failed to initialize RAG. Some features may not work.")
        except Exception as e:
            st.error(f"Error initializing RAG: {str(e)}")
            st.info("Please install required packages: pip install langchain-community chromadb")

# --- Reset Pipeline Button BELOW the title and toggle buttons ---
reset_col = st.container()
with reset_col:
    if st.button("🔄 Reset Pipeline", use_container_width=True, key="reset_pipeline_btn"):
        for key in [
            "requirements_output", "reviewed_requirements", "implementation_output",
            "code_loop", "coding_agent_output", "documentation_output", "website_output",
            "server_started", "uploaded_file", "chat_history", "current_step"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_step = "requirements"
        st.session_state.chat_history = []
        st.rerun()

# Step Tracker (horizontal boxes below title)
completed_steps = {
    "requirements": bool(st.session_state.requirements_output),
    "review": bool(st.session_state.reviewed_requirements),
    "implementation": bool(st.session_state.implementation_output),
    "code": bool(st.session_state.coding_agent_output),
    "documentation": bool(st.session_state.documentation_output),
    "website": bool(st.session_state.website_output),
}
render_step_tracker(st.session_state.current_step, completed_steps)

# Progress Tracker (horizontal bar, keep below step tracker if you want)
progress = get_progress()
render_progress_tracker(progress)

# Create main layout columns (center only, maximize width)
middle_col = st.container()

# ---------------------------------------------------
# Middle Column - Only Show Selected Step
# ---------------------------------------------------

with middle_col:
    step = st.session_state.current_step

    if step == "requirements":
        st.markdown('### 📝 Step 1: Requirements Generation')
        # File upload for requirements step only
        render_file_upload_for_requirements()
        if st.button("🚀 Generate Requirements", 
                    use_container_width=True, 
                    disabled=st.session_state.uploaded_file is None, key="gen_req_btn"):
            if st.session_state.uploaded_file is None:
                st.error("❌ Please upload a PDF file first!")
            else:
                with st.spinner("🔍 Analyzing your PDF and generating requirements..."):
                    st.session_state.requirements_output = generate_requirements()
                    st.session_state.chat_history.append({
                        "role": "system",
                        "content": "🎉 Requirements generated successfully from uploaded PDF."
                    })
                st.success("✅ Requirements generated successfully!")
                # st.session_state.current_step = "review"  # REMOVE AUTO ADVANCE
                # st.rerun()  # REMOVE AUTO ADVANCE
        
        if st.session_state.requirements_output:
            with st.expander("📄 View Generated Requirements", expanded=True):
                st.markdown(f'{st.session_state.requirements_output}', unsafe_allow_html=True)

    elif step == "review":
        st.markdown('### 👁️ Step 2: Requirements Review')
        review_text = st.text_area(
            "💬 Share your feedback on the requirements:",
            height=100,
            disabled=st.session_state.requirements_output == "",
            placeholder="Add your suggestions, corrections, or additional requirements here...",
            key="review_textarea"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Submit Review", 
                        use_container_width=True,
                        disabled=st.session_state.requirements_output == "", key="submit_review_btn"):
                with st.spinner("🔄 Processing your feedback..."):
                    st.session_state.reviewed_requirements = review_requirements(
                        review_text, st.session_state.requirements_output
                    )
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": f"📝 Review feedback: {review_text}"
                    })
                st.success("✅ Requirements reviewed successfully!")
                # st.session_state.current_step = "implementation"  # REMOVE AUTO ADVANCE
                # st.rerun()  # REMOVE AUTO ADVANCE
        
        with col2:
            if st.button("⏭️ Skip Review", 
                        use_container_width=True,
                        disabled=st.session_state.requirements_output == "", key="skip_review_btn"):
                st.session_state.reviewed_requirements = st.session_state.requirements_output
                st.success("⏭️ Using original requirements!")
                # st.session_state.current_step = "implementation"  # REMOVE AUTO ADVANCE
                # st.rerun()  # REMOVE AUTO ADVANCE
        
        if st.session_state.reviewed_requirements:
            with st.expander("📄 Final Requirements", expanded=False):
                st.markdown(f'{st.session_state.reviewed_requirements}', unsafe_allow_html=True)

    elif step == "implementation":
        st.markdown('### 🔧 Step 3: Implementation Planning')
        if st.button("🏗️ Generate Implementation Plan", 
                    use_container_width=True,
                    disabled=st.session_state.reviewed_requirements == "", key="gen_impl_btn"):
            with st.spinner("🎯 Creating detailed implementation plan..."):
                st.session_state.implementation_output = generate_implementation(
                    st.session_state.reviewed_requirements
                )
                st.session_state.chat_history.append({
                    "role": "system",
                    "content": "🎯 Implementation plan generated successfully."
                })
            st.success("✅ Implementation plan ready!")
            # st.session_state.current_step = "code"  # REMOVE AUTO ADVANCE
            # st.rerun()  # REMOVE AUTO ADVANCE
        
        if st.session_state.implementation_output:
            with st.expander("🔧 Implementation Plan", expanded=True):
                st.markdown(f'{st.session_state.implementation_output}', unsafe_allow_html=True)

    elif step == "code":
        st.markdown('### 💻 Step 4: Code Generation')
        if st.session_state.implementation_output:
            MAX_CODE_LOOP = 3
            st.markdown(render_status_badge("info", f"🔄 Iteration {st.session_state.code_loop + 1} of {MAX_CODE_LOOP}"), unsafe_allow_html=True)
            code_review_input = st.text_area(
                "🔍 Code review feedback (optional):",
                height=100,
                placeholder="Suggest improvements, bug fixes, or feature additions...",
                key="code_review_textarea"
            )
            if st.button("⚡ Generate/Refine Code", 
                        use_container_width=True,
                        disabled=st.session_state.code_loop >= MAX_CODE_LOOP, key="gen_code_btn"):
                with st.spinner("⚡ Generating high-quality code..."):
                    input_text = (
                        st.session_state.implementation_output
                        if st.session_state.code_loop == 0
                        else st.session_state.coding_agent_output
                    )
                    st.session_state.coding_agent_output = generate_code(input_text, code_review_input)
                    st.session_state.code_loop += 1
                    
                    # Save code and get URL
                    localhost_url = save_and_serve_code(st.session_state.coding_agent_output)
                    if localhost_url:
                        st.session_state.preview_url = localhost_url
                        st.session_state.chat_history.append({
                            "role": "system",
                            "content": f"💻 Code generated (iteration {st.session_state.code_loop}). 🌐 Preview: {localhost_url}"
                        })
                st.success("✅ Code generated successfully!")
            
            if st.session_state.coding_agent_output:
                # Split layout: Code on the left, preview on the right
                code_col, preview_col = st.columns([1, 1])
                with code_col:
                    st.markdown("#### Generated Code")
                    st.code(st.session_state.coding_agent_output, language="html")
                with preview_col:
                    st.markdown("#### Live Preview")
                    if st.session_state.preview_url:
                        st.markdown(f"""
                        <iframe src="{st.session_state.preview_url}" style="width:100%;height:500px;border:none;"></iframe>
                        """, unsafe_allow_html=True)
                        if st.button("🌐 Open in New Tab", key="open_code_preview_btn"):
                            webbrowser.open_new_tab(st.session_state.preview_url)
            
            if st.session_state.code_loop >= MAX_CODE_LOOP:
                st.markdown(render_status_badge("warning", "⚠️ Maximum iterations reached"), unsafe_allow_html=True)
                
            if st.session_state.coding_agent_output:
                next_btn = st.button("Next: Documentation ➡️", use_container_width=True, key="next_to_doc_btn")
                if next_btn:
                    st.session_state.current_step = "documentation"
                    st.rerun()
                    
        else:
            st.markdown(render_status_badge("info", "ℹ️ Complete implementation step first"), unsafe_allow_html=True)

    elif step == "documentation":
        st.markdown('### 📚 Step 5: Documentation Generation')
        if st.button("📖 Generate Documentation", 
                    use_container_width=True,
                    disabled=st.session_state.coding_agent_output == "", key="gen_doc_btn"):
            with st.spinner("📖 Creating comprehensive documentation..."):
                st.session_state.documentation_output = generate_documentation(
                    st.session_state.coding_agent_output
                )
                st.session_state.chat_history.append({
                    "role": "system",
                    "content": "📚 Documentation generated successfully."
                })
            st.success("✅ Documentation ready!")
            
            # Display generated documentation
            st.markdown(st.session_state.documentation_output)
            
            next_btn = st.button("Next: Website ➡️", use_container_width=True, key="next_to_website_btn1")
            if next_btn:
                st.session_state.current_step = "website"
                st.rerun()
        
        if st.session_state.documentation_output:
            with st.expander("📚 Generated Documentation", expanded=True):
                st.markdown(f'{st.session_state.documentation_output}', unsafe_allow_html=True)
                
            next_btn = st.button("Next: Website ➡️", use_container_width=True, key="next_to_website_btn2")
            if next_btn:
                st.session_state.current_step = "website"
                st.rerun()

    elif step == "website":
        st.markdown('### 🌐 Step 6: Virtual Lab Website')
        
        # Add verification option
        verify_system_checkbox = st.checkbox("Verify system against requirements", value=False, key="verify_system_checkbox")
        
        website_feedback = st.text_area(
            "🎨 Website design preferences (optional):",
            height=100,
            disabled=st.session_state.coding_agent_output == "",
            placeholder="Describe your preferred colors, layout, features, or styling...",
            key="website_feedback_textarea"
        )
        if st.button("🎨 Generate Virtual Lab Website", 
                    use_container_width=True,
                    disabled=st.session_state.coding_agent_output == "", key="gen_website_btn"):
            with st.spinner("🎨 Creating beautiful virtual lab website..."):
                simulation_code = st.session_state.coding_agent_output
                previous_website_code = st.session_state.get("website_output", None) if website_feedback else None
                
                st.session_state.website_output = generate_website(
                    simulation_code, 
                    website_feedback=website_feedback,
                    previous_website_code=previous_website_code
                )
                
                # Save website and get URL
                localhost_url = save_and_serve_code(st.session_state.website_output)
                if localhost_url:
                    st.session_state.preview_url = localhost_url
                    st.session_state.chat_history.append({
                        "role": "system",
                        "content": f"🌐 Virtual Lab Website generated! 🚀 Available at: {localhost_url}"
                    })
            st.success("🎉 Virtual Lab Website is live!")
        
        if st.session_state.website_output:
            # Split layout: Code on the left, preview on the right
            code_col, preview_col = st.columns([1, 1])
            with code_col:
                st.markdown("#### Website Code")
                preview_length = 1000  # Show first 1000 chars
                if len(st.session_state.website_output) > preview_length:
                    preview = st.session_state.website_output[:preview_length] + "... (truncated)"
                else:
                    preview = st.session_state.website_output
                st.code(preview, language="html")
            with preview_col:
                st.markdown("#### Live Preview")
                if st.session_state.preview_url:
                    st.markdown(f"""
                    <iframe src="{st.session_state.preview_url}" style="width:100%;height:500px;border:none;"></iframe>
                    """, unsafe_allow_html=True)
                    if st.button("🌐 Open in New Tab", key="open_website_btn"):
                        webbrowser.open_new_tab(st.session_state.preview_url)
            
        # Add verification step if checkbox is checked
        if verify_system_checkbox and st.session_state.website_output and st.session_state.reviewed_requirements:
            if st.button("🔍 Verify System", use_container_width=True, key="verify_system_btn"):
                with st.spinner("Verifying system against requirements..."):
                    verification_result = verify_system(
                        st.session_state.website_output,
                        st.session_state.reviewed_requirements
                    )
                    st.session_state.chat_history.append({
                        "role": "system",
                        "content": f"🔍 System verification: {verification_result}"
                    })
                    st.markdown("### Verification Results")
                    st.markdown(verification_result)
        
        # Remove duplicate website code expander as we already have it in the split layout above

    # --- Navigation Buttons (always visible at the bottom of the main column) ---
    step_order = [
        "requirements",
        "review",
        "implementation",
        "code",
        "documentation",
        "website"
    ]
    current_idx = step_order.index(st.session_state.current_step)
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)  # Spacer above buttons
    nav_cols = st.columns([1, 1], gap="large")
    with nav_cols[0]:
        if current_idx > 0:
            if st.button("⬅️ Previous step", key="prev_step_btn", use_container_width=True):
                st.session_state.current_step = step_order[current_idx - 1]
                st.rerun()
        else:
            st.markdown("&nbsp;", unsafe_allow_html=True)  # keep button row height
    with nav_cols[1]:
        if current_idx < len(step_order) - 1:
            if st.button("Next step ➡️", key="next_step_btn", use_container_width=True):
                st.session_state.current_step = step_order[current_idx + 1]
                st.rerun()
        else:
            st.markdown("&nbsp;", unsafe_allow_html=True)  # keep button row height

# ---------------------------------------------------
# Footer
# ---------------------------------------------------

render_footer()
