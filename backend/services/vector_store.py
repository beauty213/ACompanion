import os
import json
import math
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.config import CHROMA_DIR

class VectorStore(ABC):
    """Abstract interface for Anchor vector stores."""

    @abstractmethod
    def add(self, memory_id: str, text: str, metadata: Dict[str, Any], vector: Optional[List[float]] = None) -> None:
        """Add or update an embedding and metadata for a memory."""
        pass

    @abstractmethod
    def search(self, query_text: str, query_vector: Optional[List[float]] = None, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for top_k most similar vectors, returning list of {memory_id, score, metadata}."""
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete vector for memory_id. Must ensure memory cannot be retrieved afterwards."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Clear all vectors."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count stored vectors."""
        pass


STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "you", "your", "he", "him", "his",
    "she", "her", "it", "its", "they", "them", "what", "which", "who", "whom",
    "this", "that", "these", "those", "am", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while",
    "of", "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down", "in",
    "out", "on", "off", "over", "under", "again", "further", "then", "once"
}

def local_text_embedding(text: str, dim: int = 384) -> List[float]:
    """Generates a normalized local dense embedding vector with subword hashing.
    Used when Ollama is offline or as fallback. Positive weighting preserves semantic overlap.
    """
    vec = [0.0] * dim
    clean_text = text.lower().strip()
    words = [w for w in clean_text.split() if w not in STOPWORDS]

    # Word level features
    for word in words:
        h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16) % dim
        vec[h] += 2.0

    # Character subword n-grams (3 and 4)
    for w in words:
        for n in (3, 4):
            for i in range(max(0, len(w) - n + 1)):
                ngram = w[i:i+n]
                h = int(hashlib.md5(ngram.encode("utf-8")).hexdigest(), 16) % dim
                vec[h] += 0.8

    # Normalize vector to unit length
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    else:
        vec[0] = 1.0
    return vec


class ChromaVectorStore(VectorStore):
    """Persistent Chroma Vector Store implementation."""

    def __init__(self, persist_dir: str = CHROMA_DIR):
        self.persist_dir = persist_dir
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        import chromadb
        from chromadb.config import Settings
        
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(
            name="anchor_memories",
            metadata={"description": "Anchor confirmed long-term memories", "hnsw:space": "cosine"}
        )

    def add(self, memory_id: str, text: str, metadata: Dict[str, Any], vector: Optional[List[float]] = None) -> None:
        clean_meta = {
            "memory_id": memory_id,
            "type": str(metadata.get("type", "Experience")),
            "created_at": str(metadata.get("created_at", "")),
            "status": str(metadata.get("status", "user_confirmed")),
            "importance": str(metadata.get("importance", "med")),
        }
        
        # Ensure we always supply an embedding vector so Chroma never downloads models from the internet
        final_vec = vector if (vector is not None and len(vector) > 0) else local_text_embedding(text)

        self.collection.upsert(
            ids=[memory_id],
            documents=[text],
            embeddings=[final_vec],
            metadatas=[clean_meta]
        )

    def search(self, query_text: str, query_vector: Optional[List[float]] = None, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        count = self.collection.count()
        if count == 0:
            return []
        
        limit = min(top_k, count)
        final_vec = query_vector if (query_vector is not None and len(query_vector) > 0) else local_text_embedding(query_text)

        kwargs = {
            "n_results": limit,
            "query_embeddings": [final_vec],
            "include": ["metadatas", "distances", "documents"]
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)

        hits = []
        if results and "ids" in results and len(results["ids"]) > 0:
            ids = results["ids"][0]
            metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
            distances = results.get("distances", [[]])[0] if results.get("distances") else []
            docs = results.get("documents", [[]])[0] if results.get("documents") else []
            
            for idx, mid in enumerate(ids):
                dist = distances[idx] if idx < len(distances) else 1.0
                # Chroma default distance is squared L2 between unit vectors: dist = 2 - 2*cos
                # Therefore cos = 1.0 - (dist / 2.0)
                similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                hits.append({
                    "memory_id": mid,
                    "score": round(similarity, 4),
                    "metadata": metadatas[idx] if idx < len(metadatas) else {},
                    "document": docs[idx] if idx < len(docs) else ""
                })
        return hits


    def delete(self, memory_id: str) -> bool:
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def reset(self) -> None:
        try:
            self.client.delete_collection("anchor_memories")
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection("anchor_memories")

    def count(self) -> int:
        return self.collection.count()


# Singleton vector store accessor
_vector_store_instance: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        try:
            _vector_store_instance = ChromaVectorStore()
        except Exception as e:
            print(f"[VectorStore] Warning: Could not initialize ChromaVectorStore ({e}).")
            raise e
    return _vector_store_instance
