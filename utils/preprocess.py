"""
preprocess.py
=============

spaCy based NLP preprocessing utilities used to clean and normalize
requirement text prior to classification and similarity computation.
"""

from typing import List

import spacy
from spacy.language import Language


class SpaCyModelNotFoundError(Exception):
    """Raised when the required spaCy language model is not installed."""


def load_spacy_model(model_name: str = "en_core_web_sm") -> Language:
    """
    Load the spaCy English language model.

    Args:
        model_name: Name of the spaCy model to load.

    Returns:
        A loaded spaCy Language pipeline.

    Raises:
        SpaCyModelNotFoundError: If the model is not installed.
    """
    try:
        return spacy.load(model_name)
    except OSError as exc:
        raise SpaCyModelNotFoundError(
            f"spaCy model '{model_name}' is not installed. "
            f"Run: python -m spacy download {model_name}"
        ) from exc


class TextPreprocessor:
    """
    Wraps a spaCy pipeline to provide reusable text preprocessing
    functionality such as cleaning, tokenization, lemmatization, and
    stop-word removal.
    """

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        """
        Initialize the preprocessor by loading the spaCy model once.

        Args:
            model_name: Name of the spaCy model to load.
        """
        self._nlp: Language = load_spacy_model(model_name)

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

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into a list of lowercase word tokens (punctuation and
        whitespace removed, stop words retained).

        Args:
            text: Raw input text.

        Returns:
            A list of lowercase tokens.
        """
        if not text or not text.strip():
            return []

        document = self._nlp(text)
        return [
            token.text.lower()
            for token in document
            if not token.is_punct and not token.is_space
        ]

    def sentence_count(self, text: str) -> int:
        """
        Count the number of sentences detected in the given text.

        Args:
            text: Raw input text.

        Returns:
            The number of sentences.
        """
        if not text or not text.strip():
            return 0
        document = self._nlp(text)
        return len(list(document.sents))

    def word_count(self, text: str) -> int:
        """
        Count the number of alphabetic words in the given text.

        Args:
            text: Raw input text.

        Returns:
            The number of words.
        """
        if not text or not text.strip():
            return 0
        document = self._nlp(text)
        return len([token for token in document if token.is_alpha])

    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Apply `clean_text` to a batch of texts.

        Args:
            texts: A list of raw input strings.

        Returns:
            A list of cleaned strings, in the same order.
        """
        return [self.clean_text(text) for text in texts]
