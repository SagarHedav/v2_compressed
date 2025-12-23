from typing import List, Dict, Any
from dataclasses import dataclass
from pinecone_client import PineconeClient
from neo4j_client import Neo4jClient

@dataclass
class RetrievedContext:
    vector_results: List[Dict]
    graph_context: Dict[str, Any]
    combined_context: str

class HybridRetriever:
    def __init__(self, pinecone_index: str = "pdf-knowledge-base"):
        self.pinecone_client = PineconeClient(pinecone_index)
        self.neo4j_client = Neo4jClient()
    
    def retrieve(self, query: str, top_k: int = 5) -> RetrievedContext:
        """Perform hybrid retrieval"""
        # 1. Vector search in Pinecone
        vector_results = self.pinecone_client.search(query, top_k=top_k)
        
        # 2. Extract Neo4j IDs from vector results
        neo4j_ids = []
        for result in vector_results:
            if 'neo4j_id' in result.metadata:
                neo4j_ids.append(result.metadata['neo4j_id'])
        
        # 3. Get related context from Neo4j
        graph_context = {}
        if neo4j_ids:
            graph_context = self.neo4j_client.get_related_context(neo4j_ids)
        
        # 4. Combine context
        combined_context = self._combine_contexts(vector_results, graph_context)
        
        return RetrievedContext(
            vector_results=vector_results,
            graph_context=graph_context,
            combined_context=combined_context
        )
    
    def _combine_contexts(self, vector_results: List[Dict], graph_context: Dict) -> str:
        """Combine vector and graph contexts"""
        combined = "RELEVANT DOCUMENT SECTIONS:\n\n"
        
        # Add vector search results
        combined += "=== Top Matching Chunks ===\n"
        for i, result in enumerate(vector_results, 1):
            combined += f"\n[{i}] From: {result.metadata.get('full_section', 'Unknown')}\n"
            combined += f"Content: {result.metadata.get('text', '')[:300]}...\n"
        
        # Add graph context
        if graph_context and 'context' in graph_context:
            combined += "\n\n=== Related Context from Knowledge Graph ===\n"
            seen_docs = set()
            for item in graph_context['context']:
                if item['doc_id'] and item['doc_id'] not in seen_docs:
                    seen_docs.add(item['doc_id'])
                    combined += f"\nSection: {item['section_path']}\n"
                    if item['content']:
                        combined += f"Content: {item['content'][:500]}...\n"
        
        return combined