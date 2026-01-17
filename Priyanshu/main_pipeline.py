import os
import sys

# Import from the SAME directory
from prepro import process_all_pdfs, extract_and_clean_pdf
from chunk_embed import process_cleaned_text, process_multiple_files

def full_pipeline(pdf_dir: str = "books", output_dir: str = "processed"):
    """
    Complete pipeline: Clean PDFs → Chunk → Embed → Store
    """
    print("=" * 60)
    print("STARTING FULL PDF PROCESSING PIPELINE")
    print("=" * 60)
    
    # Step 1: Clean PDFs using your existing code
    print("\nStep 1: Cleaning PDFs...")
    process_all_pdfs()  # This will create cleaned text files in OUTPUT_DIR
    
    # Step 2: Get list of cleaned text files
    cleaned_files = []
    for file in os.listdir(output_dir):
        if file.endswith(".txt") and file != "combined_book.txt":
            cleaned_files.append(os.path.join(output_dir, file))
    
    if not cleaned_files:
        print("No cleaned text files found!")
        return None
    
    print(f"\nFound {len(cleaned_files)} cleaned text files")
    
    # Step 3: Process all cleaned files into vector store
    print("\nStep 2: Chunking and embedding...")
    vector_store = process_multiple_files(
        text_files=cleaned_files,
        collection_name="educational_books"
    )
    
    if vector_store:
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE!")
        print(f"Vector store created at: ./qdrant_db")
        print("Collection: educational_books")
        print("=" * 60)
    
    return vector_store

def process_single_pdf(pdf_path: str, collection_name: str = None):
    """
    Process a single PDF file
    """
    print(f"Processing single PDF: {pdf_path}")
    
    # Step 1: Clean the PDF
    print("Step 1: Cleaning PDF...")
    cleaned_text = extract_and_clean_pdf(pdf_path)
    
    # Save cleaned text temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(cleaned_text)
        temp_file = f.name
    
    # Step 2: Chunk and embed
    print("Step 2: Chunking and embedding...")
    if collection_name is None:
        # Use PDF name as collection name
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        collection_name = f"{base_name}_collection"
    
    vector_store = process_cleaned_text(temp_file, collection_name)
    
    # Clean up temp file
    os.unlink(temp_file)
    
    return vector_store

if __name__ == "__main__":
    # Option 1: Process all PDFs in books folder
    # vector_store = full_pipeline()
    
    # Option 2: Process a single PDF
    vector_store = process_single_pdf(
        pdf_path="books/your_pdf.pdf",  # Your PDF file
        collection_name="mil_course"
    )