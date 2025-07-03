"""
UI Components for AI Pipeline Studio
"""
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Tuple
import os
import time

def render_header():
    """Render the main header component"""
    st.markdown("""
    <div class="modern-header">
        <h1>🚀 Automatic Lab Generation Using Multi-Agent RL</h1>
        <p>Transform your ideas into interactive virtual labs with AI</p>
    </div>
    """, unsafe_allow_html=True)

def render_theme_toggle():
    """Render theme toggle button (Python only, no JS)"""
    mode = "🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"
    if st.button(f"Toggle Theme ({mode})", key="theme_toggle_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

def render_progress_tracker(progress):
    """Render horizontal progress bar only (no steps)"""
    st.markdown(
        f"""
        <div class="progress-container" style="margin-top:1rem;">
            <div class="progress-bar" style="height:18px;">
                <div class="progress-fill" style="width: {progress}%; height:100%;"></div>
            </div>
            <div style="text-align: center; font-weight: 600; color: var(--text-secondary); margin-top:0.5rem;">
                {progress:.1f}% Complete
            </div>
        </div>
        """, unsafe_allow_html=True
    )

def render_step_tracker(current_step, completed_steps):
    """Render horizontal step tracker as boxes below the title"""
    steps = [
        ("requirements", "📝 Requirements"),
        ("review", "👁️ Review"),
        ("implementation", "🔧 Implementation"),
        ("code", "💻 Code"),
        ("documentation", "📚 Documentation"),
        ("website", "🌐 Website"),
    ]
    box_html = '<div style="display:flex;gap:1rem;justify-content:center;margin:1.5rem 0 1.5rem 0;">'
    for step_key, step_label in steps:
        if completed_steps.get(step_key, False):
            color = "background:linear-gradient(135deg,#38a169,#68d391);color:white;border:2px solid #38a169;"
        elif current_step == step_key:
            color = "background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:2px solid #667eea;"
        else:
            color = "background:#e2e8f0;color:#6c757d;border:2px solid #cbd5e1;"
        box_html += f'<div style="padding:1rem 1.5rem;border-radius:12px;font-weight:700;font-size:1.1rem;{color}min-width:120px;text-align:center;transition:all 0.2s;">{step_label}</div>'
    box_html += '</div>'
    st.markdown(box_html, unsafe_allow_html=True)

def render_model_selection():
    """Render AI model selection with temperature and max tokens, and a button to show model limits"""
    model_options = [
        ("gemini-2.5-flash", "Gemini 2.5 Flash", 10, 250_000, 250),
        ("gemini-2.5-flash-lite-preview-06-17", "Gemini 2.5 Flash-Lite Preview 06-17", 15, 250_000, 1000),
        ("gemini-2.5-flash-preview-tts", "Gemini 2.5 Flash Preview TTS", 3, 10_000, 15),
        ("gemini-2.0-flash", "Gemini 2.0 Flash", 15, 1_000_000, 200),
        ("gemini-2.0-flash-preview-image", "Gemini 2.0 Flash Preview Image Generation", 10, 200_000, 100),
        ("gemini-2.0-flash-lite", "Gemini 2.0 Flash-Lite", 30, 1_000_000, 200),
        ("gemini-1.5-flash", "Gemini 1.5 Flash (Deprecated)", 15, 250_000, 50),
        ("gemini-1.5-flash-8b", "Gemini 1.5 Flash-8B (Deprecated)", 15, 250_000, 50),
        ("gemma-3", "Gemma 3 & 3n", 30, 15_000, 14_400),
        ("gemini-embedding-experimental-03-07", "Gemini Embedding Experimental 03-07", 5, None, 100),
    ]

    st.markdown("#### 🤖 AI Configuration")

    model_labels = [label for _, label, *_ in model_options]
    model_keys = [k for k, *_ in model_options]

    default_idx = model_keys.index(
        st.session_state.get("selected_model", model_keys[0])
    ) if st.session_state.get("selected_model", model_keys[0]) in model_keys else 0

    selected_idx = st.selectbox(
        "Choose AI Model:",
        options=list(range(len(model_keys))),
        format_func=lambda i: model_labels[i],
        index=default_idx,
        key="model_selector"
    )

    selected_model = model_keys[selected_idx]

    temp = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get("temperature", 0.1),
        step=0.01,
        key="temperature_slider"
    )

    max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        max_value=1000000,
        value=st.session_state.get("max_tokens", 100000),
        step=1,
        key="max_tokens_input"
    )

    # Show Model Limits button (no rerun, just set flag)
    if st.button("📊 Show Model Limits", key="show_model_limits_btn"):
        st.session_state.show_model_limits = True
        # Do NOT call st.rerun() here

    if st.session_state.get("show_model_limits", False):
        # Always expand sidebar when showing model limits
        st.markdown("""
            <script>
            window.parent.document.querySelector('section[data-testid="stSidebar"]').style.transform = "translateX(0%)";
            window.parent.document.querySelector('section[data-testid="stSidebar"]').style.width = "400px";
            </script>
        """, unsafe_allow_html=True)
        with st.sidebar:
            st.markdown("### Gemini Model Limits")
            st.markdown("""
| Model | RPM | TPM | RPD |
|-------|-----|------|------|
| Gemini 2.5 Pro | -- | -- | -- |
| Gemini 2.5 Flash | 10 | 250,000 | 250 |
| Gemini 2.5 Flash-Lite Preview 06-17 | 15 | 250,000 | 1,000 |
| Gemini 2.5 Flash Preview TTS | 3 | 10,000 | 15 |
| Gemini 2.5 Pro Preview TTS | -- | -- | -- |
| Gemini 2.0 Flash | 15 | 1,000,000 | 200 |
| Gemini 2.0 Flash Preview Image Generation | 10 | 200,000 | 100 |
| Gemini 2.0 Flash-Lite | 30 | 1,000,000 | 200 |
| Imagen 3 | -- | -- | -- |
| Veo 2 | -- | -- | -- |
| Gemini 1.5 Flash (Deprecated) | 15 | 250,000 | 50 |
| Gemini 1.5 Flash-8B (Deprecated) | 15 | 250,000 | 50 |
| Gemini 1.5 Pro (Deprecated) | -- | -- | -- |
| Gemma 3 & 3n | 30 | 15,000 | 14,400 |
| Gemini Embedding Experimental 03-07 | 5 | -- | 100 |
""")
            st.info("RPM = Requests Per Minute, TPM = Tokens Per Minute, RPD = Requests Per Day")
            if st.button("❌ Close Model Limits", key="close_model_limits_btn"):
                st.session_state.show_model_limits = False
                st.rerun()

    return selected_model, temp, max_tokens


def render_file_upload_for_requirements():
    """Render file upload for requirements step only"""
    uploaded_file = st.file_uploader(
        "Upload Requirements PDF", 
        type=['pdf'],
        help="Upload a PDF containing your project requirements",
        key="requirements_file_uploader"
    )
    if uploaded_file is not None:
        temp_path = Path("temp_requirements.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.session_state.uploaded_file = temp_path
        st.markdown(render_status_badge("success", "✅ PDF uploaded successfully!"), unsafe_allow_html=True)
    return uploaded_file

def render_chat_interface():
    """Render chat interface component (no card)"""
    chat_messages = ""
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            chat_messages += f'<div class="chat-message chat-user"><strong>You:</strong> {message["content"]}</div>'
        elif message["role"] == "system":
            chat_messages += f'<div class="chat-message chat-system">{message["content"]}</div>'
        else:
            chat_messages += f'<div class="chat-message chat-ai"><strong>AI:</strong> {message["content"]}</div>'
    st.markdown("#### 🤖 Support Chatbot")
    st.markdown(f"""
    <div class="chat-container">
        {chat_messages}
    </div>
    """, unsafe_allow_html=True)
    chat_input = st.text_input(
        "💬 Ask me anything:",
        placeholder="How can I help you today?",
        key="chat_input"
    )
    send_clicked = st.button("Send 📤", use_container_width=True, key="chat_send_btn")
    clear_clicked = st.button("Clear 🗑️", use_container_width=True, key="chat_clear_btn")
    return chat_input, send_clicked, clear_clicked

def render_footer():
    """Render footer component"""
    st.markdown("---")
    html = f"""
    <div style='text-align: center; color: var(--text-muted); padding: 2rem 0;'>
        <p>🚀 <strong>AI Pipeline Studio</strong> | Powered by LangChain & Google Gemini</p>
        <p>Theme: {'🌙 Dark Mode' if st.session_state.dark_mode else '☀️ Light Mode'}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_status_badge(status_type, message):
    """Render a status badge"""
    return f'<div class="status-badge status-{status_type}">{message}</div>'

def render_rag_file_uploader():
    """Render a file uploader for RAG documents"""
    st.markdown("### 📚 Knowledge Base Documents")
    st.markdown("Upload documents to enhance the AI's knowledge")
    
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, TXT, or HTML files",
        accept_multiple_files=True,
        type=["pdf", "docx", "doc", "txt", "html"],
        key="rag_file_uploader"
    )
    
    return uploaded_files

def render_rag_document_manager():
    """Render the document management UI for RAG"""
    if "rag_documents" not in st.session_state:
        st.session_state.rag_documents = []
    
    # Synchronize UI with database when documents show different counts
    if "document_store" in st.session_state and st.session_state.document_store is not None:
        doc_count = st.session_state.document_store.get_document_count()
        if doc_count > 0 and len(st.session_state.rag_documents) == 0:
            # There are documents in DB but not in UI, attempt to sync
            try:
                # Get sources from document store
                documents = st.session_state.document_store.list_all_documents()
                if documents:
                    # Reset rag_documents with data from database
                    st.session_state.rag_documents = []
                    for doc in documents:
                        source = doc.get('source', 'Unknown document')
                        name = os.path.basename(source) if isinstance(source, str) else 'Unknown document'
                        st.session_state.rag_documents.append({
                            "name": name,
                            "path": source
                        })
                    st.info(f"Synchronized UI with database - found {len(st.session_state.rag_documents)} document sources")
            except Exception as e:
                st.warning(f"Could not synchronize UI with database: {str(e)}")
        
    with st.expander("📑 Manage Knowledge Base", expanded=False):
        # Show list of documents in knowledge base
        if not st.session_state.rag_documents:
            st.info("No documents in knowledge base. Upload documents to get started.")
        else:
            st.markdown("### Current Knowledge Base Documents")
            for i, doc in enumerate(st.session_state.rag_documents):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i+1}. {doc['name']}**")
                with col2:
                    # Fix the remove button functionality
                    if st.button("Remove", key=f"remove_doc_{i}"):
                        # Remove from document store first
                        if "document_store" in st.session_state and st.session_state.document_store is not None:
                            try:
                                # Use the document path for removal
                                success = st.session_state.document_store.remove_document(doc['path'])
                                if success:
                                    # Only remove from UI state if database removal was successful
                                    st.session_state.rag_documents.pop(i)
                                    st.success(f"Removed document: {doc['name']}")
                                else:
                                    st.error(f"Failed to remove document from database: {doc['name']}")
                            except Exception as e:
                                st.error(f"Error removing document: {str(e)}")
                        else:
                            # Just remove from UI if no document store
                            st.session_state.rag_documents.pop(i)
                        st.rerun()
        
        # Clear all documents button
        if st.session_state.rag_documents:
            if st.button("🗑️ Clear All Documents", use_container_width=True):
                # First, try a complete database reset
                if "document_store" in st.session_state and st.session_state.document_store is not None:
                    try:
                        # Use reset_database which is more robust than delete_collection
                        success = st.session_state.document_store.reset_database()
                        if success:
                            # Clear the UI state after successful database reset
                            st.session_state.rag_documents = []
                            st.success("Knowledge base completely reset!")
                            
                            # Force reinitialize the document store
                            initialize_rag(force=True)
                        else:
                            st.error("Failed to reset knowledge base!")
                    except Exception as e:
                        st.error(f"Error resetting knowledge base: {str(e)}")
                else:
                    # Just clear UI state if no document store
                    st.session_state.rag_documents = []
                
                # Force a rerun to update the UI
                st.rerun()
    
        # Add button to force synchronization
        if "document_store" in st.session_state and st.session_state.document_store is not None:
            if st.button("🔄 Sync with Database", use_container_width=True):
                try:
                    # Get document count from document store
                    doc_count = st.session_state.document_store.get_document_count()
                    if doc_count > 0:
                        # Get sources from document store
                        documents = st.session_state.document_store.list_all_documents()
                        if documents:
                            # Reset rag_documents with data from database
                            st.session_state.rag_documents = []
                            for doc in documents:
                                source = doc.get('source', 'Unknown document')
                                name = os.path.basename(source) if isinstance(source, str) else 'Unknown document'
                                st.session_state.rag_documents.append({
                                    "name": name,
                                    "path": source
                                })
                            st.success(f"Found {len(st.session_state.rag_documents)} document sources in database")
                            st.rerun()
                        else:
                            st.warning("No document sources found in database")
                    else:
                        st.warning("No documents found in database")
                except Exception as e:
                    st.error(f"Error syncing with database: {str(e)}")
        
        # Add "Reset Database" button
        if "document_store" in st.session_state and st.session_state.document_store is not None:
            if st.button("🔄 Reset Database (Complete)", use_container_width=True, type="secondary"):
                if st.session_state.document_store.reset_database():
                    st.session_state.rag_documents = []
                    st.success("✅ Database completely reset!")
                    st.rerun()
                else:
                    st.error("Failed to reset database")
            
            # Add a Fix Permissions button
            if st.button("🔧 Fix Database Permissions", use_container_width=True):
                try:
                    persist_dir = os.path.abspath(st.session_state.document_store.config.CHROMA_PERSIST_DIRECTORY)
                    if st.session_state.document_store.check_and_fix_permissions(persist_dir):
                        st.success("✅ Database permissions fixed successfully!")
                        # Force reinitialize the document store
                        initialize_rag(force=True)
                        st.rerun()
                    else:
                        st.error("Failed to fix database permissions")
                except Exception as e:
                    st.error(f"Error fixing permissions: {str(e)}")

def render_rag_settings():
    """Render RAG settings UI"""
    with st.expander("⚙️ RAG Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            rag_enabled = st.checkbox("Enable RAG", 
                value=st.session_state.get("rag_enabled", False),
                key="rag_enabled_checkbox")
            if rag_enabled != st.session_state.get("rag_enabled", False):
                st.session_state.rag_enabled = rag_enabled
                st.rerun()
                
        with col2:
            n_results = st.slider("Number of results", 
                min_value=1, max_value=10, 
                value=st.session_state.get("rag_n_results", 5),
                key="rag_n_results_slider")
            if n_results != st.session_state.get("rag_n_results", 5):
                st.session_state.rag_n_results = n_results

def process_rag_files(uploaded_files, document_store) -> Tuple[int, List[Dict]]:
    """
    Process uploaded files and add them to the document store
    
    Returns:
        Tuple containing (number of successful uploads, list of document metadata)
    """
    # Check if document_store is valid
    if document_store is None:
        st.error("Document store is not initialized properly")
        return 0, []
        
    successful = 0
    docs_metadata = []
    
    for uploaded_file in uploaded_files:
        # Save the uploaded file temporarily - use a more consistent naming pattern
        # Include a timestamp to avoid name collisions
        timestamp = int(time.time())
        filename = uploaded_file.name
        # Remove any existing temp_upload_ prefix to avoid double prefixing
        if filename.startswith("temp_upload_"):
            filename = filename[12:]
        temp_file_path = f"temp_upload_{timestamp}_{filename}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Add to document store
            if document_store.add_document(temp_file_path):
                successful += 1
                docs_metadata.append({
                    "name": uploaded_file.name,
                    "size": uploaded_file.size,
                    "type": uploaded_file.type,
                    "path": temp_file_path
                })
                # Save to session state for management
                if "rag_documents" not in st.session_state:
                    st.session_state.rag_documents = []
                st.session_state.rag_documents.append({
                    "name": uploaded_file.name,
                    "path": temp_file_path
                })
            else:
                st.error(f"Failed to add {uploaded_file.name} to knowledge base")
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    return successful, docs_metadata

def initialize_rag(force=False):
    """Initialize RAG components"""
    try:
        # Setup the basic RAG environment first
        from rag import setup_rag_environment
        if not setup_rag_environment():
            st.error("Failed to setup RAG environment")
            return False
            
        # Initialize document store if not already initialized or forced
        if "document_store" not in st.session_state or st.session_state.document_store is None or force:
            try:
                # Import locally to avoid import errors
                from rag.document_store import DocumentStore
                
                # Initialize the document store
                st.session_state.document_store = DocumentStore()
                
                # Verify initialization
                if hasattr(st.session_state.document_store, 'collection'):
                    st.success("✅ RAG components initialized successfully")
                    return True
                else:
                    st.error("Document store initialized but collection is not accessible")
                    st.session_state.document_store = None
                    return False
                    
            except Exception as e:
                st.error(f"Failed to initialize document store: {str(e)}")
                st.session_state.document_store = None
                return False
        
        # Set default values for RAG settings if needed
        if "rag_enabled" not in st.session_state:
            st.session_state.rag_enabled = False
            
        if "rag_n_results" not in st.session_state:
            st.session_state.rag_n_results = 5
            
        return True
        
    except Exception as e:
        st.error(f"Failed to initialize RAG: {str(e)}")
        st.session_state.document_store = None
        return False

def render_document_search_results(results: List[Dict[str, Any]]):
    """Render search results"""
    if not results:
        st.warning("No relevant documents found")
        return
        
    for i, result in enumerate(results):
        with st.expander(f"Document {i+1} - Score: {result['score']:.3f}", expanded=i==0):
            st.markdown(f"**Source:** {result['metadata'].get('source', 'Unknown')}")
            st.markdown(f"**Content:**\n{result['content']}")

def render_rag_search_section():
    """Render the RAG search section"""
    
    st.markdown("### 🔎 Search Knowledge Base")
    
    query = st.text_input("Enter search query:", key="rag_search_query")
    n_results = st.slider("Number of results:", min_value=1, max_value=10, value=3, key="rag_n_results")
    
    if st.button("🔍 Search", key="rag_search_btn", use_container_width=True):
        if not query:
            st.warning("⚠️ Please enter a search query")
        else:
            with st.spinner("Searching knowledge base..."):
                from rag.rag_manager import RAGManager
                rag_manager = RAGManager()
                results = rag_manager.search_documents(query, n_results)
                render_document_search_results(results)
