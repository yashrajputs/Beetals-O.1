try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    raise ImportError("scikit-learn is required. Install it with: pip install scikit-learn")
import numpy as np

def create_vector_index(structured_clauses: list[dict]):
    """
    Create a TF-IDF vector index from structured clauses.
    Returns the vectorizer and the matrix for similarity search.
    """
    # Initialize the TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2),
        lowercase=True
    )
    
    # Prepare text for vectorization
    text_to_embed = [f"{clause['title']} {clause['text']}" for clause in structured_clauses]
    
    # Generate TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(text_to_embed)
    
    return {'vectorizer': vectorizer, 'matrix': tfidf_matrix}, vectorizer

def get_top_similar_clauses(query: str, indexed_data: list[dict], index: dict, 
                          model, k: int = 5) -> list[dict]:
    """
    Finds and returns the top k most similar clauses using TF-IDF and cosine similarity.
    """
    vectorizer = index['vectorizer']
    tfidf_matrix = index['matrix']
    
    # Transform the query using the same vectorizer
    query_vector = vectorizer.transform([query])
    
    # Calculate cosine similarity
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Get top k most similar indices
    top_indices = similarities.argsort()[-k:][::-1]
    
    # Return the most similar clauses
    results = [indexed_data[i] for i in top_indices if i < len(indexed_data)]
    
    return results
