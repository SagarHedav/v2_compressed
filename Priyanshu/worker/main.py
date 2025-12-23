from pdf_processor import PDFProcessor
from pinecone_client import PineconeClient
from neo4j_client import Neo4jClient
from knowledge_graph import KnowledgeGraphBuilder
from chatbot import PDFChatbot
import os

def process_pdf_and_build_knowledge_base(pdf_path: str):
    """Process PDF and build both vector and graph databases"""
    print("Processing PDF...")
    
    # Process PDF
    processor = PDFProcessor()
    documents = processor.extract_text_from_pdf(pdf_path)
    chunks = processor.chunk_documents(documents)
    
    print(f"Extracted {len(documents)} documents and {len(chunks)} chunks")
    
    # Build Pinecone vector store
    print("Building Pinecone vector store...")
    pinecone_client = PineconeClient()
    pinecone_client.upsert_chunks(chunks)
    
    # Build Neo4j knowledge graph
    print("Building Neo4j knowledge graph...")
    neo4j_client = Neo4jClient()
    neo4j_client.create_knowledge_graph(documents)
    
    print("Knowledge base built successfully!")
    return chunks

def main():
    # Path to your PDF
    pdf_path = "C:/Users/Dell/Desktop/worker/pdfs/MNM-003.pdf"  # Update with your PDF path
    
    # Process PDF (run once)
    if not os.path.exists("data/processed/processed.flag"):
        chunks = process_pdf_and_build_knowledge_base(pdf_path)
        with open("data/processed/processed.flag", "w") as f:
            f.write("processed")
    else:
        print("Using existing knowledge base...")
    
    # Initialize chatbot
    chatbot = PDFChatbot()
    
    # Interactive chat loop
    print("\n" + "="*50)
    print("PDF Chatbot Ready! Type 'quit' to exit.")
    print("="*50 + "\n")
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if question.lower() == 'quit':
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nThinking...")
            result = chatbot.ask_question(question)
            
            print(f"\nAssistant: {result['answer']}")
            
            # Show sources
            if result['sources']:
                print("\nSources:")
                for i, source in enumerate(result['sources'][:3], 1):
                    print(f"  {i}. {source.get('full_section', 'Unknown section')} (Page {source.get('page', 'N/A')})")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()