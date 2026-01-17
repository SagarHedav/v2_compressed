from typing import List, Dict
import re

class QueryExpander:
    def __init__(self):
        # FOCUSED concept mappings for media literacy
        self.concept_mappings = {
            'life cycle': ['research life cycle', 'research process', 'methodology steps', 'research phases'],
            'digital survey': ['online survey', 'web survey', 'internet survey', 'digital questionnaire'],
            'sampling': ['sample selection', 'participant recruitment', 'sampling methods', 'sample design'],
            'data analysis': ['data interpretation', 'statistical analysis', 'findings analysis'],
            'digital divide': ['access gap', 'digital inequality', 'coverage error', 'access limitations'],
            'methodology': ['research method', 'approach', 'technique'],
            'ethnography': ['digital ethnography', 'online ethnography', 'netnography'],
            'experiment': ['online experiment', 'digital experiment', 'web experiment'],
        }
        
        # Question pattern recognition
        self.question_patterns = {
            'definition': r'what is|what are|define|definition of',
            'process': r'how to|how do|steps|process|lifecycle|phases',
            'comparison': r'difference between|compare|versus|vs',
            'explanation': r'explain|why|how does',
            'list': r'list|enumerate|what are the'
        }
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with FOCUSED variations - not too broad"""
        query_lower = query.lower().strip()
        expanded = [query_lower]  # Original query first
        
        # Detect query type
        query_type = self._detect_query_type(query_lower)
        
        # Extract key concepts
        key_concepts = self._extract_key_concepts(query_lower)
        
        # Generate focused expansions based on query type
        if query_type == 'process':
            # For process questions, add specific variations
            for concept in key_concepts:
                if concept in self.concept_mappings:
                    for variant in self.concept_mappings[concept][:2]:  # Only top 2
                        expanded.append(f"steps in {variant}")
                        expanded.append(f"{variant} process")
        
        elif query_type == 'definition':
            # For definition questions
            for concept in key_concepts:
                if concept in self.concept_mappings:
                    for variant in self.concept_mappings[concept][:2]:
                        expanded.append(variant)
                        expanded.append(f"{variant} definition")
        
        else:
            # General expansion - replace key terms with synonyms
            for concept in key_concepts:
                if concept in self.concept_mappings:
                    for variant in self.concept_mappings[concept][:2]:
                        new_query = query_lower.replace(concept, variant)
                        if new_query != query_lower:
                            expanded.append(new_query)
        
        # Remove duplicates and limit
        seen = set()
        unique_expanded = []
        for q in expanded:
            if q not in seen:
                seen.add(q)
                unique_expanded.append(q)
        
        # Return max 4 queries (original + 3 expansions)
        return unique_expanded[:4]
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of question being asked"""
        for qtype, pattern in self.question_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return qtype
        return 'general'
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from query"""
        # Remove stop words
        stopwords = {'what', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 
                    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                    'how', 'does', 'do', 'are', 'explain', 'describe'}
        
        words = query.lower().split()
        
        # Look for known concepts (multi-word phrases first)
        found_concepts = []
        
        # Check for multi-word concepts
        for concept in self.concept_mappings.keys():
            if concept in query:
                found_concepts.append(concept)
        
        # Check for single words
        for word in words:
            if word not in stopwords and len(word) > 3:
                if word in self.concept_mappings:
                    found_concepts.append(word)
        
        return list(set(found_concepts))