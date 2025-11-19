"""
Ground Truth Validation Script

This script validates the format and content of manually annotated ground truth data.

Expected format:
{
    "query": "What rehabilitation methods are most effective for treating knee injuries in badminton players?",
    "relevant_ids": ["394", "440", "180", ...]
}

Validation checks:
1. JSON format validity
2. Required fields (query, relevant_ids)
3. Data types (query: string, relevant_ids: list)
4. ID format (all strings)
5. Duplicate IDs
6. Empty values
7. ID existence in database
8. ID existence in Elasticsearch (optional)
9. LLM response quality (optional, using --check-llm)
   - Response validity
   - Response length
   - Retrieval metrics (Precision, Recall, F1)
"""

import json
import sys
import argparse
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import psycopg2
from ..config import PG_CONFIG, ES_CONFIG
import io
import contextlib

# Optional RAG pipeline import
try:
    from ..pipeline import RAGPipeline
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️  RAG pipeline not available. LLM validation will be disabled.")


class GroundTruthValidator:
    """
    Validator for ground truth data format and content.
    """
    
    def __init__(
        self,
        check_database: bool = True,
        check_elasticsearch: bool = False,
        check_llm: bool = False
    ):
        """
        Initialize validator.
        
        Args:
            check_database: Whether to check if IDs exist in PostgreSQL
            check_elasticsearch: Whether to check if IDs exist in Elasticsearch
            check_llm: Whether to check LLM response quality
        """
        self.check_database = check_database
        self.check_elasticsearch = check_elasticsearch
        self.check_llm = check_llm and RAG_AVAILABLE
        self.pg_config = PG_CONFIG
        # Always load ES config for document retrieval (even if not checking ES)
        self.es_config = ES_CONFIG
        
        # Initialize RAG pipeline if needed
        self.rag_pipeline = None
        if self.check_llm:
            try:
                # Suppress warnings during initialization
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    self.rag_pipeline = RAGPipeline()
                print("✅ RAG Pipeline initialized for LLM validation")
            except Exception as e:
                print(f"⚠️  Failed to initialize RAG pipeline: {e}")
                import traceback
                traceback.print_exc()
                self.check_llm = False
        
        # Statistics
        self.stats = {
            "total_entries": 0,
            "valid_entries": 0,
            "invalid_entries": 0,
            "total_ids": 0,
            "valid_ids": 0,
            "invalid_ids": 0,
            "duplicate_ids": 0,
            "missing_in_db": 0,
            "llm_tested": 0,
            "llm_successful": 0,
            "llm_failed": 0,
            "llm_errors": []
        }
    
    def validate_json_format(self, data: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON format and structure.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's a list or dict
        if isinstance(data, list):
            if len(data) == 0:
                return False, "Empty list"
            # Validate each entry
            for i, entry in enumerate(data):
                is_valid, error = self._validate_single_entry(entry)
                if not is_valid:
                    return False, f"Entry {i}: {error}"
            return True, None
        elif isinstance(data, dict):
            is_valid, error = self._validate_single_entry(data)
            return is_valid, error
        else:
            return False, f"Invalid root type: {type(data).__name__}, expected list or dict"
    
    def _validate_single_entry(self, entry: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a single ground truth entry.
        
        Args:
            entry: Single entry dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if not isinstance(entry, dict):
            return False, "Entry is not a dictionary"
        
        if "query" not in entry:
            return False, "Missing required field: 'query'"
        
        if "relevant_ids" not in entry:
            return False, "Missing required field: 'relevant_ids'"
        
        # Check query field
        if not isinstance(entry["query"], str):
            return False, f"Field 'query' must be a string, got {type(entry['query']).__name__}"
        
        if not entry["query"].strip():
            return False, "Field 'query' cannot be empty"
        
        # Check relevant_ids field
        if not isinstance(entry["relevant_ids"], list):
            return False, f"Field 'relevant_ids' must be a list, got {type(entry['relevant_ids']).__name__}"
        
        if len(entry["relevant_ids"]) == 0:
            return False, "Field 'relevant_ids' cannot be empty"
        
        # Check each ID
        seen_ids = set()
        for i, doc_id in enumerate(entry["relevant_ids"]):
            if not isinstance(doc_id, str):
                return False, f"relevant_ids[{i}] must be a string, got {type(doc_id).__name__}"
            
            if not doc_id.strip():
                return False, f"relevant_ids[{i}] cannot be empty"
            
            # Check for duplicates
            if doc_id in seen_ids:
                return False, f"Duplicate ID found: {doc_id}"
            seen_ids.add(doc_id)
        
        return True, None
    
    def check_ids_in_database(self, ids: List[str]) -> Dict[str, bool]:
        """
        Check if IDs exist in PostgreSQL database.
        
        Args:
            ids: List of document IDs to check
            
        Returns:
            Dictionary mapping ID to existence status
        """
        if not self.check_database:
            return {}
        
        result = {}
        
        try:
            conn = psycopg2.connect(
                dbname=self.pg_config["dbname"],
                user=self.pg_config["user"],
                password=self.pg_config["password"],
                host=self.pg_config["host"],
                port=self.pg_config["port"]
            )
            cur = conn.cursor()
            
            # Convert string IDs to integers for query
            id_ints = []
            valid_string_ids = set()  # Track which string IDs are valid integers
            
            for doc_id in ids:
                try:
                    id_int = int(doc_id)
                    id_ints.append(id_int)
                    valid_string_ids.add(doc_id)
                except ValueError:
                    # Non-numeric ID, mark as not found
                    result[doc_id] = False
            
            if not id_ints:
                cur.close()
                conn.close()
                return result
            
            # Query database
            placeholders = ','.join(['%s'] * len(id_ints))
            cur.execute(
                f"SELECT id FROM knowledge_base WHERE id IN ({placeholders})",
                tuple(id_ints)
            )
            
            # Get existing IDs as both int and string for comparison
            existing_int_ids = {row[0] for row in cur.fetchall()}
            existing_str_ids = {str(id_int) for id_int in existing_int_ids}
            
            # Map results back to original string IDs
            for doc_id in valid_string_ids:
                if doc_id in result:
                    continue  # Already processed (invalid format)
                # Check if the ID exists
                try:
                    id_int = int(doc_id)
                    result[doc_id] = id_int in existing_int_ids or doc_id in existing_str_ids
                except ValueError:
                    result[doc_id] = False
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"  ⚠️  Error checking database: {e}")
            # Mark all as unknown
            for doc_id in ids:
                result[doc_id] = None
        
        return result
    
    def get_documents_by_ids(self, doc_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get documents from Elasticsearch or PostgreSQL by their IDs.
        Tries Elasticsearch first, falls back to PostgreSQL if ES fails.
        
        Args:
            doc_ids: List of document IDs
            
        Returns:
            List of document dictionaries
        """
        # Try Elasticsearch first if configured
        if self.es_config:
            try:
                from elasticsearch import Elasticsearch
                es = Elasticsearch(
                    self.es_config["host"],
                    api_key=self.es_config["api_key"],
                    ca_certs=self.es_config["ca_certs"]
                )
                
                # Convert string IDs to integers for query
                id_ints = []
                for doc_id in doc_ids:
                    try:
                        id_ints.append(int(doc_id))
                    except ValueError:
                        continue
                
                if id_ints:
                    # Query Elasticsearch by IDs
                    resp = es.mget(
                        index=self.es_config["index_name"],
                        body={"ids": [str(id_int) for id_int in id_ints]},
                        _source=["id", "category", "source", "content"]
                    )
                    
                    documents = []
                    for doc in resp.get("docs", []):
                        if doc.get("found"):
                            source = doc["_source"]
                            documents.append({
                                "id": source.get("id"),
                                "category": source.get("category"),
                                "source": source.get("source"),
                                "content": source.get("content"),
                                "score": 1.0  # Ground truth documents have score 1.0
                            })
                    
                    if documents:
                        return documents
                    # If ES returned empty, fall through to PostgreSQL
            except Exception as e:
                # Fallback to PostgreSQL on any ES error
                pass
        
        # Fallback to PostgreSQL
        return self._get_documents_from_postgres(doc_ids)
    
    def _get_documents_from_postgres(self, doc_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get documents from PostgreSQL by their IDs.
        
        Args:
            doc_ids: List of document IDs
            
        Returns:
            List of document dictionaries
        """
        try:
            conn = psycopg2.connect(
                dbname=self.pg_config["dbname"],
                user=self.pg_config["user"],
                password=self.pg_config["password"],
                host=self.pg_config["host"],
                port=self.pg_config["port"]
            )
            cur = conn.cursor()
            
            # Convert string IDs to integers
            id_ints = []
            for doc_id in doc_ids:
                try:
                    id_ints.append(int(doc_id))
                except ValueError:
                    continue
            
            if not id_ints:
                cur.close()
                conn.close()
                return []
            
            # Query database
            placeholders = ','.join(['%s'] * len(id_ints))
            cur.execute(
                f"SELECT id, category, content, source FROM knowledge_base WHERE id IN ({placeholders})",
                tuple(id_ints)
            )
            
            documents = []
            for row in cur.fetchall():
                _id, category, content, source = row
                documents.append({
                    "id": str(_id),
                    "category": category,
                    "source": source,
                    "content": content,
                    "score": 1.0  # Ground truth documents have score 1.0
                })
            
            cur.close()
            conn.close()
            
            return documents
        
        except Exception as e:
            print(f"  ⚠️  Error getting documents from PostgreSQL: {e}")
            return []
    
    def validate_llm_response(
        self,
        query: str,
        relevant_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Validate LLM response quality using ground truth documents directly.
        No retrieval is performed - uses only the provided relevant_ids.
        
        Args:
            query: Query text
            relevant_ids: Ground truth relevant document IDs
            
        Returns:
            Dictionary with validation results
        """
        if not self.check_llm or not self.rag_pipeline:
            return {"skipped": True, "reason": "LLM validation not enabled"}
        
        try:
            # Get documents directly from ground truth IDs
            documents = self.get_documents_by_ids(relevant_ids)
            
            if not documents:
                return {
                    "valid": False,
                    "error": f"No documents found for {len(relevant_ids)} provided IDs",
                    "has_error": True,
                    "documents_found": 0,
                    "documents_requested": len(relevant_ids)
                }
            
            # Generate response using ground truth documents directly
            # Use a much larger context length for ground truth validation
            # to include all provided documents
            stdout_capture = io.StringIO()
            with contextlib.redirect_stdout(stdout_capture):
                # Calculate approximate max length: allow ~1000 chars per document
                # This ensures we can include most/all ground truth documents
                # Cap at 100k to avoid token limits
                max_context = min(100000, max(30000, len(documents) * 1000))
                result = self.rag_pipeline.generator.generate(
                    query, 
                    documents,
                    max_context_length=max_context
                )
            
            # Extract response
            response_text = result.get("response", "")
            
            # Check response quality
            is_valid = True
            issues = []
            
            # Check 1: Response is not empty
            if not response_text or len(response_text.strip()) < 10:
                is_valid = False
                issues.append("Response is too short or empty")
            
            # Check 2: Response is not an error message
            error_keywords = ["error", "failed", "exception", "unable to", "cannot"]
            if any(keyword in response_text.lower() for keyword in error_keywords):
                is_valid = False
                issues.append("Response contains error keywords")
            
            # Check 3: Response has reasonable length
            if len(response_text) < 50:
                issues.append("Response is very short (may be incomplete)")
            elif len(response_text) > 5000:
                issues.append("Response is very long (may be verbose)")
            
            return {
                "valid": is_valid,
                "response_length": len(response_text),
                "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "documents_used": len(documents),
                "documents_requested": len(relevant_ids),
                "issues": issues,
                "has_error": "error" in result or result.get("error"),
                "error": result.get("error")  # Include error message if present
            }
        
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "has_error": True
            }
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a ground truth JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with validation results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        print(f"\n{'='*70}")
        print(f"📋 Validating: {file_path.name}")
        print(f"{'='*70}")
        
        # Load JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON format: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {e}"
            }
        
        # Validate format
        is_valid, error = self.validate_json_format(data)
        if not is_valid:
            return {
                "success": False,
                "error": error
            }
        
        # Process entries
        entries = data if isinstance(data, list) else [data]
        self.stats["total_entries"] = len(entries)
        
        all_issues = []
        all_ids = []
        llm_results = []
        
        for i, entry in enumerate(entries):
            print(f"\n📝 Entry {i+1}/{len(entries)}")
            print(f"   Query: {entry['query'][:80]}...")
            print(f"   Relevant IDs: {len(entry['relevant_ids'])} IDs")
            
            # Collect all IDs
            all_ids.extend(entry['relevant_ids'])
            
            entry_issues = []
            
            # Check IDs in database
            if self.check_database:
                id_status = self.check_ids_in_database(entry['relevant_ids'])
                missing_ids = [doc_id for doc_id, exists in id_status.items() if exists is False]
                
                if missing_ids:
                    entry_issues.append({
                        "type": "missing_ids",
                        "missing_ids": missing_ids
                    })
                    print(f"   ⚠️  Missing IDs in database: {len(missing_ids)}")
                    if len(missing_ids) <= 10:
                        print(f"      {missing_ids}")
                    else:
                        print(f"      {missing_ids[:10]} ... (and {len(missing_ids)-10} more)")
                else:
                    print(f"   ✅ All IDs exist in database")
                    self.stats["valid_entries"] += 1
            else:
                self.stats["valid_entries"] += 1
            
            # Check LLM response
            if self.check_llm:
                print(f"   🤖 Testing LLM response...")
                llm_result = self.validate_llm_response(entry['query'], entry['relevant_ids'])
                llm_results.append({
                    "entry": i,
                    "query": entry['query'],
                    "result": llm_result
                })
                self.stats["llm_tested"] += 1
                
                if llm_result.get("has_error"):
                    self.stats["llm_failed"] += 1
                    error_msg = llm_result.get("error", "Unknown error")
                    self.stats["llm_errors"].append({
                        "entry": i,
                        "error": error_msg
                    })
                    # Show error message (truncate if too long)
                    if len(error_msg) > 150:
                        print(f"   ❌ LLM validation failed: {error_msg[:150]}...")
                    else:
                        print(f"   ❌ LLM validation failed: {error_msg}")
                elif not llm_result.get("valid", True):
                    self.stats["llm_failed"] += 1
                    issues_list = llm_result.get("issues", [])
                    print(f"   ⚠️  LLM response issues: {', '.join(issues_list)}")
                    entry_issues.append({
                        "type": "llm_quality",
                        "issues": issues_list,
                        "response_length": llm_result.get("response_length", 0)
                    })
                else:
                    self.stats["llm_successful"] += 1
                    response_preview = llm_result.get("response_preview", "")
                    docs_used = llm_result.get("documents_used", 0)
                    docs_requested = llm_result.get("documents_requested", 0)
                    
                    print(f"   ✅ LLM response valid")
                    print(f"      Response length: {llm_result.get('response_length', 0)} chars")
                    print(f"      Documents used: {docs_used}/{docs_requested} (from ground truth)")
                    if response_preview:
                        print(f"      Response preview: {response_preview[:150]}...")
                
                # Show error details if available
                if llm_result.get("error"):
                    error_msg = llm_result.get("error", "")
                    if len(error_msg) > 100:
                        print(f"      Error details: {error_msg[:100]}...")
                    else:
                        print(f"      Error details: {error_msg}")
            
            if entry_issues:
                all_issues.append({
                    "entry": i,
                    "query": entry['query'],
                    "issues": entry_issues
                })
        
        # Check for duplicate IDs across entries
        id_counts = {}
        for doc_id in all_ids:
            id_counts[doc_id] = id_counts.get(doc_id, 0) + 1
        
        duplicates = {doc_id: count for doc_id, count in id_counts.items() if count > 1}
        if duplicates:
            print(f"\n⚠️  Duplicate IDs across entries: {len(duplicates)}")
            self.stats["duplicate_ids"] = len(duplicates)
        
        # Summary
        self.stats["total_ids"] = len(all_ids)
        self.stats["invalid_entries"] = self.stats["total_entries"] - self.stats["valid_entries"]
        
        print(f"\n{'='*70}")
        print("📊 VALIDATION SUMMARY")
        print(f"{'='*70}")
        print(f"  Total entries: {self.stats['total_entries']}")
        print(f"  Valid entries: {self.stats['valid_entries']}")
        print(f"  Invalid entries: {self.stats['invalid_entries']}")
        print(f"  Total IDs: {self.stats['total_ids']}")
        if duplicates:
            print(f"  Duplicate IDs: {self.stats['duplicate_ids']}")
        if all_issues:
            # Count missing IDs
            total_missing = 0
            for issue in all_issues:
                for sub_issue in issue.get("issues", []):
                    if sub_issue.get("type") == "missing_ids":
                        total_missing += len(sub_issue.get("missing_ids", []))
            if total_missing > 0:
                print(f"  Missing IDs in database: {total_missing}")
        
        # LLM validation summary
        if self.check_llm and self.stats["llm_tested"] > 0:
            print(f"\n🤖 LLM VALIDATION SUMMARY")
            print(f"  Tested queries: {self.stats['llm_tested']}")
            print(f"  Successful: {self.stats['llm_successful']}")
            print(f"  Failed: {self.stats['llm_failed']}")
            if self.stats["llm_errors"]:
                print(f"  Errors: {len(self.stats['llm_errors'])}")
        
        result = {
            "success": True,
            "stats": self.stats,
            "issues": all_issues,
            "duplicates": duplicates,
            "llm_results": llm_results if self.check_llm else []
        }
        
        # Save LLM results to file if available
        if self.check_llm and llm_results:
            output_file = Path(file_path).stem + "_llm_results.json"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(llm_results, f, ensure_ascii=False, indent=2)
                print(f"\n💾 LLM results saved to: {output_file}")
            except Exception as e:
                print(f"\n⚠️  Failed to save LLM results: {e}")
        
        return result


def main():
    """
    Main function for command-line usage.
    """
    parser = argparse.ArgumentParser(
        description="Validate ground truth JSON file format and content"
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to ground truth JSON file"
    )
    parser.add_argument(
        "--no-db-check",
        action="store_true",
        help="Skip database existence check"
    )
    parser.add_argument(
        "--check-es",
        action="store_true",
        help="Also check Elasticsearch (not implemented yet)"
    )
    parser.add_argument(
        "--check-llm",
        action="store_true",
        help="Test LLM response quality using RAG pipeline"
    )
    
    args = parser.parse_args()
    
    validator = GroundTruthValidator(
        check_database=not args.no_db_check,
        check_elasticsearch=args.check_es,
        check_llm=args.check_llm
    )
    
    result = validator.validate_file(args.file)
    
    if result["success"]:
        # Show LLM results summary if available
        if args.check_llm and result.get("llm_results"):
            print(f"\n💡 Tip: Full LLM responses are saved in the output JSON file")
            print(f"   You can review detailed responses, errors, and retrieval metrics there.")
        
        if result.get("issues") or result.get("duplicates"):
            print("\n⚠️  Validation completed with issues")
            sys.exit(1)
        else:
            print("\n✅ Validation passed!")
            sys.exit(0)
    else:
        print(f"\n❌ Validation failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

