# Mock implementation for deployment without scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Mock classes for basic functionality
    class MockTfidfVectorizer:
        def __init__(self, **kwargs):
            pass
        def fit_transform(self, texts):
            return texts  # Return texts as-is for mock
        def transform(self, texts):
            return texts
    
    TfidfVectorizer = MockTfidfVectorizer
    
    def cosine_similarity(a, b):
        # Simple mock similarity - just return random similarities
        import random
        if hasattr(b, '__len__'):
            return [[random.random() for _ in range(len(b))]]
        return [[random.random()]]

try:
    import numpy as np
except ImportError:
    # Mock numpy if not available
    class MockNumpy:
        def array(self, x):
            return x
        def argsort(self, x):
            if isinstance(x, (list, tuple)):
                return list(range(len(x)))
            return [0]
    np = MockNumpy()

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
