import os
import re
import pdfplumber
from neo4j import GraphDatabase
from pathlib import Path
import json

# === CONFIGURATION ===
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "chatbot01"  # CHANGE THIS!
PDF_FOLDER = "pdfs"
# ====================

def extract_pdf_content(pdf_path):
    """Extract content from PDF with multiple strategies"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"  Warning: {str(e)[:50]}...")
        full_text = ""
    
    return full_text

def analyze_pdf_structure(pdf_path, text):
    """Analyze PDF structure and extract components"""
    filename = os.path.basename(pdf_path)
    
    # Initialize data structure
    data = {
        "file_name": filename,
        "title": "",
        "headings": [],
        "sections": [],
        "activities": [],
        "objectives": [],
        "keywords": [],
        "references": [],
        "content_blocks": []
    }
    
    # Try to extract title from first meaningful lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        # Look for title in first 10 lines
        for i in range(min(10, len(lines))):
            line = lines[i]
            if 10 < len(line) < 200 and not line.startswith('http'):
                data["title"] = line
                break
        
        if not data["title"]:
            data["title"] = filename.replace('.pdf', '')
    
    # Extract headings (various patterns)
    heading_patterns = [
        r'^\d+\.\s+\d+\.\s+(.+?)$',      # 1.1. Heading
        r'^\d+\.\d+\s+(.+?)$',           # 1.1 Heading
        r'^\d+\.\s+(.+?)$',              # 1. Heading
        r'^[IVXLCDM]+\.\s+(.+?)$',       # I. Heading
        r'^[A-Z][A-Z\s]{5,}$',           # ALL CAPS HEADING
        r'^[A-Z][a-z].{10,}[:\.,]?$',    # Normal heading
    ]
    
    # Extract activities
    activity_patterns = [
        r'Activity\s*\d+[\.:]\s*(.+?)(?=\nActivity|\n\d+\.|\n[A-Z]|\Z)',
        r'ACTIVITY\s*\d+[\.:]\s*(.+?)(?=\nACTIVITY|\n\d+\.|\Z)',
        r'Exercise\s*\d+[\.:]\s*(.+?)(?=\nExercise|\n\d+\.|\Z)',
    ]
    
    # Extract objectives
    objective_patterns = [
        r'Objective[s]?[:\s]+(.+?)(?=\n\d+\.|\n[A-Z]|\Z)',
        r'Learning Objective[s]?[:\s]+(.+?)(?=\n\d+\.|\n[A-Z]|\Z)',
    ]
    
    # Process the text
    lines = text.split('\n')
    current_block = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_block:
                data["content_blocks"].append(' '.join(current_block))
                current_block = []
            continue
        
        # Check for headings
        for pattern in heading_patterns:
            match = re.match(pattern, line)
            if match:
                heading = match.group(1) if match.groups() else line
                if len(heading) > 5 and heading not in data["headings"]:
                    data["headings"].append(heading)
                    data["sections"].append(heading)
        
        # Check for activities
        if re.search(r'[Aa]ctivity\s*\d+', line):
            # Extract activity description
            activity_text = line
            idx = lines.index(line)
            # Get next few lines
            for i in range(idx + 1, min(idx + 10, len(lines))):
                next_line = lines[i].strip()
                if next_line and not re.search(r'[Aa]ctivity\s*\d+', next_line):
                    activity_text += " " + next_line
                else:
                    break
            
            if len(activity_text) > 20:
                data["activities"].append(activity_text[:200])
        
        # Check for objectives
        if 'objective' in line.lower() and len(line) < 150:
            data["objectives"].append(line)
        
        # Check for keywords (short, important terms)
        if (line.isupper() or line[0].isupper() and line[1:].islower()) and 2 < len(line) < 50:
            if line not in data["keywords"]:
                data["keywords"].append(line)
        
        # Add to current content block
        current_block.append(line)
    
    # Add last block
    if current_block:
        data["content_blocks"].append(' '.join(current_block))
    
    # Clean up
    data["headings"] = [h for h in data["headings"] if 5 < len(h) < 150]
    data["sections"] = [s for s in data["sections"] if 5 < len(s) < 150]
    data["activities"] = [a for a in data["activities"] if len(a) > 10]
    data["keywords"] = [k for k in data["keywords"] if len(k) > 2]
    
    return data

def create_neo4j_graph_knowledge(all_data):
    """Create knowledge graph in Neo4j with proper syntax"""
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI, 
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        print("  ✓ Connected to Neo4j")
        
        with driver.session() as session:
            # Clear previous data
            session.run("MATCH (n) DETACH DELETE n")
            print("  ✓ Cleared previous data")
            
            # Create all units
            for idx, data in enumerate(all_data):
                unit_id = f"U{idx+1:03d}"
                
                # Create Unit
                session.run("""
                    CREATE (u:Document {
                        id: $id,
                        title: $title,
                        filename: $filename,
                        type: "PDF"
                    })
                """, 
                    id=unit_id,
                    title=data["title"][:100],
                    filename=data["file_name"]
                )
                
                # Create Headings/Sections
                for h_idx, heading in enumerate(data["headings"][:50]):  # Limit to 50
                    heading_id = f"{unit_id}_H{h_idx+1:03d}"
                    session.run("""
                        MATCH (d:Document {id: $unit_id})
                        CREATE (h:Heading {
                            id: $heading_id,
                            text: $text,
                            order: $order
                        })
                        CREATE (d)-[:CONTAINS]->(h)
                    """,
                        unit_id=unit_id,
                        heading_id=heading_id,
                        text=heading[:150],
                        order=h_idx
                    )
                
                # Create Activities
                for a_idx, activity in enumerate(data["activities"][:20]):  # Limit to 20
                    activity_id = f"{unit_id}_A{a_idx+1:03d}"
                    session.run("""
                        MATCH (d:Document {id: $unit_id})
                        CREATE (a:Activity {
                            id: $activity_id,
                            description: $desc,
                            order: $order
                        })
                        CREATE (d)-[:HAS_ACTIVITY]->(a)
                    """,
                        unit_id=unit_id,
                        activity_id=activity_id,
                        desc=activity[:200],
                        order=a_idx
                    )
                
                # Create Keywords
                for k_idx, keyword in enumerate(data["keywords"][:30]):  # Limit to 30
                    keyword_id = f"{unit_id}_K{k_idx+1:03d}"
                    session.run("""
                        MATCH (d:Document {id: $unit_id})
                        CREATE (k:Keyword {
                            id: $keyword_id,
                            term: $term
                        })
                        CREATE (d)-[:DEFINES]->(k)
                    """,
                        unit_id=unit_id,
                        keyword_id=keyword_id,
                        term=keyword[:50]
                    )
                
                print(f"  ✓ Created: {data['file_name']}")
            
            # Get statistics - FIXED UNION QUERY
            result = session.run("""
                MATCH (d:Document) 
                RETURN count(d) as count, 'Documents' as type
                
                UNION ALL
                
                MATCH (h:Heading) 
                RETURN count(h) as count, 'Headings' as type
                
                UNION ALL
                
                MATCH (a:Activity) 
                RETURN count(a) as count, 'Activities' as type
                
                UNION ALL
                
                MATCH (k:Keyword) 
                RETURN count(k) as count, 'Keywords' as type
            """)
            
            stats = []
            for record in result:
                stats.append({
                    "type": record["type"],
                    "count": record["count"]
                })
            
            driver.close()
            return stats
            
    except Exception as e:
        print(f"  ✗ Neo4j Error: {str(e)[:100]}")
        return None

def main():
    """Main function"""
    print("=" * 60)
    print("PDF TO KNOWLEDGE GRAPH CONVERTER")
    print("=" * 60)
    
    # Get current directory
    current_dir = Path(__file__).parent
    pdf_folder = current_dir / PDF_FOLDER
    
    if not pdf_folder.exists():
        print(f"❌ Error: Folder '{PDF_FOLDER}' not found!")
        print(f"   Please create a '{PDF_FOLDER}' folder with your PDFs")
        return
    
    # Find PDFs
    pdf_files = list(pdf_folder.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ Error: No PDF files found in '{PDF_FOLDER}'!")
        return
    
    print(f"\n📚 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files[:8]:  # Show first 8
        print(f"   • {pdf.name}")
    
    if len(pdf_files) > 8:
        print(f"   ... and {len(pdf_files) - 8} more")
    
    # Step 1: Extract data
    print("\n" + "=" * 60)
    print("STEP 1: EXTRACTING DATA FROM PDFS")
    print("=" * 60)
    
    all_data = []
    for pdf_file in pdf_files[:7]:  # Process max 7 files
        try:
            print(f"\n📄 Processing: {pdf_file.name}")
            
            # Extract text
            text = extract_pdf_content(str(pdf_file))
            if not text:
                print(f"  ⚠️  Could not extract text from {pdf_file.name}")
                continue
            
            # Analyze structure
            data = analyze_pdf_structure(str(pdf_file), text)
            all_data.append(data)
            
            # Print summary
            print(f"  ✓ Title: {data['title'][:60]}...")
            print(f"  ✓ Headings: {len(data['headings'])}")
            print(f"  ✓ Activities: {len(data['activities'])}")
            print(f"  ✓ Keywords: {len(data['keywords'])}")
            
        except Exception as e:
            print(f"  ✗ Error processing {pdf_file.name}: {str(e)[:50]}")
    
    if not all_data:
        print("\n❌ No data extracted from PDFs!")
        return
    
    # Save extracted data
    output_file = current_dir / "extracted_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Data saved to: {output_file}")
    
    # Step 2: Create Neo4j Graph
    print("\n" + "=" * 60)
    print("STEP 2: CREATING NEO4J KNOWLEDGE GRAPH")
    print("=" * 60)
    
    if NEO4J_PASSWORD == "your_password_here":
        print("\n❌ Error: Please update the password in the script!")
        print("   Change: NEO4J_PASSWORD = 'your_password_here'")
        print("   To:     NEO4J_PASSWORD = 'your_actual_password'")
        return
    
    print(f"\n🔗 Connecting to Neo4j: {NEO4J_URI}")
    print(f"   Username: {NEO4J_USERNAME}")
    
    stats = create_neo4j_graph_knowledge(all_data)
    
    if stats:
        print("\n" + "=" * 60)
        print("✅ KNOWLEDGE GRAPH CREATED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n📊 STATISTICS:")
        print("-" * 30)
        for stat in stats:
            print(f"  {stat['type']:15} {stat['count']:>5}")
        
        print("\n🌐 OPEN NEO4J BROWSER:")
        print("   URL: http://localhost:7474")
        print("   Username: neo4j")
        print(f"   Password: {NEO4J_PASSWORD[:3]}...")
        
        print("\n🔍 SAMPLE QUERIES:")
        print("""
    -- View all documents
    MATCH (d:Document) RETURN d.title, d.filename
    
    -- View headings from a document
    MATCH (d:Document)-[:CONTAINS]->(h:Heading)
    RETURN d.title, h.text LIMIT 20
    
    -- Count activities per document
    MATCH (d:Document)-[:HAS_ACTIVITY]->(a:Activity)
    RETURN d.title, count(a) as activity_count
    
    -- Search for specific terms
    MATCH (k:Keyword) WHERE k.term CONTAINS 'CASE'
    RETURN k.term LIMIT 10
        """)
        
    else:
        print("\n❌ Failed to create knowledge graph!")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Is Neo4j Desktop/Server running?")
        print("   2. Check: http://localhost:7474")
        print("   3. Verify your password is correct")
        print("   4. Try starting Neo4j: neo4j console")

if __name__ == "__main__":
    main()
