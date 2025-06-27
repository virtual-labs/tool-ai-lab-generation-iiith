import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Tuple
from PyPDF2 import PdfReader
import numpy as np

# Load environment and configure Gemini
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

# Use Gemini for embedding and generation
gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
embed_model = genai.embed_content

# --- PDF Loading and Chunking ---
def load_and_chunk_pdfs(folder: str, chunk_size: int = 500, overlap: int = 100) -> List[Tuple[str, str]]:
    """Load all PDFs in folder, return list of (chunk_text, source_name)."""
    pdf_files = glob.glob(os.path.join(folder, '*.pdf'))
    chunks = []
    for pdf_path in pdf_files:
        reader = PdfReader(pdf_path)
        all_text = "\n".join(page.extract_text() or '' for page in reader.pages)
        # Simple sliding window chunking
        words = all_text.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i+chunk_size])
            if chunk.strip():
                chunks.append((chunk, os.path.basename(pdf_path)))
    return chunks

# --- Embedding ---
def embed_texts(texts: List[str]) -> List[np.ndarray]:
    """Embed a list of texts using Gemini."""
    embeddings = []
    for text in texts:
        response = embed_model(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_query"
        )
        embeddings.append(np.array(response["embedding"]))
    return embeddings

"""questions should be embedded in retrival query 
anytime a quesiton is asked, it should genrate in retrival query, find the nearest chunks, and use them to generate ananswer
sent the top k doucments and come back.
generate using LLMs.
Chunk embedding are in similarty search
"""
# --- Similarity Search ---
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_top_k(query: str, chunk_texts: List[str], chunk_embeds: List[np.ndarray], k: int = 4) -> List[Tuple[str, str]]:
    query_embed = embed_texts([query])[0]
    sims = [cosine_similarity(query_embed, emb) for emb in chunk_embeds]
    top_indices = np.argsort(sims)[-k:][::-1]
    return [(chunk_texts[i], sims[i]) for i in top_indices]

# --- RAG Answer Generation ---
def answer_query(query: str, context_chunks: List[str]) -> str:
    context = "\n\n".join(context_chunks)
    prompt = f"""You are an expert assistant. Use the following context from reference documents to answer the user's question.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer in detail, citing the context where relevant."""
    response = gemini_model.generate_content(prompt)
    return response.text

# --- CLI Loop ---
def main():
    print("\n=== Gemini RAG CLI ===")
    print("Loading and chunking PDFs from 'doucuments/'...")
    chunks_with_src = load_and_chunk_pdfs("doucuments")
    chunk_texts = [c[0] for c in chunks_with_src]
    print(f"Total chunks: {len(chunk_texts)}. Embedding...")
    chunk_embeds = embed_texts(chunk_texts)
    print("Ready! Type your question (or 'exit' to quit):\n")
    while True:
        query = input("Q: ")
        if query.strip().lower() in {"exit", "quit"}:
            break
        top_chunks = retrieve_top_k(query, chunk_texts, chunk_embeds, k=4)
        context_chunks = [c[0] for c in top_chunks]
        answer = answer_query(query, context_chunks)
        print("\n--- Answer ---\n" + answer + "\n")

if __name__ == "__main__":
    main() 