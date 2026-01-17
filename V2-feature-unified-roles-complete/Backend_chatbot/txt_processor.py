import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class DocumentSection:
    id: str
    title: str
    content: str
    level: int
    section_path: List[str]
    parent_id: str = None
    page: int = 1
    source_file: str = ""  # NEW: Track which PDF this came from
    
class TXTStructureParser:
    def __init__(self):
        # ENHANCED patterns for better hierarchy detection
        self.patterns = {
            'chapter': re.compile(r'^(Chapter|CHAPTER|CH\.?)\s+(\d+|[IVXLCDM]+)[.:]\s*(.+)$', re.IGNORECASE),
            'unit': re.compile(r'^(Unit|UNIT)\s+(\d+)[.:]\s*(.+)$', re.IGNORECASE),  # NEW
            'section': re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$'),  # 1.2.3 Title
            'subsection': re.compile(r'^([A-Z])\.\s+(.+)$'),  # A. Title
            'bullet': re.compile(r'^[•\-\*]\s+(.+)$'),
            'numbered': re.compile(r'^\(\d+\)\s+(.+)$'),
        }
    
    def parse_txt_file(self, file_path: str) -> List[DocumentSection]:
        """Parse structured TXT file into hierarchical sections"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        sections = []
        current_hierarchy = []
        current_content = []
        section_counter = 0
        
        # Extract source filename
        import os
        source_file = os.path.basename(file_path)
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check what type of line this is
            line_type, title, level = self._classify_line(line)
            
            if line_type in ['chapter', 'unit', 'section', 'subsection']:
                # Save previous section if exists
                if current_hierarchy and current_content:
                    self._save_section(current_hierarchy[-1], current_content, sections)
                    current_content = []
                
                # Create new section
                section_id = f"{source_file}_s{section_counter}"  # FIXED: More unique IDs
                section_counter += 1
                
                # Determine parent based on level hierarchy
                parent_id = None
                if current_hierarchy:
                    # Remove sections at same or deeper level
                    while current_hierarchy and current_hierarchy[-1].level >= level:
                        current_hierarchy.pop()
                    if current_hierarchy:
                        parent_id = current_hierarchy[-1].id
                
                # Build section path
                section_path = [s.title for s in current_hierarchy] + [title]
                
                section = DocumentSection(
                    id=section_id,
                    title=title,
                    content="",
                    level=level,
                    section_path=section_path,
                    parent_id=parent_id,
                    page=line_num // 50 + 1,
                    source_file=source_file
                )
                
                sections.append(section)
                current_hierarchy.append(section)
                
            else:
                # Content line - add to current section
                if current_hierarchy:
                    current_content.append(line)
                else:
                    # Orphan content before first section - create intro
                    if not any(s.title == "Introduction" for s in sections):
                        section = DocumentSection(
                            id=f"{source_file}_intro_0",
                            title="Introduction",
                            content=line,
                            level=0,
                            section_path=["Introduction"],
                            parent_id=None,
                            page=1,
                            source_file=source_file
                        )
                        sections.append(section)
                        current_hierarchy.append(section)
                    else:
                        # Append to intro
                        for s in sections:
                            if s.title == "Introduction":
                                s.content += " " + line
                                break
        
        # Save last section
        if current_hierarchy and current_content:
            self._save_section(current_hierarchy[-1], current_content, sections)
        
        print(f"✅ Parsed {len(sections)} sections from {source_file}")
        return sections
    
    def _classify_line(self, line: str) -> Tuple[str, str, int]:
        """Classify line and determine hierarchy level"""
        
        # Check for Unit (level 1, same as chapter)
        unit_match = self.patterns['unit'].match(line)
        if unit_match:
            return 'unit', unit_match.group(3).strip(), 1
        
        # Check for chapter
        chapter_match = self.patterns['chapter'].match(line)
        if chapter_match:
            return 'chapter', chapter_match.group(3).strip(), 1
        
        # Check for numbered section (1.2.3)
        section_match = self.patterns['section'].match(line)
        if section_match:
            section_num = section_match.group(1)
            title = section_match.group(2)
            # Count dots to determine depth
            level = len(section_num.split('.')) + 1  # +1 because chapter/unit is 1
            return 'section', title, level
        
        # Check for subsection (A. Title)
        subsection_match = self.patterns['subsection'].match(line)
        if subsection_match:
            return 'subsection', subsection_match.group(2).strip(), 4
        
        # Check for bullets
        bullet_match = self.patterns['bullet'].match(line)
        if bullet_match:
            return 'bullet', bullet_match.group(1).strip(), 5
        
        # Check for numbered lists
        numbered_match = self.patterns['numbered'].match(line)
        if numbered_match:
            return 'numbered', numbered_match.group(1).strip(), 5
        
        # Default: content line
        return 'content', line, 99
    
    def _save_section(self, section, content_lines, sections):
        """Save content to section"""
        content = " ".join(content_lines).strip()
        section.content = content
        
        # Update in list
        for i, s in enumerate(sections):
            if s.id == section.id:
                sections[i] = section
                break
    
    def create_chunks(self, sections: List[DocumentSection], 
                     chunk_size: int = 400, overlap: int = 50) -> List[Dict]:
        """Create overlapping chunks with PROPER metadata"""
        chunks = []
        chunk_counter = 0
        
        for section in sections:
            # Skip empty sections
            if not section.content or len(section.content.strip()) < 20:
                continue
            
            # Clean content
            content = section.content.strip()
            words = content.split()
            
            # Skip very short sections
            if len(words) < 10:
                continue
            
            # Create overlapping chunks
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                # CRITICAL: Proper metadata construction
                metadata = {
                    'section_id': section.id,
                    'title': section.title[:200],
                    'full_section': ' > '.join(section.section_path)[:300],
                    'level': str(section.level),
                    'parent_id': section.parent_id if section.parent_id else "ROOT",
                    'page': str(section.page),
                    'chunk_index': str(i // (chunk_size - overlap)),
                    'source_file': section.source_file,
                    'text': chunk_text[:500],  # First 500 chars for preview
                }
                
                # Ensure no None values
                metadata = {k: v for k, v in metadata.items() if v is not None}
                
                chunk = {
                    'id': f"{section.id}_chunk{chunk_counter}",
                    'text': chunk_text,
                    'metadata': metadata,
                    'section_path': section.section_path
                }
                chunks.append(chunk)
                chunk_counter += 1
        
        print(f"✅ Created {len(chunks)} chunks from {len(sections)} sections")
        
        # DEBUGGING: Show sample chunks
        print("\n📋 Sample chunks created:")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"  {i}. Section: {chunk['metadata']['full_section'][:50]}")
            print(f"     Text preview: {chunk['text'][:80]}...")
        
        return chunks