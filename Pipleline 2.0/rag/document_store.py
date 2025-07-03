from typing import List, Dict, Any, Optional
import os
import sys
from .config import RAGConfig

# Import and apply telemetry patch before importing ChromaDB
from . import patch_chromadb_telemetry
patch_chromadb_telemetry()

# Now import ChromaDB
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Try to import document loaders from langchain_community
# If not available, create simplified versions
try:
    from langchain_community.document_loaders import (
        PyPDFLoader,
        TextLoader,
        Docx2txtLoader,
        UnstructuredHTMLLoader,
    )
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create simplified document loaders
    class SimpleLoader:
        """Simple document loader that reads text files"""
        def __init__(self, file_path):
            self.file_path = file_path
            
        def load(self):
            """Load document content as text"""
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return [{"page_content": text, "metadata": {"source": self.file_path}}]
            
    # Simple document classes to mimic langchain's structure
    class SimpleTextLoader(SimpleLoader):
        pass
        
    class SimplePyPDFLoader(SimpleLoader):
        def load(self):
            try:
                import PyPDF2
                pages = []
                with open(self.file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            pages.append({
                                "page_content": text,
                                "metadata": {"source": self.file_path, "page": i}
                            })
                return pages
            except ImportError:
                print("PyPDF2 not installed. Using simple text loader as fallback.")
                return super().load()
                
    # Define aliases to match langchain imports
    PyPDFLoader = SimplePyPDFLoader
    TextLoader = SimpleTextLoader
    Docx2txtLoader = SimpleTextLoader  # Fallback to simple text loading
    UnstructuredHTMLLoader = SimpleTextLoader  # Fallback to simple text loading

class DocumentStore:
    """Document store for retrieval augmented generation"""
    
    def __init__(self, embedding_model=None):
        """Initialize the document store with the specified embedding model"""
        self.config = RAGConfig()
        self.embedding_model = embedding_model or self.config.EMBEDDING_MODEL
        
        # Initialize the embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create the directory if it doesn't exist
        import os
        persist_dir = os.path.abspath(self.config.CHROMA_PERSIST_DIRECTORY)
        os.makedirs(persist_dir, exist_ok=True)
        
        # Check and fix permissions for the ChromaDB directory
        self.check_and_fix_permissions(persist_dir)

        # Apply telemetry patch again just to be sure
        patch_chromadb_telemetry()
        
        try:
            # Initialize Chroma client
            self.client = chromadb.PersistentClient(path=persist_dir)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.config.COLLECTION_NAME,
                    embedding_function=self.embedding_function
                )
                print(f"Successfully got collection: {self.config.COLLECTION_NAME}")
            except (ValueError, Exception) as e:
                print(f"Collection not found, creating new one: {str(e)}")
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.config.COLLECTION_NAME,
                    embedding_function=self.embedding_function
                )
                print(f"Created new collection: {self.config.COLLECTION_NAME}")
                
        except Exception as e:
            print(f"Error initializing ChromaDB: {str(e)}")
            # Try to recreate with a clean directory
            import shutil
            try:
                shutil.rmtree(persist_dir)
                os.makedirs(persist_dir, exist_ok=True)
                print(f"Recreated ChromaDB directory at {persist_dir}")
                self.client = chromadb.PersistentClient(path=persist_dir)
                self.collection = self.client.create_collection(
                    name=self.config.COLLECTION_NAME,
                    embedding_function=self.embedding_function
                )
            except Exception as e2:
                print(f"Failed to recreate ChromaDB: {str(e2)}")
                raise ValueError(f"Failed to initialize ChromaDB: {str(e2)}")
    
    def check_and_fix_permissions(self, directory):
        """
        Check and fix permissions for ChromaDB directory and files
        """
        import os
        import stat
        import sys
        
        try:
            print(f"Checking permissions for directory: {directory}")
            
            # Check if directory exists
            if not os.path.exists(directory):
                print(f"Creating directory: {directory}")
                os.makedirs(directory, exist_ok=True)
            
            # Set directory permissions to be writable
            current_permissions = os.stat(directory).st_mode
            if not (current_permissions & stat.S_IWUSR):
                print(f"Setting write permissions for directory: {directory}")
                os.chmod(directory, current_permissions | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            
            # Walk through all files and directories
            for root, dirs, files in os.walk(directory):
                # Set permissions for subdirectories
                for d in dirs:
                    path = os.path.join(root, d)
                    try:
                        current_permissions = os.stat(path).st_mode
                        if not (current_permissions & stat.S_IWUSR):
                            print(f"Setting write permissions for subdirectory: {path}")
                            os.chmod(path, current_permissions | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
                    except Exception as e:
                        print(f"Warning: Could not set permissions for directory {path}: {str(e)}")
                
                # Set permissions for files
                for f in files:
                    path = os.path.join(root, f)
                    try:
                        current_permissions = os.stat(path).st_mode
                        if not (current_permissions & stat.S_IWUSR):
                            print(f"Setting write permissions for file: {path}")
                            os.chmod(path, current_permissions | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
                    except Exception as e:
                        print(f"Warning: Could not set permissions for file {path}: {str(e)}")
            
            return True
        except Exception as e:
            print(f"Error fixing permissions: {str(e)}")
            return False
    
    def add_document(self, filepath: str) -> bool:
        """
        Process and add a document to the vector store
        Returns True if successful, False otherwise
        """
        try:
            file_extension = os.path.splitext(filepath)[1].lower()
            
            # Select appropriate loader based on file extension
            if file_extension == '.pdf':
                loader = PyPDFLoader(filepath)
            elif file_extension == '.docx' or file_extension == '.doc':
                loader = Docx2txtLoader(filepath)
            elif file_extension == '.txt':
                loader = TextLoader(filepath)
            elif file_extension == '.html':
                loader = UnstructuredHTMLLoader(filepath)
            else:
                print(f"Unsupported file type: {file_extension}")
                return False
            
            # Load the document
            documents = loader.load()
            
            # If using our simple loaders that don't have langchain's structure
            if not LANGCHAIN_AVAILABLE:
                chunks = []
                for doc in documents:
                    # Simple chunking if langchain_text_splitters not available
                    text = doc["page_content"]
                    chunk_size = self.config.CHUNK_SIZE
                    overlap = self.config.CHUNK_OVERLAP
                    text_chunks = []
                    
                    for i in range(0, len(text), chunk_size - overlap):
                        chunk = text[i:i + chunk_size]
                        if len(chunk) < chunk_size / 2 and text_chunks:
                            # Merge small final chunks
                            text_chunks[-1] += chunk
                        else:
                            text_chunks.append(chunk)
                    
                    for i, chunk in enumerate(text_chunks):
                        chunks.append({
                            "page_content": chunk,
                            "metadata": {
                                **doc["metadata"],
                                "chunk": i
                            }
                        })
            else:
                # Split the document into chunks using langchain
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.config.CHUNK_SIZE,
                    chunk_overlap=self.config.CHUNK_OVERLAP
                )
                chunks = text_splitter.split_documents(documents)
            
            # Add chunks to the collection
            for i, chunk in enumerate(chunks):
                content = chunk.page_content if hasattr(chunk, "page_content") else chunk["page_content"]
                metadata = chunk.metadata if hasattr(chunk, "metadata") else chunk["metadata"]
                
                self.collection.add(
                    ids=[f"{os.path.basename(filepath)}-{i}"],
                    documents=[content],
                    metadatas=[{
                        "source": filepath,
                        "page": metadata.get("page", 0),
                        "chunk": i
                    }]
                )
            
            return True
        
        except Exception as e:
            print(f"Error adding document: {str(e)}")
            return False
    
    def search_documents(
        self, 
        query: str, 
        n_results: int = 5, 
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the document store for relevant documents
        Returns a list of dictionaries containing document ID, content, metadata, and score
        """
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_dict  # Filter if provided
            )
            
            # Format the results
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": results['distances'][0][i] if 'distances' in results else 0
                    })
            
            return formatted_results
        
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        """Get the number of documents in the collection"""
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error getting document count: {str(e)}")
            # Try to recreate collection if it doesn't exist
            try:
                self.collection = self.client.create_collection(
                    name=self.config.COLLECTION_NAME,
                    embedding_function=self.embedding_function
                )
                print(f"Recreated collection: {self.config.COLLECTION_NAME}")
                return 0
            except Exception as e2:
                print(f"Failed to recreate collection: {str(e2)}")
                return 0
    
    def list_all_documents(self) -> List[Dict]:
        """List all documents in the collection with their metadata"""
        try:
            # Get all documents from the collection (up to a reasonable limit)
            results = self.collection.peek(limit=1000)
            
            # Format the results in a more useful way
            document_list = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'])):
                    document_list.append({
                        "id": results['ids'][i],
                        "content": results['documents'][i] if i < len(results['documents']) else "",
                        "metadata": results['metadatas'][i] if i < len(results['metadatas']) else {},
                    })
            
            # Group by source file for better UI display
            grouped_docs = {}
            for doc in document_list:
                source = doc["metadata"].get("source", "Unknown")
                if source not in grouped_docs:
                    grouped_docs[source] = []
                grouped_docs[source].append(doc)
            
            # Convert to list of sources with document counts
            result = [{"source": source, "count": len(docs)} for source, docs in grouped_docs.items()]
            return result
            
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []
    
    def delete_collection(self) -> bool:
        """Delete the entire collection and recreate an empty one. Use with caution!"""
        try:
            self.client.delete_collection(self.config.COLLECTION_NAME)
            # Immediately recreate the collection to avoid "not found" errors
            self.collection = self.client.create_collection(
                name=self.config.COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            print(f"Deleted and recreated empty collection: {self.config.COLLECTION_NAME}")
            return True
        except Exception as e:
            print(f"Error managing collection: {str(e)}")
            # Try to create collection if it doesn't exist
            try:
                self.collection = self.client.create_collection(
                    name=self.config.COLLECTION_NAME, 
                    embedding_function=self.embedding_function
                )
                return True
            except:
                return False
    
    def reset_database(self) -> bool:
        """Completely reset the database by recreating the ChromaDB directory"""
        try:
            # Close the client connection if possible
            if hasattr(self, 'client') and hasattr(self.client, 'close'):
                try:
                    self.client.close()
                    # Sleep briefly to ensure connection is closed
                    import time
                    time.sleep(1)
                except:
                    pass
            
            # Get the directory path
            import os
            import shutil
            persist_dir = os.path.abspath(self.config.CHROMA_PERSIST_DIRECTORY)
            
            # Check and fix permissions before attempting to delete
            self.check_and_fix_permissions(persist_dir)
            
            # Force delete the collection before removing directory
            try:
                import chromadb
                temp_client = chromadb.PersistentClient(path=persist_dir)
                try:
                    temp_client.delete_collection(self.config.COLLECTION_NAME)
                    print(f"Successfully deleted collection {self.config.COLLECTION_NAME}")
                except Exception as e:
                    print(f"Collection may not exist: {str(e)}")
                temp_client.reset()
            except Exception as e:
                print(f"Error with force delete: {str(e)}")
            
            # Remove and recreate the directory
            if os.path.exists(persist_dir):
                print(f"Removing directory: {persist_dir}")
                # Use force delete with force=True if available
                try:
                    import shutil
                    shutil.rmtree(persist_dir, ignore_errors=True)
                except Exception as e:
                    print(f"Error removing directory: {str(e)}")
                    # Try individual file deletion if rmtree fails
                    for root, dirs, files in os.walk(persist_dir, topdown=False):
                        for name in files:
                            try:
                                os.chmod(os.path.join(root, name), 0o777)
                                os.remove(os.path.join(root, name))
                            except:
                                pass
                        for name in dirs:
                            try:
                                os.chmod(os.path.join(root, name), 0o777)
                                os.rmdir(os.path.join(root, name))
                            except:
                                pass
            
            # Create the directory fresh
            print(f"Creating new directory: {persist_dir}")
            os.makedirs(persist_dir, exist_ok=True)
            
            # Make sure the new directory is writable
            self.check_and_fix_permissions(persist_dir)
            
            # Reinitialize the client and collection
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.create_collection(
                name=self.config.COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            print(f"Database completely reset at {persist_dir}")
            return True
        except Exception as e:
            print(f"Failed to reset database: {str(e)}")
            return False
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a specific document from the collection by ID or path"""
        try:
            # If doc_id is a path, we need to find all chunks with that path
            if os.path.exists(doc_id) or '/' in doc_id or '\\' in doc_id:
                # This is a file path, find all documents with this source
                source_path = doc_id
                
                # Get all documents
                results = self.collection.peek(limit=1000)
                
                # Find document IDs matching the source
                ids_to_delete = []
                if results['ids'] and len(results['ids']) > 0:
                    for i, metadata in enumerate(results['metadatas']):
                        if 'source' in metadata and metadata['source'] == source_path:
                            ids_to_delete.append(results['ids'][i])
                
                if ids_to_delete:
                    # Delete documents by ID
                    self.collection.delete(ids=ids_to_delete)
                    print(f"Removed {len(ids_to_delete)} chunks for document: {source_path}")
                    return True
                else:
                    print(f"No documents found with source: {source_path}")
                    return False
            else:
                # Direct ID deletion
                self.collection.delete(ids=[doc_id])
                return True
        except Exception as e:
            print(f"Error removing document: {str(e)}")
            return False