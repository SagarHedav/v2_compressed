import os
from dotenv import load_dotenv
from chatbot import PDFChatbot

load_dotenv()

def check_txt_processing():
    """Check if TXT file has been processed"""
    return os.path.exists("data/processed/txt_processed.flag")

def print_detailed_sources(sources):
    """Print sources with more detail for debugging"""
    print("\n" + "="*70)
    print("📚 SOURCES USED:")
    print("="*70)
    for i, source in enumerate(sources, 1):
        print(f"\n{i}. Section: {source.get('full_section', 'Unknown')}")
        print(f"   File: {source.get('source_file', 'N/A')}")
        print(f"   Page: {source.get('page', 'N/A')}")
        print(f"   Preview: {source.get('text', '')[:100]}...")
    print("="*70)

def main():
    print("="*60)
    print("📖 Media Literacy Course Chatbot")
    print("="*60)
    
    # Check if data has been processed
    if not check_txt_processing():
        print("\n❌ TXT file not processed yet!")
        print("Please run: python process_txt_pipeline.py")
        print("First, make sure your TXT files are in: data/txts/")
        return
    
    print("✅ Using existing knowledge base...")
    
    # Initialize chatbot
    try:
        chatbot = PDFChatbot()
    except Exception as e:
        print(f"\n❌ Error initializing chatbot: {e}")
        return
    
    # Interactive chat loop
    print("\n" + "="*60)
    print("💬 Chatbot Ready!")
    print("="*60)
    print("\nCommands:")
    print("  • Type your question to get an answer")
    print("  • Type 'sources' to see detailed source info from last answer")
    print("  • Type 'clear' to clear conversation history")
    print("  • Type 'quit' to exit")
    print("="*60 + "\n")
    
    last_result = None
    
    while True:
        try:
            question = input("\n🎓 You: ").strip()
            
            if question.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if question.lower() == 'clear':
                chatbot.clear_history()
                print("✅ Conversation history cleared!")
                continue
            
            if question.lower() == 'sources' and last_result:
                print_detailed_sources(last_result['sources'])
                continue
            
            if not question:
                continue
            
            print("\n🤔 Thinking...")
            result = chatbot.ask_question(question)
            last_result = result
            
            # Print answer
            print("\n" + "="*70)
            print("🤖 Assistant:")
            print("="*70)
            print(result['answer'])
            print("="*70)
            
            # Show brief source summary
            if result['sources']:
                print(f"\n📚 Answer based on {len(result['sources'])} section(s)")
                print("   Type 'sources' to see detailed source information")
                
                # Show unique sections
                unique_sections = list(set([
                    s.get('full_section', 'Unknown')[:50] 
                    for s in result['sources']
                ]))
                print(f"\n   Sections referenced:")
                for i, section in enumerate(unique_sections[:3], 1):
                    print(f"   {i}. {section}...")
            else:
                print("\n⚠️  No relevant sources found - answer may be incomplete")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()