"""
Generation module for RAG Pipeline.
Handles prompt construction and Gemini API calls.
"""

from typing import List, Dict, Any, Optional
import google.generativeai as genai
from ..config import GEMINI_CONFIG, PROMPT_CONFIG
from ..utils import format_context_documents


class GeminiGenerator:
    """
    Generate responses using Google Gemini API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini generator.
        
        Args:
            api_key: Gemini API key (defaults to config)
            model: Gemini model name (defaults to config)
        """
        self.api_key = api_key or GEMINI_CONFIG["api_key"]
        self.model_name = model or GEMINI_CONFIG["model"]
        self.temperature = GEMINI_CONFIG["temperature"]
        self.max_output_tokens = GEMINI_CONFIG["max_output_tokens"]
        self.top_p = GEMINI_CONFIG["top_p"]
        self.top_k = GEMINI_CONFIG["top_k"]
        
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable or update config.py")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def build_prompt(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        max_context_length: Optional[int] = None
    ) -> str:
        """
        Build prompt with query and context documents.
        
        Args:
            query: User query
            documents: Retrieved documents
            system_instruction: System instruction (defaults to config)
            max_context_length: Maximum context length (defaults to config)
            
        Returns:
            Formatted prompt string
        """
        system_instruction = system_instruction or PROMPT_CONFIG["system_instruction"]
        max_context_length = max_context_length or PROMPT_CONFIG["max_context_length"]
        
        # Format context documents
        # Use truncate_per_doc=True when we have many documents (>=10) to include more documents
        truncate_per_doc = len(documents) >= 10
        context = format_context_documents(
            documents, 
            max_length=max_context_length,
            truncate_per_doc=truncate_per_doc
        )
        
        # Build prompt
        prompt = f"""{system_instruction}

Context Documents:
{context}

Question: {query}

Answer based on the context documents above. """
        
        return prompt
    
    def generate(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        max_context_length: Optional[int] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response using Gemini API.
        
        Args:
            query: User query
            documents: Retrieved documents
            system_instruction: System instruction
            max_context_length: Maximum context length
            temperature: Generation temperature
            max_output_tokens: Maximum output tokens
            
        Returns:
            Dictionary with 'response', 'sources', and metadata
        """
        # Build prompt
        prompt = self.build_prompt(query, documents, system_instruction, max_context_length)
        
        # Configure generation parameters
        generation_config = {
            "temperature": temperature or self.temperature,
            "max_output_tokens": max_output_tokens or self.max_output_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k
        }
        
        try:
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract response text
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Extract sources if available
            sources = []
            if PROMPT_CONFIG["include_sources"]:
                sources = [doc.get("source", "Unknown") for doc in documents]
            
            return {
                "response": response_text,
                "sources": sources,
                "num_documents": len(documents),
                "prompt_length": len(prompt)
            }
        
        except Exception as e:
            error_msg = str(e)
            # Identify error source
            if "403" in error_msg or "API key" in error_msg or "leaked" in error_msg.lower():
                error_source = "Google Gemini API"
            else:
                error_source = "Unknown"
            
            return {
                "response": f"Error generating response ({error_source}): {error_msg}",
                "sources": [],
                "num_documents": len(documents),
                "error": error_msg,
                "error_source": error_source
            }
    
    def generate_stream(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        max_context_length: Optional[int] = None
    ):
        """
        Generate response with streaming (generator).
        
        Args:
            query: User query
            documents: Retrieved documents
            system_instruction: System instruction
            max_context_length: Maximum context length
            
        Yields:
            Response chunks
        """
        prompt = self.build_prompt(query, documents, system_instruction, max_context_length)
        
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k
        }
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if hasattr(chunk, 'text'):
                    yield chunk.text
                else:
                    yield str(chunk)
        
        except Exception as e:
            yield f"Error: {str(e)}"

