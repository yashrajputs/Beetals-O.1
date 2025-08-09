# Vector search with database integration using ChromaDB
from typing import List, Dict, Optional
from .database_manager import DatabaseManager

def create_vector_index_with_db(structured_clauses: List[Dict], db_manager: DatabaseManager, 
                               document_id: int) -> str:
    """
    Create and store vector index in ChromaDB.
    Returns collection name.
    """
    collection_name = db_manager.store_vector_index(
        document_id=document_id,
        structured_clauses=structured_clauses,
        model_name="chromadb_default"
    )
    return collection_name

def get_top_similar_clauses_from_db(query: str, db_manager: DatabaseManager, 
                                   document_id: int, k: int = 5) -> List[Dict]:
    """
    Find similar clauses using ChromaDB vector search or fallback.
    """
    try:
        return db_manager.search_similar_clauses(
            document_id=document_id,
            query=query,
            k=k
        )
    except Exception:
        # Fallback to simple text search when ChromaDB is not available
        clauses = db_manager.get_clauses_by_document_id(document_id)
        return get_top_similar_clauses(
            query=query,
            indexed_data=clauses,
            index={}, 
            model=None,
            k=k
        )

# Backward compatibility functions for existing code
def create_vector_index(structured_clauses: List[Dict]):
    """
    Legacy function - returns empty index for backward compatibility.
    New code should use create_vector_index_with_db instead.
    """
    return {'type': 'chromadb', 'clauses': structured_clauses}, None

def get_top_similar_clauses(query: str, indexed_data: List[Dict], index: Dict, 
                          model, k: int = 5) -> List[Dict]:
    """
    Legacy function - returns simple text matching for backward compatibility.
    New code should use get_top_similar_clauses_from_db instead.
    """
    # Simple text-based matching as fallback
    query_lower = query.lower()
    results = []
    
    for clause in indexed_data:
        text_lower = clause.get('text', '').lower()
        title_lower = clause.get('title', '').lower()
        
        # Simple word matching score
        score = 0
        for word in query_lower.split():
            if word in text_lower:
                score += 1
            if word in title_lower:
                score += 2  # Title matches are weighted higher
        
        if score > 0:
            clause_copy = clause.copy()
            clause_copy['similarity_score'] = score / len(query_lower.split())
            results.append(clause_copy)
    
    # Sort by score and return top k
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    return results[:k]
