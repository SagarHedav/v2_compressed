import PyPDF2
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    text: str
    metadata: Dict
    section_path: List[str]
    chunk_id: str

class PDFProcessor:
    def __init__(self):
        self.section_pattern = re.compile(r'^(\d+(\.\d+)*)\s+(.+)$')
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text with structure from PDF"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            documents = []
            current_section = []
            current_text = []
            page_num = 0
            
            for page in pdf_reader.pages:
                page_num += 1
                text = page.extract_text()
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if line is a section header
                    match = self.section_pattern.match(line)
                    if match:
                        # Save previous section if exists
                        if current_text:
                            doc = self._create_document(current_text, current_section, page_num)
                            documents.append(doc)
                            current_text = []
                        
                        # Update current section
                        section_num = match.group(1)
                        section_title = match.group(3)
                        current_section = self._update_section_path(current_section, section_num, section_title)
                    else:
                        current_text.append(line)
            
            # Add last document
            if current_text:
                doc = self._create_document(current_text, current_section, page_num)
                documents.append(doc)
            
            return documents
    
    def _update_section_path(self, current_path: List, section_num: str, title: str) -> List:
        """Update section hierarchy based on numbering"""
        level = len(section_num.split('.')) - 1
        
        if level < len(current_path):
            return current_path[:level] + [f"{section_num} {title}"]
        else:
            return current_path + [f"{section_num} {title}"]
    
    def _create_document(self, text_lines: List[str], section_path: List[str], page: int) -> Dict:
        """Create structured document"""
        return {
            'text': ' '.join(text_lines),
            'section_path': section_path.copy(),
            'page': page,
            'full_section': ' > '.join(section_path) if section_path else "Document",
            'chunk_id': f"chunk_{len(section_path)}_{page}_{hash(' '.join(text_lines)) % 10000}"
        }
    
    def chunk_documents(self, documents: List[Dict], chunk_size: int = 500, overlap: int = 50) -> List[DocumentChunk]:
        """Split documents into overlapping chunks"""
        chunks = []
        
        for doc in documents:
            text = doc['text']
            words = text.split()
            
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                chunk = DocumentChunk(
                    text=chunk_text,
                    metadata={
                        'section_path': doc['section_path'],
                        'full_section': doc['full_section'],
                        'page': doc['page'],
                        'chunk_index': i // (chunk_size - overlap),
                        'doc_id': doc['chunk_id']
                    },
                    section_path=doc['section_path'],
                    chunk_id=f"{doc['chunk_id']}_chunk{i}"
                )
                chunks.append(chunk)
        
        return chunks