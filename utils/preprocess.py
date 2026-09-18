"""
preprocess.py
=============

spaCy based NLP preprocessing utilities used to clean and normalize
requirement text prior to classification and similarity computation.
"""

from typing import List

import spacy
from spacy.language import Language


import re

# Fallback English stop words for serverless/lightweight environments
FALLBACK_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

class SpaCyModelNotFoundError(Exception):
    """Raised when the required spaCy language model is not installed."""


def load_spacy_model(model_name: str = "en_core_web_sm"):
    """
    Load the spaCy English language model with fallback.
    """
    try:
        import spacy
        return spacy.load(model_name)
    except Exception:
        return None


class TextPreprocessor:
    """
    Wraps spaCy pipeline with high-speed regex fallback for zero-dependency / Vercel execution.
    """

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        self._nlp = load_spacy_model(model_name)

    def clean_text(self, text: str) -> str:
        """
        Lowercase, lemmatize, and remove stop words and punctuation from
        the given text.

        Args:
            text: Raw input text.

        Returns:
            A cleaned, space-joined string of lemmatized tokens.
        """
        if not text or not text.strip():
            return ""

        if self._nlp is not None:
            try:
                document = self._nlp(text)
                tokens = [
                    token.lemma_.lower().strip()
                    for token in document
                    if not token.is_stop
                    and not token.is_punct
                    and not token.is_space
                    and token.lemma_.strip() != ""
                ]
                return " ".join(tokens)
            except Exception:
                pass

        # High-speed fallback: regex tokenization & stopword removal
        words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
        tokens = [w for w in words if w not in FALLBACK_STOP_WORDS]
        return " ".join(tokens)

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into a list of lowercase word tokens.
        """
        if not text or not text.strip():
            return []

        if self._nlp is not None:
            try:
                document = self._nlp(text)
                return [
                    token.text.lower()
                    for token in document
                    if not token.is_punct and not token.is_space
                ]
            except Exception:
                pass

        return re.findall(r"\b\w+\b", text.lower())

    def sentence_count(self, text: str) -> int:
        """
        Count the number of sentences detected in the given text.
        """
        if not text or not text.strip():
            return 0
        if self._nlp is not None:
            try:
                document = self._nlp(text)
                return len(list(document.sents))
            except Exception:
                pass
        sents = re.split(r"[.!?]+", text.strip())
        return len([s for s in sents if s.strip()])

    def word_count(self, text: str) -> int:
        """
        Count the number of alphabetic words in the given text.
        """
        if not text or not text.strip():
            return 0
        if self._nlp is not None:
            try:
                document = self._nlp(text)
                return len([token for token in document if token.is_alpha])
            except Exception:
                pass
        return len(re.findall(r"\b[a-zA-Z]+\b", text))

    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Apply `clean_text` to a batch of texts.

        Args:
            texts: A list of raw input strings.

        Returns:
            A list of cleaned strings, in the same order.
        """
        return [self.clean_text(text) for text in texts]
