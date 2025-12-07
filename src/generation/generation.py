"""
Generation module for RAG Pipeline.
Handles prompt construction and Gemini API calls.
"""

from typing import List, Dict, Any, Optional
import time
import google.generativeai as genai
from ..config import GEMINI_CONFIG, PROMPT_CONFIG
from ..utils import format_context_documents

# Try to import tiktoken for token counting, fallback to simple estimation
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    # Simple token estimation: ~4 characters per token for English text
    def estimate_tokens(text: str) -> int:
        """Simple token estimation (fallback when tiktoken not available)."""
        return len(text) // 4


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
        self.timeout = GEMINI_CONFIG.get("timeout", 60.0)
        self.max_retries = GEMINI_CONFIG.get("max_retries", 3)
        self.retry_delay = GEMINI_CONFIG.get("retry_delay", 2.0)
        
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable or update config.py")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Initialize token counter (use cl100k_base which is close to Gemini's tokenizer)
        if HAS_TIKTOKEN:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except:
                self.tokenizer = None
        else:
            self.tokenizer = None
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        elif HAS_TIKTOKEN:
            # Fallback: try to get encoding
            try:
                enc = tiktoken.get_encoding("cl100k_base")
                return len(enc.encode(text))
            except:
                return estimate_tokens(text)
        else:
            return estimate_tokens(text)
    
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
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Check if an error is retryable.
        
        Args:
            error: Exception to check
            
        Returns:
            True if error is retryable, False otherwise
        """
        error_msg = str(error).lower()
        error_type = str(type(error))
        
        # Non-retryable errors
        non_retryable_indicators = [
            "403",  # Forbidden
            "401",  # Authentication error
            "api key",
            "invalid",
            "quota exceeded",
            "safety",
            "blocked"
        ]
        
        for indicator in non_retryable_indicators:
            if indicator in error_msg or indicator in error_type:
                return False
        
        # Retryable errors (timeout, network, server errors)
        retryable_indicators = [
            "timeout",
            "connection",
            "network",
            "500",
            "502",
            "503",
            "504",
            "rate limit",
            "429"  # Rate limit (not quota) can be retried with delay
        ]
        
        for indicator in retryable_indicators:
            if indicator in error_msg or indicator in error_type:
                return True
        
        # Default: retry on unknown errors
        return True
    
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
            Includes 'input_tokens' and 'output_tokens' counts
        """
        # Build prompt
        prompt = self.build_prompt(query, documents, system_instruction, max_context_length)
        
        # Count input tokens (initialize before retry loop)
        input_tokens = self.count_tokens(prompt)
        
        # Configure generation parameters
        generation_config = {
            "temperature": temperature or self.temperature,
            "max_output_tokens": max_output_tokens or self.max_output_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k
        }
        
        last_exception = None
        
        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Generate response
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                elapsed_time = time.time() - start_time
                
                # Warn if approaching timeout
                if elapsed_time > self.timeout * 0.8:
                    print(f"⚠️  Generation API call took {elapsed_time:.2f}s (approaching timeout of {self.timeout}s)")
                
                # Extract response text
                response_text = response.text if hasattr(response, 'text') else str(response)
                
                # Count output tokens
                output_tokens = self.count_tokens(response_text)
                
                # Try to get token usage from response if available
                # Gemini API may provide usage_metadata
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    if hasattr(usage, 'prompt_token_count'):
                        input_tokens = usage.prompt_token_count
                    if hasattr(usage, 'candidates_token_count'):
                        output_tokens = usage.candidates_token_count
                    elif hasattr(usage, 'total_token_count'):
                        # If only total is available, estimate output
                        total = usage.total_token_count
                        output_tokens = max(output_tokens, total - input_tokens)
                
                # Extract sources if available
                sources = []
                if PROMPT_CONFIG["include_sources"]:
                    sources = [doc.get("source", "Unknown") for doc in documents]
                
                return {
                    "response": response_text,
                    "sources": sources,
                    "num_documents": len(documents),
                    "prompt_length": len(prompt),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }
            
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                
                # Check if error is retryable
                if not self._is_retryable_error(e):
                    error_source = "Google Gemini API" if "403" in error_msg or "API key" in error_msg else "Unknown"
                    print(f"❌ Non-retryable error: {error_msg[:200]}")
                    return {
                        "response": f"Error generating response ({error_source}): {error_msg}",
                        "sources": [],
                        "num_documents": len(documents),
                        "prompt_length": len(prompt),
                        "input_tokens": input_tokens,
                        "output_tokens": 0,
                        "total_tokens": input_tokens,
                        "error": error_msg,
                        "error_source": error_source
                    }
                
                # Retry with exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️  Generation API call failed (attempt {attempt + 1}/{self.max_retries}): {error_msg[:100]}")
                    print(f"   Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Generation API call failed after {self.max_retries} attempts: {error_msg[:200]}")
                    error_source = "Google Gemini API" if "403" in error_msg or "API key" in error_msg else "Unknown"
                    return {
                        "response": f"Error generating response ({error_source}): {error_msg}",
                        "sources": [],
                        "num_documents": len(documents),
                        "prompt_length": len(prompt),
                        "input_tokens": input_tokens,
                        "output_tokens": 0,
                        "total_tokens": input_tokens,
                        "error": error_msg,
                        "error_source": error_source
                    }
        
        # Should not reach here, but handle just in case
        if last_exception:
            error_msg = str(last_exception)
            error_source = "Google Gemini API" if "403" in error_msg or "API key" in error_msg else "Unknown"
            return {
                "response": f"Error generating response ({error_source}): {error_msg}",
                "sources": [],
                "num_documents": len(documents),
                "prompt_length": len(prompt),
                "input_tokens": input_tokens,
                "output_tokens": 0,
                "total_tokens": input_tokens,
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

