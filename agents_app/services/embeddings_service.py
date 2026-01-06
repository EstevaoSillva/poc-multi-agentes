"""
Embeddings service - vector storage and RAG retrieval.

Provides:
- Text embedding using sentence-transformers (or other models)
- Vector storage using FAISS (local) or extensible to Milvus/Pinecone
- Similarity search for RAG context retrieval
- Metadata indexing for retrieved snippets
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import numpy as np

# Try to import faiss; fallback if not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Try to import sentence-transformers; fallback if not available
try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class EmbeddingsService:
    """
    Vector embeddings and RAG retrieval service.
    
    Stores embeddings for code files, documentation, and interactions.
    Supports similarity-based retrieval to augment agent context.
    """

    def __init__(
        self,
        session_id: int,
        workspace_path: Path,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
    ):
        """
        Initialize embeddings service.
        
        Args:
            session_id: Session ID
            workspace_path: Path to session workspace
            model_name: SentenceTransformer model (default: all-MiniLM-L6-v2 - fast, 384-dim)
            dimension: Embedding dimension (must match model_name)
        """
        self.session_id = session_id
        self.workspace_path = workspace_path
        self.model_name = model_name
        self.dimension = dimension
        
        # Paths
        self.vectors_dir = workspace_path / "vectors"
        self.vectors_dir.mkdir(parents=True, exist_ok=True)
        self.faiss_index_path = self.vectors_dir / "index.faiss"
        self.metadata_path = self.vectors_dir / "metadata.json"
        
        # Load or initialize model
        self.model = None
        if TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"Warning: Could not load SentenceTransformer model: {e}")
                self.model = None
        
        # Load or initialize FAISS index
        self.index = None
        self.metadata = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one."""
        if self.faiss_index_path.exists() and FAISS_AVAILABLE:
            try:
                self.index = faiss.read_index(str(self.faiss_index_path))
                if self.metadata_path.exists():
                    with open(self.metadata_path, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)
                return
            except Exception as e:
                print(f"Warning: Could not load FAISS index: {e}")
        
        # Create new index
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
        else:
            # Fallback: in-memory simple storage (no FAISS)
            self.index = None
            self.embeddings = []
            self.metadata = []
    
    def _save_index(self):
        """Persist FAISS index and metadata."""
        if self.index is not None and FAISS_AVAILABLE:
            try:
                faiss.write_index(self.index, str(self.faiss_index_path))
            except Exception as e:
                print(f"Warning: Could not save FAISS index: {e}")
        
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Embed a text string.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector (1D numpy array) or None if model unavailable
        """
        if self.model is None:
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"Warning: Could not embed text: {e}")
            return None
    
    def add_document(
        self,
        content: str,
        source: str,
        metadata_dict: Optional[Dict] = None,
    ) -> Optional[int]:
        """
        Add a document (file, snippet, etc) to the vector store.
        
        Args:
            content: Document content to embed
            source: Source identifier (file path, interaction ID, etc)
            metadata_dict: Extra metadata (line range, type, etc)
        
        Returns:
            Document ID in index, or None if embedding failed
        """
        embedding = self.embed_text(content)
        if embedding is None:
            return None
        
        # Create metadata entry
        doc_id = len(self.metadata)
        meta_entry = {
            "id": doc_id,
            "source": source,
            "content_hash": hashlib.md5(content.encode()).hexdigest(),
            "content_length": len(content),
            "embedding_model": self.model_name,
            "metadata": metadata_dict or {},
        }
        
        # Store in FAISS
        if self.index is not None and FAISS_AVAILABLE:
            self.index.add(np.array([embedding]))
        else:
            # Fallback: store in memory
            if not hasattr(self, "embeddings"):
                self.embeddings = []
            self.embeddings.append(embedding)
        
        self.metadata.append(meta_entry)
        self._save_index()
        
        return doc_id
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
    ) -> List[Dict]:
        """
        Search for similar documents (RAG retrieval).
        
        Args:
            query: Query text
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1, L2 distance; lower is more similar)
        
        Returns:
            List of similar documents with metadata and distance
        """
        if self.index is None or len(self.metadata) == 0:
            return []
        
        query_embedding = self.embed_text(query)
        if query_embedding is None:
            return []
        
        # Search in FAISS
        if FAISS_AVAILABLE:
            distances, indices = self.index.search(
                np.array([query_embedding]),
                min(top_k, len(self.metadata))
            )
            
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                
                meta = self.metadata[int(idx)]
                
                # Apply threshold if specified
                if threshold is not None and dist > threshold:
                    continue
                
                results.append({
                    "doc_id": int(idx),
                    "source": meta["source"],
                    "distance": float(dist),
                    "similarity": 1 / (1 + float(dist)),  # Convert L2 dist to similarity (0-1)
                    "metadata": meta["metadata"],
                    "content_hash": meta["content_hash"],
                })
            
            return results
        else:
            # Fallback: simple cosine similarity
            if not hasattr(self, "embeddings") or len(self.embeddings) == 0:
                return []
            
            embeddings_array = np.array(self.embeddings)
            # Cosine similarity
            similarities = np.dot(embeddings_array, query_embedding) / (
                np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_embedding) + 1e-8
            )
            
            top_indices = np.argsort(-similarities)[:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] < (threshold or -1):
                    continue
                
                meta = self.metadata[int(idx)]
                results.append({
                    "doc_id": int(idx),
                    "source": meta["source"],
                    "similarity": float(similarities[idx]),
                    "distance": float(1 - similarities[idx]),
                    "metadata": meta["metadata"],
                    "content_hash": meta["content_hash"],
                })
            
            return results
    
    def get_rag_context(
        self,
        query: str,
        top_k: int = 3,
        max_chars: int = 1500,
    ) -> str:
        """
        Build a RAG context string from similar documents.
        
        Args:
            query: User query or prompt
            top_k: Number of documents to retrieve
            max_chars: Max total characters in context
        
        Returns:
            Formatted context string for agent prompts
        """
        results = self.search(query, top_k=top_k)
        
        if not results:
            return "(No relevant documents found)"
        
        context_lines = ["Retrieved context (RAG):"]
        current_chars = 0
        
        for i, doc in enumerate(results, 1):
            source = doc["source"]
            similarity = doc["similarity"]
            
            line = f"{i}. [{source}] (similarity: {similarity:.2f})"
            if current_chars + len(line) > max_chars:
                break
            
            context_lines.append(line)
            current_chars += len(line)
        
        return "\n".join(context_lines)
    
    def clear(self):
        """Clear all vectors and metadata."""
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatL2(self.dimension)
        else:
            self.embeddings = []
        self.metadata = []
        self._save_index()
    
    def get_stats(self) -> Dict:
        """Get service statistics."""
        return {
            "session_id": self.session_id,
            "model": self.model_name,
            "dimension": self.dimension,
            "num_documents": len(self.metadata),
            "faiss_available": FAISS_AVAILABLE,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "model_loaded": self.model is not None,
        }
    
    def to_dict(self) -> Dict:
        """Export full state (for debugging)."""
        return {
            "session_id": self.session_id,
            "metadata": self.metadata,
            "stats": self.get_stats(),
        }
