from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
    
    def close(self):
        self.driver.close()
    
    def create_knowledge_graph(self, documents: List[Dict]) -> None:
        """Create knowledge graph from structured documents"""
        with self.driver.session(database=self.database) as session:
            # Clear existing data (optional)
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create sections hierarchy
            for doc in documents:
                section_path = doc['section_path']
                full_section = doc['full_section']
                
                # Create or get document node
                doc_query = """
                MERGE (d:Document {id: $doc_id})
                SET d.title = $full_section,
                    d.content = $content,
                    d.page = $page
                """
                session.run(doc_query, {
                    'doc_id': doc['chunk_id'],
                    'full_section': full_section,
                    'content': doc['text'],
                    'page': doc['page']
                })
                
                # Create section hierarchy
                for i, section in enumerate(section_path):
                    parent_id = f"root_{hash(' > '.join(section_path[:i]))}" if i > 0 else "ROOT"
                    section_id = f"section_{hash(' > '.join(section_path[:i+1]))}"
                    
                    # Create section node
                    section_query = """
                    MERGE (s:Section {id: $section_id})
                    SET s.title = $title,
                        s.level = $level,
                        s.path = $path
                    """
                    session.run(section_query, {
                        'section_id': section_id,
                        'title': section,
                        'level': i,
                        'path': ' > '.join(section_path[:i+1])
                    })
                    
                    # Connect to parent
                    if i == 0:
                        connect_query = """
                        MATCH (s:Section {id: $section_id})
                        MERGE (r:Root {id: 'DOCUMENT_ROOT'})
                        MERGE (r)-[:HAS_SUBSECTION]->(s)
                        """
                        session.run(connect_query, {'section_id': section_id})
                    else:
                        connect_query = """
                        MATCH (s:Section {id: $section_id})
                        MATCH (p:Section {id: $parent_id})
                        MERGE (p)-[:HAS_SUBSECTION]->(s)
                        """
                        session.run(connect_query, {
                            'section_id': section_id,
                            'parent_id': parent_id
                        })
                    
                    # Connect document to deepest section
                    if i == len(section_path) - 1:
                        doc_section_query = """
                        MATCH (d:Document {id: $doc_id})
                        MATCH (s:Section {id: $section_id})
                        MERGE (s)-[:CONTAINS]->(d)
                        """
                        session.run(doc_section_query, {
                            'doc_id': doc['chunk_id'],
                            'section_id': section_id
                        })
    
    def get_related_context(self, section_ids: List[str]) -> Dict[str, Any]:
        """Get related context from knowledge graph"""
        with self.driver.session(database=self.database) as session:
            # Get the sections and related content - FIXED QUERY
            query = """
            MATCH (s:Section)
            WHERE s.id IN $section_ids
            OPTIONAL MATCH (s)-[:HAS_SUBSECTION*0..2]->(sub:Section)
            OPTIONAL MATCH (sub)-[:CONTAINS]->(d:Document)
            WITH COLLECT(DISTINCT s) + COLLECT(DISTINCT sub) as all_sections,
                COLLECT(DISTINCT d) as all_docs
            UNWIND all_sections as section
            WITH section, all_docs
            UNWIND all_docs as doc
            RETURN DISTINCT 
                section.id as section_id,
                section.title as section_title,
                section.path as section_path,
                section.level as section_level,
                doc.id as doc_id,
                doc.content as content,
                doc.title as doc_title
            ORDER BY section.level
            """
            
            result = session.run(query, section_ids=section_ids)
            context_data = []
            
            for record in result:
                context_data.append({
                    'section_id': record['section_id'],
                    'section_title': record['section_title'],
                    'section_path': record['section_path'],
                    'section_level': record['section_level'],
                    'doc_id': record['doc_id'],
                    'content': record['content'],
                    'doc_title': record['doc_title']
                })
            
            return {'context': context_data}
    
    def query_graph(self, cypher_query: str, params: Dict = None) -> List[Dict]:
        """Execute custom Cypher query"""
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher_query, params or {})
            return [dict(record) for record in result]