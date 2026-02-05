from typing import List, Dict, Any
import spacy
from dataclasses import dataclass

@dataclass
class Entity:
    text: str
    label: str
    start: int
    end: int

class KnowledgeGraphBuilder:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Please download spaCy model: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities from text"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append(Entity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            ))
        
        return entities
    
    def build_entity_graph(self, documents: List[Dict], neo4j_client):
        """Build entity-relationship graph in Neo4j"""
        if not self.nlp:
            print("spaCy not loaded. Skipping entity graph.")
            return
        
        with neo4j_client.driver.session() as session:
            for doc in documents:
                # Extract entities
                entities = self.extract_entities(doc['text'])
                
                # Create entity nodes and relationships
                for entity in entities:
                    # Create entity node
                    session.run("""
                    MERGE (e:Entity {text: $text, type: $type})
                    ON CREATE SET e.count = 1
                    ON MATCH SET e.count = e.count + 1
                    """, text=entity.text, type=entity.label)
                    
                    # Connect entity to document
                    session.run("""
                    MATCH (d:Document {id: $doc_id})
                    MATCH (e:Entity {text: $text, type: $type})
                    MERGE (d)-[:MENTIONS]->(e)
                    """, doc_id=doc['chunk_id'], text=entity.text, type=entity.label)