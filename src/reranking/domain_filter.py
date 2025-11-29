"""Domain-specific filtering and boosting for sports injury domain."""

from typing import List, Dict, Set, Any


class DomainFilter:
    """
    Domain-specific filter for sports injury prevention RAG.
    
    Applies heuristic boosting based on:
    - Sport category matching
    - Query intent classification
    """
    
    # Domain knowledge dictionaries
    SPORTS = ["badminton", "cycling", "running", "soccer", "swimming", "football"]
    
    BODY_PARTS = {
        "knee", "shoulder", "ankle", "hip", "back", "thigh", "calf", "leg",
        "hamstring", "quadriceps", "rotator cuff", "achilles", "shin",
        "elbow", "wrist", "neck", "spine", "groin", "foot", "hand"
    }
    
    QUERY_INTENT_PATTERNS = {
        "definition": ["what is", "define", "definition", "meaning of"],
        "diagnosis": ["recognize", "diagnose", "symptoms", "signs", "identify"],
        "treatment": ["treatment", "rehab", "rehabilitation", "recovery", "therapy", "cure"],
        "prevention": ["prevent", "reduce risk", "avoid", "protection", "warm-up", "warm up"],
        "mechanism": ["causes", "why", "how", "mechanism", "reason", "due to"],
        "exercise": ["exercise", "drill", "strengthen", "stretch", "workout", "training"]
    }
    
    def __init__(self):
        """Initialize domain filter."""
        pass
    
    def detect_sport(self, text: str) -> str:
        """
        Detect sport category from text.
        
        Args:
            text: Query or document text
            
        Returns:
            Sport name or None
        """
        text_lower = text.lower()
        
        # Check sport keywords (including related terms)
        sport_keywords = {
            "badminton": ["badminton", "shuttlecock", "racket"],
            "cycling": ["cycling", "cyclist", "bike", "bicycle"],
            "running": ["running", "runner", "run", "jogging", "jogger"],
            "soccer": ["soccer", "football", "footballer"],
            "swimming": ["swimming", "swimmer", "swim", "stroke"]
        }
        
        for sport, keywords in sport_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return sport
        
        return None
    
    def extract_body_parts(self, text: str) -> Set[str]:
        """
        Extract body part mentions from text.
        
        Args:
            text: Query or document text
            
        Returns:
            Set of body part keywords found
        """
        text_lower = text.lower()
        found = set()
        for part in self.BODY_PARTS:
            if part in text_lower:
                found.add(part)
        return found
    
    def classify_query_intent(self, query: str) -> str:
        """
        Classify query intent/type.
        
        Args:
            query: Query text
            
        Returns:
            Intent type (definition, diagnosis, treatment, etc.)
        """
        query_lower = query.lower()
        
        for intent, patterns in self.QUERY_INTENT_PATTERNS.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return "general"
    
    def boost_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Apply domain-specific score boosting to documents.
        
        Args:
            query: Query text
            documents: List of document dicts with 'score', 'category', etc.
            
        Returns:
            Documents with boosted scores
        """
        if not documents:
            return []
        
        # Analyze query
        query_sport = self.detect_sport(query)
        query_intent = self.classify_query_intent(query)
        
        # Store query analysis in first document for debugging
        if documents:
            documents[0]['query_sport'] = query_sport
            documents[0]['query_intent'] = query_intent
        
        # Apply boosting to each document
        for doc in documents:
            boost = 1.0
            
            # Sport category matching
            if query_sport:
                doc_category = doc.get('category', '').lower()
                if doc_category == query_sport:
                    boost *= 1.25  # Strong boost for same category
                elif doc_category and doc_category != query_sport:
                    boost *= 0.9   # Slight penalty for different category
            
            # Apply boost
            original_score = doc.get('score', 0)
            doc['score'] = original_score * boost
            doc['domain_boost'] = boost
        
        # Re-sort by boosted scores
        documents.sort(key=lambda d: d.get('score', 0), reverse=True)
        
        return documents

