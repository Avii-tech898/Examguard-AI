from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(text_a: str, text_b: str) -> float:
    """
    Calculate cosine similarity between two documents
    using TF-IDF vectors.
    """

    if not text_a or not text_a.strip():
        return 0.0

    if not text_b or not text_b.strip():
        return 0.0

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        [text_a, text_b]
    )

    similarity_matrix = cosine_similarity(tfidf_matrix)

    similarity_score = similarity_matrix[0][1]

    return round(float(similarity_score * 100), 3)