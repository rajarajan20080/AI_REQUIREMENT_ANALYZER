"""
duplicate.py
============

Detects duplicate and near-duplicate requirement statements using semantic
sentence embeddings produced by a Sentence-Transformers model.
"""

from typing import List, TypedDict, Dict, Any, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except Exception:
    SentenceTransformer = None
    HAS_SENTENCE_TRANSFORMERS = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity
except Exception:
    TfidfVectorizer = None
    sk_cosine_similarity = None


class DuplicatePair(TypedDict):
    """Type definition for a single duplicate pair result."""
    index_a: int
    index_b: int
    req_id_a: str
    req_id_b: str
    requirement_a: str
    requirement_b: str
    similarity_score: float
    similarity_percentage: float
    status: str  # "High Duplicate Risk", "Potential Semantic Overlap"


class DuplicateDetector:
    """
    Wraps a Sentence-Transformers model with high-speed TF-IDF fallback
    for zero-dependency / Vercel serverless execution.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.80,
    ) -> None:
        self._similarity_threshold = similarity_threshold
        self._model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self._model = SentenceTransformer(model_name)
            except Exception:
                self._model = None

    @staticmethod
    def _cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
        """
        Compute a pairwise cosine similarity matrix for a set of embeddings.
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        normalized = embeddings / norms
        return np.dot(normalized, normalized.T)

    def find_duplicates(
        self,
        requirements: List[str],
        threshold: Optional[float] = None
    ) -> List[DuplicatePair]:
        """
        Identify pairs of requirements whose semantic similarity exceeds the
        configured threshold using vectorized cosine indexing.

        Args:
            requirements: A list of raw requirement texts.
            threshold: Optional custom threshold to override default.

        Returns:
            A list of DuplicatePair dictionaries describing each detected
            duplicate pair, sorted by descending similarity score.
        """
        if len(requirements) < 2:
            return []

        use_threshold = threshold if threshold is not None else self._similarity_threshold

        # Extract text if list of dictionaries was passed
        string_reqs = [
            (r.get("requirement_text") or r.get("text") or str(r)) if isinstance(r, dict) else str(r)
            for r in requirements
        ]

        # Fast sentence encoding or TF-IDF fallback
        if self._model is not None:
            embeddings = self._model.encode(string_reqs, show_progress_bar=False, batch_size=64)
            embeddings = np.asarray(embeddings)
            similarity_matrix = self._cosine_similarity_matrix(embeddings)
        elif TfidfVectorizer is not None:
            vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            tfidf_mat = vec.fit_transform(string_reqs)
            similarity_matrix = (tfidf_mat * tfidf_mat.T).toarray()
        else:
            similarity_matrix = np.zeros((len(string_reqs), len(string_reqs)))

        # Vectorized upper triangle extraction
        upper_tri = np.triu(similarity_matrix, k=1)
        matches = np.argwhere(upper_tri >= use_threshold)

        duplicates: List[DuplicatePair] = []
        for i, j in matches:
            score = float(upper_tri[i, j])
            status = "High Duplicate Risk" if score >= 0.90 else "Potential Semantic Overlap"
            duplicates.append({
                "index_a": int(i),
                "index_b": int(j),
                "req_id_a": f"REQ-{i+1:03d}",
                "req_id_b": f"REQ-{j+1:03d}",
                "requirement_a": requirements[i],
                "requirement_b": requirements[j],
                "similarity_score": round(score, 3),
                "similarity_percentage": round(score * 100, 1),
                "status": status
            })

        duplicates.sort(key=lambda pair: pair["similarity_score"], reverse=True)
        return duplicates
