class AcademicContextEnhancer:
    """Add academic context to improve understanding of course material"""
    
    def __init__(self):
        self.course_topics = {
            'digital survey': ['online research', 'internet methodology', 'web-based research'],
            'life cycle': ['research process', 'methodological steps', 'phases'],
            'sampling': ['population selection', 'participant recruitment'],
            'data analysis': ['statistical interpretation', 'findings evaluation'],
            'digital divide': ['access limitations', 'coverage error', 'representation issues']
        }
        
        self.course_structure = {
            'Unit 1': 'Internet Mediated Research',
            'Unit 2': 'Online Sampling Methods', 
            'Unit 3': 'Online Survey Methods',
            'Unit 4': 'Digital Ethnography',
            'Unit 5': 'Online Experiments'
        }
    
    def enhance_response(self, question: str, context: str) -> str:
        """Add course-specific context"""
        enhanced = context
        
        # Add course structure awareness
        if any(unit in question.lower() for unit in ['unit', 'chapter']):
            enhanced += "\n\nCOURSE STRUCTURE REFERENCE:\n"
            for unit, title in self.course_structure.items():
                enhanced += f"{unit}: {title}\n"
        
        # Add topic cross-references
        for topic, related in self.course_topics.items():
            if topic in question.lower():
                enhanced += f"\n\nRELATED TOPICS IN COURSE: {', '.join(related)}"
                break
        
        return enhanced