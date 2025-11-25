"""Vector database operations using ChromaDB."""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

import config

class VectorStore:
    """Manages vector embeddings and similarity search using ChromaDB."""
    
    def __init__(self):
        self._client = None
        self._collection = None
        self._embedding_model = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=str(config.CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
        return self._client
    
    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        return self._embedding_model
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection
    
    def _generate_id(self, text: str, source: str, index: int) -> str:
        """Generate unique ID for a chunk."""
        content = f"{source}_{index}_{text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """Add document chunks to the vector store."""
        if not chunks:
            return 0
        
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            text = chunk.get("text", "")
            source = chunk.get("source_document", "unknown")
            index = chunk.get("chunk_index", 0)
            
            chunk_id = self._generate_id(text, source, index)
            ids.append(chunk_id)
            documents.append(text)
            metadatas.append({
                "source_document": source,
                "chunk_index": index,
                "filename": chunk.get("filename", source)
            })
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        return len(ids)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted_results = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })
        
        return formatted_results
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retrieve all documents from the collection."""
        results = self.collection.get(include=["documents", "metadatas"])
        
        documents = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })
        return documents
    
    def get_document_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get all chunks from a specific source document."""
        results = self.collection.get(
            where={"source_document": source},
            include=["documents", "metadatas"]
        )
        
        documents = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })
        return documents
    
    def clear(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection(config.COLLECTION_NAME)
            self._collection = None
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            count = self.collection.count()
            # Get unique sources
            all_docs = self.collection.get(include=["metadatas"])
            sources = set()
            if all_docs and all_docs["metadatas"]:
                for meta in all_docs["metadatas"]:
                    if meta and "source_document" in meta:
                        sources.add(meta["source_document"])
            
            return {
                "total_chunks": count,
                "unique_sources": len(sources),
                "sources": list(sources)
            }
        except Exception as e:
            return {"error": str(e), "total_chunks": 0, "unique_sources": 0, "sources": []}


# Singleton instance
vector_store = VectorStore()