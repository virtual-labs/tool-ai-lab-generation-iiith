import streamlit as st
import os
from typing import List
from pathlib import Path
from .document_store import DocumentStore
from .config import RAGConfig

class RAGManager:
    """Manager for RAG document ingestion and retrieval in UI"""
    
    def __init__(self):
        self.document_store = DocumentStore()
        self.config = RAGConfig()
    
    def handle_file_upload(self, uploaded_files):
        """
        Process uploaded files and add to document store
        Returns number of successfully ingested files
        """
        if not uploaded_files:
            return 0
            
        successful = 0
        temp_dir = Path("./temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        for uploaded_file in uploaded_files:
            # Get file extension
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            # Check if extension is supported
            if file_extension not in self.config.SUPPORTED_FILE_TYPES:
                continue
                
            # Save file temporarily
            temp_path = temp_dir / uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Add to document store
            if self.document_store.add_document(str(temp_path)):
                successful += 1
                
            # Remove temp file
            os.remove(temp_path)
                
        return successful
    
    def get_document_count(self):
        """Get the number of documents in the store"""
        return self.document_store.get_document_count()
    
    def clear_document_store(self):
        """Clear all documents from the store"""
        return self.document_store.delete_collection()
        
    def search_documents(self, query, n_results=5):
        """Search documents in the store"""
        return self.document_store.search_documents(query, n_results)
