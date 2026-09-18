"""
classify.py
===========

Loads the trained TF-IDF vectorizer and Logistic Regression classifier to
predict whether a requirement is Functional or Non-Functional, along with a
confidence score.
"""

import os
from typing import List, Tuple, Optional

import joblib
import numpy as np


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CLASSIFIER_PATH = os.path.join(BASE_DIR, "models", "classifier.pkl")
DEFAULT_VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")


class ModelNotTrainedError(Exception):
    """Raised when the classifier/vectorizer model files are missing."""


class RequirementClassifier:
    """
    Wraps a trained TF-IDF vectorizer and Logistic Regression classifier to
    classify requirement statements as Functional or Non-Functional.
    """

    def __init__(
        self,
        classifier_path: Optional[str] = None,
        vectorizer_path: Optional[str] = None,
    ) -> None:
        """
        Load the trained classifier and vectorizer from disk.

        Args:
            classifier_path: Path to the trained classifier pickle file.
            vectorizer_path: Path to the trained TF-IDF vectorizer pickle file.

        Raises:
            ModelNotTrainedError: If either model file does not exist or
                cannot be loaded.
        """
        clf_path = classifier_path or DEFAULT_CLASSIFIER_PATH
        vec_path = vectorizer_path or DEFAULT_VECTORIZER_PATH

        if not os.path.isfile(clf_path) or not os.path.isfile(vec_path):
            # Also check relative fallback
            rel_clf = os.path.join("models", "classifier.pkl")
            rel_vec = os.path.join("models", "vectorizer.pkl")
            if os.path.isfile(rel_clf) and os.path.isfile(rel_vec):
                clf_path, vec_path = rel_clf, rel_vec
            else:
                raise ModelNotTrainedError(
                    f"Trained model files were not found at '{clf_path}'. "
                    "Please run 'python train_model.py' before analyzing requirements."
                )

        try:
            self._classifier = joblib.load(clf_path)
            self._vectorizer = joblib.load(vec_path)
        except Exception as exc:  # pylint: disable=broad-except
            raise ModelNotTrainedError(
                f"Failed to load trained model files: {exc}"
            ) from exc

    def predict(self, requirement_text: str) -> Tuple[str, float]:
        """
        Predict the category (Functional / Non-Functional) of a single
        requirement statement.

        Args:
            requirement_text: The cleaned requirement text.

        Returns:
            A tuple of (predicted_label, confidence_score) where
            confidence_score is in the range [0.0, 1.0].
        """
        if not requirement_text or not requirement_text.strip():
            return "Unknown", 0.0

        features = self._vectorizer.transform([requirement_text])
        probabilities = self._classifier.predict_proba(features)[0]
        predicted_index = int(np.argmax(probabilities))
        predicted_label = str(self._classifier.classes_[predicted_index])
        confidence = float(probabilities[predicted_index])
        return predicted_label, confidence

    def predict_batch(self, requirement_texts: List[str]) -> List[Tuple[str, float]]:
        """
        Predict categories for a batch of requirement statements.

        Args:
            requirement_texts: A list of cleaned requirement texts.

        Returns:
            A list of (predicted_label, confidence_score) tuples, in the
            same order as the input.
        """
        return [self.predict(text) for text in requirement_texts]
