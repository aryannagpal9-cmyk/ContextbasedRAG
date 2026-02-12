from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text_chunks: list[str]) -> np.ndarray:
        """
        Generates embeddings for a list of text strings.
        """
        if not text_chunks:
            return np.array([])
        
        embeddings = self.model.encode(text_chunks, normalize_embeddings=True)
        return embeddings

    def get_similarity_scores(self, query: str, candidates: list[str]) -> list[float]:
        """
        Calculates cosine similarity scores between a query and a list of candidates.
        """
        if not candidates:
            return []
            
        q_emb = self.embed([query])[0]
        c_embs = self.embed(candidates)
        
        # Cosine similarity for normalized vectors is just the dot product
        similarities = np.dot(c_embs, q_emb)
        return similarities.tolist()
