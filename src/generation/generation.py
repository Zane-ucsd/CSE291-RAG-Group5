"""
Generation module for RAG Pipeline.
Handles prompt construction and Gemini API calls.
"""

from typing import List, Dict, Any, Optional
import time
import warnings
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from multiprocessing import Process, Queue, Manager, TimeoutError as ProcessTimeoutError
import pickle
from ..config import GEMINI_CONFIG, PROMPT_CONFIG
from ..utils import format_context_documents

# Suppress warnings from Google API Core (Python 3.9 compatibility warnings)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

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


# Module-level functions for multiprocessing (must be at module level for pickle)
def _gemini_worker_process(api_key: str, model_name: str, prompt: str, gen_config: Dict[str, Any], 
                           input_tokens_val: int, debug: bool, result_queue: Queue):
    """
    Worker function that runs in a separate process for Gemini API calls.
    Must be at module level for multiprocessing pickle compatibility.
    
    Args:
        api_key: Gemini API key
        model_name: Model name
        prompt: Input prompt
        gen_config: Generation configuration
        input_tokens_val: Pre-calculated input tokens
        debug: Whether to enable debug logging
        result_queue: Queue to put results in
    """
    import warnings
    
    # Suppress warnings in worker process
    warnings.filterwarnings("ignore")
    
    import google.generativeai as genai
    import time
    
    try:
        # Re-initialize in the worker process
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        result_input_tokens = input_tokens_val
        result_output_tokens = 0
        
        if debug:
            print("   [DEBUG] Starting API call...")
        
        # Call API
        response = model.generate_content(prompt, generation_config=gen_config)
        
        if debug:
            print("   [DEBUG] API call completed")
        
        # Extract response text
        try:
            response_text = response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            if debug:
                print(f"   [DEBUG] Error extracting response.text: {e}")
            response_text = str(response)
        
        if debug:
            print(f"   [DEBUG] Response text extracted (length: {len(response_text)})")
        
        # Get token usage from API response (more accurate and faster than counting)
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            if hasattr(usage, 'prompt_token_count'):
                result_input_tokens = usage.prompt_token_count
            if hasattr(usage, 'candidates_token_count'):
                result_output_tokens = usage.candidates_token_count
            elif hasattr(usage, 'total_token_count'):
                total = usage.total_token_count
                result_output_tokens = total - result_input_tokens
        
        # Fallback: simple estimation if API doesn't provide token count
        if result_output_tokens == 0:
            result_output_tokens = len(response_text) // 4
        
        if debug:
            print(f"   [DEBUG] Tokens: Input={result_input_tokens}, Output={result_output_tokens}")
        
        result = {
            "response": response_text,
            "input_tokens": result_input_tokens,
            "output_tokens": result_output_tokens
        }
        result_queue.put(("success", result))
    except Exception as e:
        result_queue.put(("error", str(e)))


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
        self.debug_logging = GEMINI_CONFIG.get("debug_logging", False)
        self.use_multiprocessing = GEMINI_CONFIG.get("use_multiprocessing", True)
        
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
            "timed out",
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
        
        # Initialize input tokens (will be updated from API response if available)
        input_tokens = 0
        
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
                
                if self.use_multiprocessing:
                    # Process mode: Reliable timeout on Windows but slower due to process startup overhead
                    manager = Manager()
                    result_queue = manager.Queue()
                    
                    process = Process(
                        target=_gemini_worker_process,
                        args=(
                            self.api_key,
                            self.model_name,
                            prompt,
                            generation_config,
                            input_tokens,
                            self.debug_logging,
                            result_queue
                        )
                    )
                    process.start()
                    
                    # Wait with timeout
                    process.join(timeout=self.timeout)
                    
                    # Check if process is still alive (timed out)
                    if process.is_alive():
                        process.terminate()
                        process.join(timeout=5)
                        if process.is_alive():
                            process.kill()
                        elapsed = time.time() - start_time
                        raise TimeoutError(
                            f"Generation processing timed out after {elapsed:.1f}s "
                            f"(timeout limit: {self.timeout}s). "
                            f"The process has been terminated."
                        )
                    
                    # Get result from queue
                    if not result_queue.empty():
                        status, result = result_queue.get()
                        if status == "success":
                            processed = result
                        else:
                            raise RuntimeError(f"Error in worker process: {result}")
                    else:
                        elapsed = time.time() - start_time
                        raise TimeoutError(
                            f"Generation processing did not return a result after {elapsed:.1f}s "
                            f"(timeout limit: {self.timeout}s)."
                        )
                    
                    response_text = processed["response"]
                    input_tokens = processed["input_tokens"]
                    output_tokens = processed["output_tokens"]
                else:
                    # Thread mode: Faster but timeout may not work reliably on Windows for blocking I/O
                    def _process_response():
                        """Process response in thread mode."""
                        result_input_tokens = 0
                        result_output_tokens = 0
                        
                        # Call API
                        response = self.model.generate_content(
                            prompt,
                            generation_config=generation_config
                        )
                        
                        # Extract response text
                        try:
                            response_text = response.text if hasattr(response, 'text') else str(response)
                        except Exception as e:
                            if self.debug_logging:
                                print(f"   [DEBUG] Error extracting response.text: {e}")
                            response_text = str(response)
                        
                        # Get token usage from API response
                        if hasattr(response, 'usage_metadata'):
                            usage = response.usage_metadata
                            if hasattr(usage, 'prompt_token_count'):
                                result_input_tokens = usage.prompt_token_count
                            if hasattr(usage, 'candidates_token_count'):
                                result_output_tokens = usage.candidates_token_count
                            elif hasattr(usage, 'total_token_count'):
                                total = usage.total_token_count
                                result_output_tokens = total - result_input_tokens
                        
                        # Fallback: simple estimation if API doesn't provide token count
                        if result_output_tokens == 0:
                            result_output_tokens = len(response_text) // 4
                        
                        return {
                            "response": response_text,
                            "input_tokens": result_input_tokens,
                            "output_tokens": result_output_tokens
                        }
                    
                    # Execute with thread timeout (may not work reliably on Windows)
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(_process_response)
                        try:
                            processed = future.result(timeout=self.timeout)
                        except FutureTimeoutError:
                            future.cancel()
                            elapsed = time.time() - start_time
                            raise TimeoutError(
                                f"Generation processing timed out after {elapsed:.1f}s "
                                f"(timeout limit: {self.timeout}s). "
                                f"Note: Thread timeout may not work reliably on Windows for blocking I/O."
                            )
                    
                    response_text = processed["response"]
                    input_tokens = processed["input_tokens"]
                    output_tokens = processed["output_tokens"]
                
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
            
            except (TimeoutError, FutureTimeoutError) as e:
                # Handle timeout specifically
                last_exception = e
                try:
                    elapsed = time.time() - start_time
                except:
                    elapsed = 0
                error_msg = str(e) if str(e) else f"Request timed out after {self.timeout}s"
                print(f"⏱️  Timeout error: {error_msg}")
                print(f"   Elapsed time: {elapsed:.1f}s, Timeout limit: {self.timeout}s")
                # Timeout is retryable
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"   Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Generation API call failed after {self.max_retries} attempts: {error_msg}")
                    return {
                        "response": f"Error generating response: {error_msg}. The generation process exceeded the timeout limit of {self.timeout}s. This may indicate network issues or the API response processing is stuck.",
                        "sources": [],
                        "num_documents": len(documents),
                        "prompt_length": len(prompt),
                        "input_tokens": input_tokens,
                        "output_tokens": 0,
                        "total_tokens": input_tokens,
                        "error": error_msg,
                        "error_source": "Timeout",
                        "elapsed_time": elapsed
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
        
        start_time = time.time()
        try:
            # Use ThreadPoolExecutor to enforce timeout for initial connection
            def _generate_stream():
                """Helper function to run generate_content in a separate thread."""
                return self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    stream=True
                )
            
            # Execute with timeout for initial connection
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_generate_stream)
                try:
                    response = future.result(timeout=self.timeout)
                except FutureTimeoutError:
                    future.cancel()
                    yield f"Error: Request timed out after {self.timeout}s"
                    return
            
            # Stream chunks with timeout check
            for chunk in response:
                # Check if we've exceeded timeout during streaming
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    yield f"\n[Error: Streaming timed out after {self.timeout}s]"
                    break
                
                if hasattr(chunk, 'text'):
                    yield chunk.text
                else:
                    yield str(chunk)
        
        except (TimeoutError, FutureTimeoutError) as e:
            yield f"Error: Request timed out after {self.timeout}s"
        except Exception as e:
            yield f"Error: {str(e)}"

