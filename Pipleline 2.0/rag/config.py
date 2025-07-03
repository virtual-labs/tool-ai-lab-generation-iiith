import os

class RAGConfig:
    # ChromaDB settings
    CHROMA_PERSIST_DIRECTORY = os.environ.get("CHROMA_DB_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_db")))
    COLLECTION_NAME = "lab_documents"
    
    # Text splitting settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Search settings
    DEFAULT_SEARCH_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.7
    
    # Supported file types
    SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc', '.txt']
    
    # Embedding model
    EMBEDDING_MODEL = "models/embedding-001"
    
    # RAG enhancement settings
    QUERY_REFORMULATION_ENABLED = True
    RERANKING_ENABLED = False
    HYBRID_SEARCH_ENABLED = False
    
    # Context building settings
    MAX_CONTEXT_LENGTH = 4000
    INCLUDE_METADATA = True
    SHOW_RELEVANCE_SCORE = True
    
    # Feedback and evaluation
    COLLECT_FEEDBACK = False
    EVALUATION_METRICS = ["relevance", "coverage"]
    
    @classmethod
    def get_chroma_settings(cls):
        return {
            "persist_directory": cls.CHROMA_PERSIST_DIRECTORY,
            "collection_name": cls.COLLECTION_NAME
        }