"""
RAG (Retrieval Augmented Generation) components for the AI Pipeline Studio.
This module initializes and provides access to RAG functionality.
"""
import os
import sys
import shutil

# Set CHROMA_DB_DIR to the absolute path relative to this __init__.py
CHROMA_DB_ABS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_db"))
os.environ["CHROMA_DB_DIR"] = CHROMA_DB_ABS_PATH
print(f"Setting ChromaDB directory to: {CHROMA_DB_ABS_PATH}")

def patch_chromadb_telemetry():
    """
    Patch ChromaDB 1.x telemetry to prevent posthog.capture() argument errors.
    """
    os.environ["CHROMADB_TELEMETRY"] = "0"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    os.environ["POSTHOG_API_KEY"] = "none"

    try:
        import posthog

        def noop_capture(*args, **kwargs):
            return None

        posthog.capture = noop_capture
        # print("✅ Patched posthog.capture in ChromaDB v1.x")
        return True
    except ImportError:
        # print("ℹ️ posthog module not found — no patch needed.")
        return True
    except Exception as e:
        print(f"⚠️ Failed to patch telemetry in ChromaDB v1.x: {e}")
        return False

# Early patch
patch_chromadb_telemetry()

def setup_rag_environment(clean_start=False):
    """
    Set up the RAG environment with proper configuration.
    
    Args:
        clean_start (bool): If True, removes existing ChromaDB directory before initialization
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    # Patch ChromaDB telemetry first
    patch_chromadb_telemetry()
    
    # Always use the absolute path defined at the top of this file
    chroma_dir = CHROMA_DB_ABS_PATH
    
    if clean_start and os.path.exists(chroma_dir):
        try:
            shutil.rmtree(chroma_dir)
        except Exception as e:
            print(f"Error removing directory: {str(e)}")
            return False
    
    os.makedirs(chroma_dir, exist_ok=True)
    
    # Test ChromaDB setup
    try:
        import chromadb
        client = chromadb.PersistentClient(path=chroma_dir)
        collection = client.create_collection("test_collection")
        
        # Clean up test collection
        client.delete_collection("test_collection")
        
    except ImportError:
        print("chromadb package not installed. Please install it with:")
        print("pip install chromadb")
        return False
    except Exception as e:
        print(f"ChromaDB initialization failed: {str(e)}")
        return False
    
    # Test document loaders
    try:
        from langchain_community.document_loaders import TextLoader
    except ImportError:
        print("langchain-community package not installed. Please install it with:")
        print("pip install langchain-community")
        return False
    
    return True

# Add a convenience function for running from command line
def init_rag_environment():
    """Command-line friendly function to initialize the RAG environment"""
    print("Initializing RAG environment...")
    success = setup_rag_environment(clean_start=True)
    if success:
        print("✅ ChromaDB initialized successfully!")
        print("✅ langchain-community document loaders available")
        print("\nRAG environment initialized successfully!")
    else:
        print("❌ RAG environment initialization failed")
    return success

# Allow running directly: python -m rag
if __name__ == "__main__":
    init_rag_environment()
