import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class PineconeClient:
    def __init__(self, index_name: str = "pdf-knowledge-base"):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = index_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # NEW: Initialize Pinecone with new API
        from pinecone import Pinecone, ServerlessSpec
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        
        # Create index if it doesn't exist
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if index_name not in existing_indexes:
            print(f"Creating index: {index_name}")
            self.pc.create_index(
                name=index_name,
                dimension=384,  # Dimension of all-MiniLM-L6-v2
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")  # Use your environment
                )
            )
        
        # Connect to the index
        self.index = self.pc.Index(index_name)
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def upsert_chunks(self, chunks: List[Any]) -> None:
        """Upsert document chunks to Pinecone"""
        vectors = []
        
        for chunk in chunks:
            embedding = self.create_embeddings([chunk.text])[0]
            
            vector = {
                'id': chunk.chunk_id,
                'values': embedding,
                'metadata': {
                    **chunk.metadata,
                    'text': chunk.text[:500],  # Store first 500 chars for reference
                    'neo4j_id': f"section_{hash(' > '.join(chunk.section_path)) % 1000000}",
                    'type': 'document_chunk'
                }
            }
            vectors.append(vector)
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
        
        print(f"Upserted {len(vectors)} vectors to Pinecone")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar chunks"""
        query_embedding = self.create_embeddings([query])[0]
        
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return results['matches']