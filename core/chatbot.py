import google.generativeai as genai
from typing import List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

class Chatbot:
    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.llm = genai.GenerativeModel("gemini-1.5-flash")

    def search(self, query: str, k: int = 10) -> Tuple[List[float], List[str]]:
        """
        Searches the vector database for relevant chunks based on the query.
        """
        embedded_query = self.embedding_manager.embed_text(query)[0].tolist()
        response = self.embedding_manager.index.query(
            namespace="ns1",
            vector=embedded_query,
            top_k=k,
            include_values=False,
            include_metadata=True
        )
        
        scores = []
        retrieved_chunks = []
        
        for match in response.get('matches', []):
            scores.append(match.get('score'))
            retrieved_chunks.append(match.get('metadata', {}).get('chunk', ''))
            
        return scores, retrieved_chunks

    def filter_chunks(self, scores: List[float], chunks: List[str], 
                     threshold: float = 0.7) -> List[str]:
        """Filter chunks based on similarity score"""
        return [chunk for score, chunk in zip(scores, chunks) if score > threshold]

    def generate_response(self, message: str) -> str:
        try:
            scores, chunks = self.search(message, k=5)
            relevant_chunks = self.filter_chunks(scores, chunks)
            
            if not relevant_chunks:
                return "I couldn't find any relevant information in the knowledge base."
            
            context = "\n".join(relevant_chunks)
            prompt = f"""Based on the following context, please answer the question. 
            If the context doesn't contain relevant information, say so.
            
            Context:
            {context}
            
            Question: {message}
            
            Answer:"""
            
            response = self.llm.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I encountered an error while generating the response: {str(e)}"