import faiss
import numpy as np
import pickle
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, dimension=384):
        # BGE-small default dimension is 384
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension) # Inner Product for cosine similarity (normalized vectors)
        self.metadata: List[Dict[str, Any]] = []

    def add_documents(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Adds embeddings and their corresponding metadata to the index.
        """
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} does not match index dimension {self.dimension}")
        
        self.index.add(embeddings)
        self.metadata.extend(metadata)

    def search(self, query_embedding: np.ndarray, k=5, section_filter: str = None):
        """
        Searches the index for the nearest neighbors.
        Can optionally filter by section (post-filtering for simplicity, pre-filtering would require separate indices or IVFFlat).
        """
        # For small datasets, post-filtering is fine.
        # But FAISS search returns top K. If we filter after, we might lose results.
        # Better: Search K*M, then filter.
        
        search_k = k
        if section_filter:
            search_k = k * 5 # Fetch more to allow for filtering
            
        distances, indices = self.index.search(query_embedding.reshape(1, -1), search_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue
            
            meta = self.metadata[idx]
            dist = distances[0][i]
            
            if section_filter and meta.get("section_type") != section_filter:
                continue
                
            results.append({
                "score": float(dist),
                "metadata": meta
            })
            
            if len(results) >= k:
                break
                
        return results
