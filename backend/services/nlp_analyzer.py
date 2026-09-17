import re
from collections import Counter


def clean_text(text: str) -> str:
    """
    Basic NLP text cleaning.
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def analyze_text(text: str) -> dict:
    """
    Perform basic NLP analysis on extracted document text.
    """

    if not text or not text.strip():
        return {
            "character_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "unique_word_count": 0,
            "top_words": []
        }

    cleaned_text = clean_text(text)

    words = cleaned_text.split()

    sentences = [
        sentence.strip()
        for sentence in re.split(r"[.!?]+", text)
        if sentence.strip()
    ]

    word_frequency = Counter(words)

    return {
        "character_count": len(text),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "unique_word_count": len(set(words)),
        "top_words": [
            {
                "word": word,
                "count": count
            }
            for word, count in word_frequency.most_common(10)
        ]
    }