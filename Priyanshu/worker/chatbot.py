from groq import Groq
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from hybrid_retriever import HybridRetriever

load_dotenv()

class PDFChatbot:
    def __init__(self):
        # Initialize Groq client with simpler configuration
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Try different initialization methods
        try:
            # Method 1: Newer API
            self.groq_client = Groq(api_key=api_key)
        except TypeError:
            try:
                # Method 2: Older API style
                self.groq_client = Groq(
                    api_key=api_key,
                    timeout=30.0,
                    max_retries=2,
                )
            except:
                # Method 3: Minimal configuration
                self.groq_client = Groq(api_key=api_key)
        
        self.retriever = HybridRetriever()
        self.conversation_history = []
    
    def ask_question(self, question: str, use_history: bool = True) -> Dict[str, Any]:
        """Process question and return answer"""
        # Retrieve relevant context
        retrieved_context = self.retriever.retrieve(question)
        
        # Build prompt
        prompt = self._build_prompt(question, retrieved_context.combined_context)
        
        # Get response from Groq
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or "llama2-70b-4096"
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Be precise and reference the source sections when possible."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1024
        )
        
        answer = response.choices[0].message.content
        
        # Store in history
        if use_history:
            self.conversation_history.append({
                'question': question,
                'answer': answer,
                'sources': [r.metadata for r in retrieved_context.vector_results]
            })
        
        return {
            'answer': answer,
            'sources': [r.metadata for r in retrieved_context.vector_results],
            'vector_results': retrieved_context.vector_results,
            'graph_context': retrieved_context.graph_context
        }
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build the prompt for LLM"""
        history_context = ""
        if self.conversation_history:
            history_context = "\nPrevious conversation:\n"
            for i, conv in enumerate(self.conversation_history[-3:], 1):
                history_context += f"Q{i}: {conv['question']}\nA{i}: {conv['answer']}\n"
        
        prompt = f"""{history_context}

Based on the following context from the document, answer the question.
If the context doesn't contain relevant information, say so clearly.

CONTEXT:
{context}

QUESTION: {question}

ANSWER (be specific and cite relevant sections):"""
        
        return prompt
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []