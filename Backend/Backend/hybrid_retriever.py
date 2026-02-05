from typing import List, Dict, Any
from dataclasses import dataclass
from pinecone_client import PineconeClient
from neo4j_client import Neo4jClient
from query_expander import QueryExpander

@dataclass
class RetrievedContext:
    vector_results: List[Dict]
    graph_context: Dict[str, Any]
    combined_context: str
    expanded_queries: List[str]

class EnhancedHybridRetriever:
    def __init__(self, pinecone_index: str = "pdf-knowledge-base"):
        self.pinecone_client = PineconeClient(pinecone_index)
        self.neo4j_client = Neo4jClient()
        self.query_expander = QueryExpander()
    
    def retrieve(self, query: str, top_k: int = 8) -> RetrievedContext:
        """Perform enhanced hybrid retrieval with query expansion"""
        
        # 1. Expand query (but keep it focused)
        expanded_queries = self.query_expander.expand_query(query)
        print(f"🔍 Original query: {query}")
        print(f"📝 Expanded to {len(expanded_queries)} variations")
        
        # 2. Search with weighted approach
        all_vector_results = []
        
        # Original query gets highest weight
        original_results = self.pinecone_client.search(query, top_k=5)
        for result in original_results:
            result.score = result.score * 1.5  # Boost original query
            all_vector_results.append(result)
        
        # Expanded queries get lower weight
        for expanded_query in expanded_queries[1:4]:  # Only top 3 expansions
            results = self.pinecone_client.search(expanded_query, top_k=2)
            for result in results:
                result.score = result.score * 0.8  # Lower weight
                all_vector_results.append(result)
        
        # 3. Remove duplicates and re-rank
        seen_ids = set()
        unique_results = []
        for result in all_vector_results:
            if result.id not in seen_ids:
                seen_ids.add(result.id)
                unique_results.append(result)
        
        # Sort by adjusted score
        vector_results = sorted(unique_results, 
                              key=lambda x: x.score, 
                              reverse=True)[:top_k]
        
        # DEBUGGING: Print what we retrieved
        print(f"\n📊 Retrieved {len(vector_results)} unique chunks:")
        for i, r in enumerate(vector_results[:3], 1):
            section = r.metadata.get('full_section', 'Unknown')
            score = r.score
            print(f"  {i}. {section[:60]}... (score: {score:.3f})")
        
        # 4. Extract Neo4j IDs from vector results
        neo4j_ids = []
        for result in vector_results:
            if hasattr(result, 'metadata'):
                meta = result.metadata
                for field in ['section_id', 'parent_id', 'neo4j_id']:
                    if field in meta and meta[field] and meta[field] != "ROOT":
                        neo4j_ids.append(meta[field])
                        break
        
        # 5. Get related context from Neo4j
        graph_context = {}
        if neo4j_ids:
            try:
                unique_ids = list(set(neo4j_ids))[:5]
                graph_context = self.neo4j_client.get_related_context(unique_ids)
                print(f"📚 Retrieved {len(graph_context.get('context', []))} graph nodes")
            except Exception as e:
                print(f"⚠️ Neo4j query error: {e}")
                graph_context = {'context': []}
        
        # 6. Combine context intelligently
        combined_context = self._build_intelligent_context(query, vector_results, graph_context)
        
        return RetrievedContext(
            vector_results=vector_results,
            graph_context=graph_context,
            combined_context=combined_context,
            expanded_queries=expanded_queries
        )
    
    def _build_intelligent_context(self, original_query: str, 
                                 vector_results: List[Dict], 
                                 graph_context: Dict) -> str:
        """Build intelligent context with clear section attribution"""
        
        # CHANGE #1: Modified Context Header
        context = f"""QUESTION TO ANSWER: "{original_query}"

===== COURSE MATERIAL RELEVANT TO THIS QUESTION =====

"""
        
        # Group results by section to avoid redundancy
        sections_map = {}
        for result in vector_results:
            meta = result.metadata
            full_section = meta.get('full_section', 'Unknown Section')
            
            if full_section not in sections_map:
                sections_map[full_section] = {
                    'chunks': [],
                    'max_score': 0
                }
            
            sections_map[full_section]['chunks'].append({
                'content': meta.get('text', ''),
                'score': result.score,
                'page': meta.get('page', 'N/A')
            })
            sections_map[full_section]['max_score'] = max(
                sections_map[full_section]['max_score'], 
                result.score
            )
        
        # Sort sections by relevance
        sorted_sections = sorted(
            sections_map.items(), 
            key=lambda x: x[1]['max_score'], 
            reverse=True
        )
        
        # CHANGE #2: Removed Excessive Section Formatting
        # Add sections in answer-friendly format (no excessive formatting)
        for i, (section_path, data) in enumerate(sorted_sections[:5], 1):
            # Simple section header
            context += f"[FROM: {section_path}]\n"
            
            # Combine chunks from same section
            for chunk in data['chunks'][:2]:  # Max 2 chunks per section
                context += f"{chunk['content'].strip()}\n\n"
            
            context += f"{'-'*70}\n\n"
        
        # Add graph context if available
        if graph_context and 'context' in graph_context and graph_context['context']:
            context += "[RELATED INFORMATION FROM COURSE STRUCTURE]\n\n"
            
            # Group by section
            graph_sections = {}
            for item in graph_context['context']:
                section = item.get('section_title', 'Unknown')
                if section not in graph_sections:
                    graph_sections[section] = []
                graph_sections[section].append(item)
            
            for section, items in list(graph_sections.items())[:3]:
                context += f"[FROM: {section}]\n"
                for item in items[:1]:  # Only 1 item per graph section
                    if item.get('content'):
                        context += f"{item['content'].strip()}\n\n"
            
            context += f"{'-'*70}\n\n"
        
        context += f"""===== END OF COURSE MATERIAL =====

CRITICAL INSTRUCTIONS FOR ANSWERING:
1. Provide a DIRECT, SPECIFIC answer to the question using ONLY the material above
2. For comparison questions (like "differentiate between X and Y"):
   - Create a clear comparison structure
   - List specific characteristics of each item
   - Highlight the key differences
3. Always cite which section each piece of information comes from
4. Do NOT just describe what sections contain - EXTRACT and SYNTHESIZE the answer
5. If the material is insufficient, state what's missing clearly
"""
        
        return context

# Backwards compatibility
HybridRetriever = EnhancedHybridRetriever