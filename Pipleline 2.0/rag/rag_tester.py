import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
import time

# Add parent directory to Python's path to make rag module importable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Set ChromaDB directory to the parent's chroma_db before importing rag
CHROMA_DB_ABS_PATH = os.path.abspath(os.path.join(current_dir, "../chroma_db"))
os.environ["CHROMA_DB_DIR"] = CHROMA_DB_ABS_PATH
print(f"Setting ChromaDB directory to: {CHROMA_DB_ABS_PATH}")

# Import rag module initialization
from rag import patch_chromadb_telemetry

# Disable telemetry
os.environ["CHROMADB_TELEMETRY"] = "0"
os.environ["ANONYMIZED_TELEMETRY"] = "False"

st.set_page_config(
    page_title="RAG Testing Tool",
    page_icon="🔍",
    layout="wide"
)

st.markdown("# RAG Testing & Diagnostic Tool")
st.markdown("""
This tool helps you verify that your Retrieval-Augmented Generation (RAG) system is working correctly.

## What is RAG?
RAG enhances AI responses by retrieving relevant information from your uploaded documents. 
When the AI receives a question, it:
1. Searches your document collection for relevant content
2. Uses that content to provide more accurate and informed answers

## How to test if RAG works
1. Upload a document containing specific information
2. Ask questions that require knowledge from that document
3. Compare answers with and without RAG enabled
""")

# Initialize RAG components
@st.cache_resource
def get_document_store():
    # Import here to avoid circular imports after path is properly set
    from rag.document_store import DocumentStore
    return DocumentStore()

try:
    # Test import to verify it works
    from rag.config import RAGConfig
    from rag.document_store import DocumentStore
    
    st.markdown("## 📚 Document Management")
    
    tab1, tab2, tab3 = st.tabs(["Upload & Test", "Vector Store Analysis", "Comparison Test"])
    
    with tab1:
        st.markdown("### 📄 Upload Document")
        uploaded_file = st.file_uploader(
            "Upload a PDF, DOCX, or TXT file with specific information to test",
            type=["pdf", "docx", "txt"]
        )
        
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                temp_file_path = tmp.name
            
            with st.spinner("Processing document..."):
                doc_store = get_document_store()
                success = doc_store.add_document(temp_file_path)
                if success:
                    st.success(f"✅ Successfully added {uploaded_file.name} to knowledge base")
                    
                    # Display some document stats
                    doc_count = doc_store.get_document_count()
                    st.info(f"Knowledge base now contains {doc_count} document chunks")
                else:
                    st.error("⚠️ Failed to add document to knowledge base")
                
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        st.markdown("### 🔍 Test Search")
        search_query = st.text_input("Enter a search query related to your document:")
        num_results = st.slider("Number of results to display:", 1, 10, 3)
        
        if search_query and st.button("Search Knowledge Base"):
            doc_store = get_document_store()
            with st.spinner("Searching..."):
                results = doc_store.search_documents(search_query, num_results)
                
                if results:
                    st.success(f"Found {len(results)} relevant chunks")
                    for i, result in enumerate(results):
                        with st.expander(f"Result {i+1} (Relevance Score: {result['score']:.3f})"):
                            st.markdown(f"**Source:** {result['metadata'].get('source', 'Unknown')}")
                            st.markdown(f"**Content:**\n{result['content']}")
                else:
                    st.warning("No relevant results found. This may indicate that: \n"
                              "1. The document doesn't contain relevant information\n"
                              "2. The search terms don't match the document content\n"
                              "3. The embedding model needs improvement")
                              
        st.markdown("### 🤖 Test RAG Response")
        test_question = st.text_area("Ask a question that should be answered using your document:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Get Answer WITH RAG", use_container_width=True) and test_question:
                # Import here to avoid circular imports
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                with st.spinner("Generating answer with RAG..."):
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-2.0-flash-exp",
                            temperature=0.2
                        )
                        doc_store = get_document_store()
                        
                        # Import after path is set up
                        from rag.rag_agent import RAGAgent
                        
                        role = "Research Assistant"
                        rag_agent = RAGAgent(
                            role=role,
                            basic_prompt=test_question,
                            document_store=doc_store
                        )
                        rag_agent.set_llm(llm)
                        
                        # Get response with RAG
                        result = rag_agent.get_output_with_rag(test_question)
                        st.markdown("### 📚 Answer with RAG:")
                        st.markdown(result)
                        
                        # Save for comparison
                        st.session_state.rag_answer = result
                    except Exception as e:
                        st.error(f"Error generating RAG response: {str(e)}")
                        st.exception(e)  # Show detailed error trace
        
        with col2:
            if st.button("Get Answer WITHOUT RAG", use_container_width=True) and test_question:
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                with st.spinner("Generating answer without RAG..."):
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-2.0-flash-exp", 
                            temperature=0.2
                        )
                        
                        prompt = f"""You are an expert research assistant.
                        
                        Question: {test_question}
                        
                        Answer the question based on your knowledge:
                        """
                        
                        result = llm.invoke(prompt).content
                        st.markdown("### 🤖 Answer without RAG:")
                        st.markdown(result)
                        
                        # Save for comparison
                        st.session_state.no_rag_answer = result
                    except Exception as e:
                        st.error(f"Error generating standard response: {str(e)}")
    
    with tab2:
        st.markdown("### 📊 Vector Store Analysis")
        st.markdown("This tab shows how your documents are processed and stored in the vector database.")
        
        if st.button("Analyze Vector Store"):
            doc_store = get_document_store()
            count = doc_store.get_document_count()
            
            if count == 0:
                st.warning("No documents in the knowledge base. Please upload documents first.")
            else:
                st.success(f"Your knowledge base contains {count} document chunks")
                
                # Sample a few documents to show
                try:
                    random_query = "information"  # Broad query to get some results
                    results = doc_store.search_documents(random_query, n_results=5)
                    
                    st.markdown("### Document Chunk Samples:")
                    for i, result in enumerate(results):
                        with st.expander(f"Chunk {i+1}"):
                            st.markdown(f"**Source:** {result['metadata'].get('source', 'Unknown')}")
                            st.markdown(f"**Page:** {result['metadata'].get('page', 'Unknown')}")
                            st.markdown(f"**Content Length:** {len(result['content'])} characters")
                            st.text_area("Content:", value=result['content'], height=200, key=f"sample_{i}")
                except Exception as e:
                    st.error(f"Error analyzing vector store: {str(e)}")
    
    with tab3:
        st.markdown("### 🔄 Compare RAG vs. No-RAG")
        st.markdown("See the difference between answers with and without RAG side by side.")
        
        if 'rag_answer' in st.session_state and 'no_rag_answer' in st.session_state:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📚 Answer WITH RAG")
                st.markdown(st.session_state.rag_answer)
                
            with col2:
                st.markdown("### 🤖 Answer WITHOUT RAG")
                st.markdown(st.session_state.no_rag_answer)
                
            st.markdown("### ⚖️ Analysis")
            st.markdown("""
            **A good RAG system should:**
            - Include specific information from your documents that's not in the AI's general knowledge
            - Reference sources or details only found in your knowledge base
            - Be more accurate on domain-specific questions
            """)
            
            if st.button("Generate Analysis of Differences"):
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                with st.spinner("Analyzing differences..."):
                    try:
                        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.1)
                        
                        analysis_prompt = f"""Compare these two AI responses to the same question and analyze how they differ:

                        QUESTION:
                        {test_question if 'test_question' in locals() else "Unknown question"}

                        RESPONSE WITH RAG:
                        {st.session_state.rag_answer}

                        RESPONSE WITHOUT RAG:
                        {st.session_state.no_rag_answer}

                        Please analyze:
                        1. What specific information appears in the RAG response that's not in the standard response?
                        2. Is the RAG response more accurate, detailed, or specific?
                        3. Does the RAG response reference sources or details that would likely come from the knowledge base?
                        4. Overall assessment: Is RAG working effectively in this example?
                        """
                        
                        analysis = llm.invoke(analysis_prompt).content
                        st.markdown("### 🔍 Difference Analysis:")
                        st.markdown(analysis)
                    except Exception as e:
                        st.error(f"Error analyzing differences: {str(e)}")
        else:
            st.info("Please generate both RAG and non-RAG answers in the 'Upload & Test' tab first.")
            
except Exception as e:
    st.error(f"Error initializing RAG components: {str(e)}")
    st.exception(e)  # Show detailed error for debugging
    st.markdown("""
    ### Troubleshooting:
    1. Make sure all required packages are installed:
       ```
       pip install chromadb langchain-community sentence-transformers langchain-google-genai
       ```
    2. Make sure the project structure is correct:
       - The 'rag' folder should be in the same directory as 'BaseAgent.py'
       - The 'rag' folder should contain __init__.py
    3. Check if the chroma_db directory has proper permissions
    4. Try running the script with the correct working directory:
       ```
       cd "/Users/hellgamerhell/Downloads/AI generation/vlabs-tool-ai-generation/Pipleline 2.0"
       streamlit run rag/rag_tester.py
       ```
    """)
