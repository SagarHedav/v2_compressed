from groq import Groq
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from hybrid_retriever import HybridRetriever

load_dotenv()

class PDFChatbot:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        try:
            self.groq_client = Groq(api_key=api_key)
        except TypeError:
            try:
                self.groq_client = Groq(
                    api_key=api_key,
                    timeout=30.0,
                    max_retries=2,
                )
            except:
                self.groq_client = Groq(api_key=api_key)
        
        self.retriever = HybridRetriever()
        self.conversation_history = []
    
    def ask_question(self, question: str, use_history: bool = True) -> Dict[str, Any]:
        """Process question and return answer with synthesis"""
        print("🔍 Analyzing question and retrieving context...")
        
        try:
            # Retrieve enhanced context
            retrieved_context = self.retriever.retrieve(question)
            
            # CRITICAL: Check if we actually got relevant results
            if not retrieved_context.vector_results:
                return {
                    'answer': "I couldn't find relevant information in the course materials to answer your question. Could you rephrase or provide more context?",
                    'sources': [],
                    'vector_results': [],
                    'graph_context': {},
                    'expanded_queries': []
                }
            
            # Build synthesis-focused prompt
            prompt = self._build_synthesis_prompt(question, retrieved_context)
            
            print("🤖 Generating synthesized answer...")
            
            # FIXED: Stronger system prompt with strict grounding
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert academic assistant for a Digital Media and Media Literacy course.

CRITICAL RULES:
1. ONLY use information from the PROVIDED CONTEXT below - never use your general knowledge
2. If the context doesn't contain the answer, explicitly say "The provided materials don't contain information about this"
3. ALWAYS cite the specific section/unit where you found each piece of information
4. When mentioning steps/phases/concepts, cite which section discusses each one
5. Never make up or infer information not explicitly in the context
6. If context is incomplete, acknowledge the gaps

ANSWER STRUCTURE:
1. Direct answer with section citations (e.g., "According to Unit 2, Section 2.1...")
2. Key points with specific section references for EACH point
3. If asked about a process: list steps with section citations for EACH step
4. Acknowledge if context is incomplete or partial

CITATION FORMAT:
- Always use: "According to [Section/Unit]..." or "As stated in [Section]..."
- For each distinct point/step, provide its source section
- Never make general statements without section attribution"""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for factual accuracy
                max_tokens=1500
            )
            
            answer = response.choices[0].message.content
            
            # Store in history
            if use_history:
                self.conversation_history.append({
                    'question': question,
                    'answer': answer,
                    'sources': [r.metadata for r in retrieved_context.vector_results],
                    'expanded_queries': retrieved_context.expanded_queries
                })
            
            return {
                'answer': answer,
                'sources': [r.metadata for r in retrieved_context.vector_results],
                'vector_results': retrieved_context.vector_results,
                'graph_context': retrieved_context.graph_context,
                'expanded_queries': retrieved_context.expanded_queries
            }
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'answer': f"I encountered an error: {str(e)}",
                'sources': [],
                'vector_results': [],
                'graph_context': {},
                'expanded_queries': []
            }

    def _build_synthesis_prompt(self, question: str, retrieved_context: Any) -> str:
        """Build prompt for synthesis with strict grounding"""
        
        history = ""
        if self.conversation_history:
            history = "\n=== PREVIOUS CONVERSATION (for context only) ===\n"
            for conv in self.conversation_history[-2:]:
                history += f"Q: {conv['question']}\nA: {conv['answer'][:150]}...\n\n"
        
        prompt = f"""{history}

=== STUDENT'S CURRENT QUESTION ===
{question}

=== RETRIEVED COURSE MATERIALS (YOUR ONLY SOURCE OF TRUTH) ===

{retrieved_context.combined_context}

=== END OF RETRIEVED MATERIALS ===

INSTRUCTIONS:
1. Answer STRICTLY based on the context above - do not use external knowledge
2. Cite the specific section/unit for EVERY piece of information you provide
3. If the context doesn't fully answer the question, explicitly state what's missing
4. For process/lifecycle questions: list each step with its source section
5. Use this citation format: "According to [Section X.Y]..." or "As stated in [Unit N]..."

Provide your answer now:"""
        
        return prompt
        
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []