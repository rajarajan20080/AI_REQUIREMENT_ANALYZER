"""
train_model.py
===============

Universal Machine Learning training pipeline for AI-Based Software Requirement Analyzer.
Loads, normalizes, and trains TF-IDF + Logistic Regression classification models on ANY
requirement dataset format (.csv, .xlsx, .xls, .json, .jsonl, .arff, .txt).

Supports single datasets or multi-dataset fusion, automatic schema detection, robust NLP
preprocessing, stratified cross-validation evaluation, and model metadata persistence.
"""

import argparse
import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from utils.preprocess import TextPreprocessor, SpaCyModelNotFoundError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
CLASSIFIER_PATH = os.path.join(MODELS_DIR, "classifier.pkl")
VECTORIZER_PATH = os.path.join(MODELS_DIR, "vectorizer.pkl")
METADATA_PATH = os.path.join(MODELS_DIR, "model_metadata.json")

# Common text and label column names in requirement datasets
TEXT_COLUMN_CANDIDATES = [
    "requirement_text", "requirement", "RequirementText", "text", "content",
    "statement", "sentence", "Description", "description", "req_text", "req",
    "Requirements", "Requirement_Text", "Specification", "specification"
]

LABEL_COLUMN_CANDIDATES = [
    "label", "requirement_type", "Class", "class", "Type", "type", "category",
    "Category", "target", "RequirementType", "Requirement_Type", "Tag", "tag"
]

# Standardize non-functional codes from PROMISE and other requirement benchmarks
FUNCTIONAL_LABELS = {"functional", "f", "fr", "1", 1, "true", "yes", "functional requirement"}
NON_FUNCTIONAL_LABELS = {
    "non-functional", "nonfunctional", "non_functional", "nf", "nfr", "0", 0, "false", "no",
    "us", "o", "pe", "se", "lf", "uh", "mn", "sc", "l", "a", "ft", "po", "cr", "q",
    "security", "performance", "usability", "reliability", "maintainability", "availability",
    "scalability", "portability", "fault tolerance", "compliance", "non-functional requirement"
}


def normalize_label(raw_val: Union[str, int, float]) -> Optional[str]:
    """
    Intelligently map various label encodings and PROMISE category codes
    to either 'Functional' or 'Non-Functional'.
    """
    if pd.isna(raw_val):
        return None
    val_str = str(raw_val).strip().lower()
    if val_str in FUNCTIONAL_LABELS:
        return "Functional"
    if val_str in NON_FUNCTIONAL_LABELS or any(val_str.startswith(x) for x in ["non", "nfr", "nf"]):
        return "Non-Functional"
    return "Non-Functional"


def detect_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Automatically identify the requirement text column and label column in a DataFrame.
    """
    text_col = None
    label_col = None

    # Find text column
    for col in df.columns:
        if col in TEXT_COLUMN_CANDIDATES or col.lower() in [c.lower() for c in TEXT_COLUMN_CANDIDATES]:
            text_col = col
            break

    # If not found by candidate list, find first string/object column with average word count > 3
    if not text_col:
        for col in df.columns:
            if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
                sample_lens = df[col].dropna().astype(str).str.split().apply(len)
                if len(sample_lens) > 0 and sample_lens.mean() >= 3:
                    text_col = col
                    break

    # Find label column
    for col in df.columns:
        if col == text_col:
            continue
        if col in LABEL_COLUMN_CANDIDATES or col.lower() in [c.lower() for c in LABEL_COLUMN_CANDIDATES]:
            label_col = col
            break

    return text_col, label_col


def load_dataset_file(file_path: str) -> pd.DataFrame:
    """
    Load requirement data from any supported format: CSV, Excel (.xlsx, .xls),
    JSON, JSONL, ARFF, or plain TXT.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Dataset file not found: '{file_path}'")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif ext == ".jsonl":
        records = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        df = pd.DataFrame(records)
    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try finding a list key or convert dict
                list_key = next((k for k, v in data.items() if isinstance(v, list)), None)
                if list_key:
                    df = pd.DataFrame(data[list_key])
                else:
                    df = pd.DataFrame([data])
            else:
                df = pd.DataFrame()
    elif ext in [".txt", ".md"]:
        lines = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                cleaned = line.strip()
                if len(cleaned.split()) >= 3:
                    lines.append({"requirement_text": cleaned, "label": "Functional"})
        df = pd.DataFrame(lines)
    else:
        raise ValueError(f"Unsupported dataset format: {ext}")

    text_col, label_col = detect_columns(df)
    if not text_col:
        raise ValueError(f"Could not automatically detect requirement text column in '{file_path}'. Columns found: {list(df.columns)}")

    result_df = pd.DataFrame()
    result_df["requirement_text"] = df[text_col].astype(str).str.strip()

    if label_col:
        result_df["label"] = df[label_col].apply(normalize_label)
    else:
        # If no label column, mark default as Functional
        result_df["label"] = "Functional"

    # Filter out empty or whitespace-only rows
    result_df = result_df.dropna(subset=["requirement_text", "label"])
    result_df = result_df[result_df["requirement_text"].str.len() > 5]
    return result_df


def discover_and_fuse_datasets(custom_paths: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Search and merge multiple requirement datasets into a unified training set.
    """
    candidate_paths = custom_paths or [
        os.path.join(BASE_DIR, "srs_requirements_3000.csv"),
        os.path.join(BASE_DIR, "srs_requirements_3000.jsonl"),
        os.path.join(BASE_DIR, "srs_requirements_3000.xlsx"),
        os.path.join(BASE_DIR, "data", "training_1000.csv"),
        os.path.join(BASE_DIR, "data", "training_expanded.csv"),
        os.path.join(BASE_DIR, "data", "dataset", "PROMISE_exp.csv"),
        os.path.join(BASE_DIR, "data", "dataset", "Promise_NFR_dataset.csv"),
        os.path.join(BASE_DIR, "data", "training.csv"),
        "srs_requirements_3000.csv",
        "srs_requirements_3000.jsonl",
        "srs_requirements_3000.xlsx",
        os.path.join("data", "training_1000.csv"),
        os.path.join("data", "training_expanded.csv"),
        os.path.join("data", "dataset", "PROMISE_exp.csv"),
        os.path.join("data", "dataset", "Promise_NFR_dataset.csv"),
        os.path.join("data", "training.csv")
    ]

    loaded_dfs = []
    seen_sources = set()

    for path in candidate_paths:
        if not path or not os.path.isfile(path) or path in seen_sources:
            continue
        try:
            df = load_dataset_file(path)
            if not df.empty:
                print(f"      + Loaded {len(df)} examples from '{path}'")
                loaded_dfs.append(df)
                seen_sources.add(path)
                # If we loaded the 3,000 dataset in one format, skip redundant formats of the same dataset
                if "srs_requirements_3000" in path:
                    for sibling in ["srs_requirements_3000.csv", "srs_requirements_3000.jsonl", "srs_requirements_3000.xlsx"]:
                        seen_sources.add(sibling)
        except Exception as exc:
            print(f"      [Warning] Could not load '{path}': {exc}")

    if not loaded_dfs:
        raise ValueError("No valid requirement datasets could be loaded.")

    combined = pd.concat(loaded_dfs, ignore_index=True)
    # Deduplicate based on exact text
    combined = combined.drop_duplicates(subset=["requirement_text"]).reset_index(drop=True)
    return combined


def preprocess_dataset(dataframe: pd.DataFrame, preprocessor: TextPreprocessor) -> pd.DataFrame:
    """
    Apply NLP lemmatization and text cleaning across all requirements in the dataset.
    """
    dataframe = dataframe.copy()
    dataframe["cleaned_text"] = dataframe["requirement_text"].apply(preprocessor.clean_text)
    dataframe = dataframe[dataframe["cleaned_text"].str.strip() != ""]
    return dataframe.reset_index(drop=True)


def train_classifier(
    dataframe: pd.DataFrame,
) -> Tuple[LogisticRegression, TfidfVectorizer, Dict[str, Any], str]:
    """
    Train a high-accuracy TF-IDF + Logistic Regression classifier with balanced
    weights and calibrated sublinear TF scaling.
    """
    features_text = dataframe["cleaned_text"].tolist()
    labels = dataframe["label"].tolist()

    vectorizer = TfidfVectorizer(
        max_features=8000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
        strip_accents="unicode"
    )
    features = vectorizer.fit_transform(features_text)

    stratify_labels = labels if len(set(labels)) > 1 else None
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=stratify_labels,
    )

    classifier = LogisticRegression(
        max_iter=1500,
        C=2.0,
        class_weight="balanced",
        solver="lbfgs"
    )
    classifier.fit(x_train, y_train)

    predictions = classifier.predict(x_test)
    accuracy = float(accuracy_score(y_test, predictions))
    f1 = float(f1_score(y_test, predictions, average="weighted", zero_division=0))
    precision = float(precision_score(y_test, predictions, average="weighted", zero_division=0))
    recall = float(recall_score(y_test, predictions, average="weighted", zero_division=0))
    report_text = classification_report(y_test, predictions, zero_division=0)

    # Class distribution
    counts = pd.Series(labels).value_counts().to_dict()

    metrics = {
        "accuracy": round(accuracy, 4),
        "accuracy_pct": round(accuracy * 100, 2),
        "f1_score": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "total_examples": len(dataframe),
        "train_examples": int(x_train.shape[0]),
        "test_examples": int(x_test.shape[0]),
        "vocab_size": len(vectorizer.vocabulary_),
        "classes": [str(c) for c in classifier.classes_],
        "distribution": {str(k): int(v) for k, v in counts.items()},
        "trained_at": datetime.datetime.now().isoformat()
    }

    return classifier, vectorizer, metrics, report_text


def save_models(
    classifier: LogisticRegression,
    vectorizer: TfidfVectorizer,
    metrics: Dict[str, Any],
    classifier_path: str = CLASSIFIER_PATH,
    vectorizer_path: str = VECTORIZER_PATH,
    metadata_path: str = METADATA_PATH
) -> None:
    """
    Persist trained classifier, vectorizer, and evaluation metadata.
    """
    os.makedirs(os.path.dirname(classifier_path), exist_ok=True)
    joblib.dump(classifier, classifier_path)
    joblib.dump(vectorizer, vectorizer_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def run_training_pipeline(custom_dataset_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Programmatic entry point for training on any dataset(s).
    """
    print("=" * 65)
    print("AI-Based Software Requirement Analyzer - Universal Model Training")
    print("=" * 65)

    print("\n[1/5] Ingesting & discovering datasets...")
    dataframe = discover_and_fuse_datasets(custom_dataset_paths)
    print(f"      Total unique requirement statements fused: {len(dataframe)}")
    print(f"      Distribution: {dataframe['label'].value_counts().to_dict()}")

    print("\n[2/5] Initializing NLP Text Preprocessor (spaCy)...")
    preprocessor = TextPreprocessor()

    print("[3/5] Cleaning and normalizing requirement texts...")
    dataframe = preprocess_dataset(dataframe, preprocessor)
    print(f"      {len(dataframe)} clean samples ready for training.")

    print("\n[4/5] Training TF-IDF (1-2 ngrams) + Balanced Logistic Regression...")
    classifier, vectorizer, metrics, report_text = train_classifier(dataframe)
    print(f"      [+] Test Accuracy:  {metrics['accuracy_pct']}%")
    print(f"      [+] Weighted F1:    {metrics['f1_score']}")
    print(f"      [+] Precision:      {metrics['precision']}")
    print(f"      [+] Recall:         {metrics['recall']}")
    print(f"      [+] Vocabulary:     {metrics['vocab_size']} n-grams")
    print("\nClassification Report:\n")
    print(report_text)

    print(f"[5/5] Persisting model artifacts to '{MODELS_DIR}/'...")
    save_models(classifier, vectorizer, metrics)
    print(f"      [+] Saved: {CLASSIFIER_PATH}")
    print(f"      [+] Saved: {VECTORIZER_PATH}")
    print(f"      [+] Saved: {METADATA_PATH}")

    print("\nTraining completed successfully! Model is ready for real-time inference.")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train AI Software Requirement Classifier on Any Dataset")
    parser.add_argument("--dataset", "-d", nargs="+", help="Path(s) to dataset file(s) (.csv, .json, .jsonl, .xlsx, .txt)")
    parser.add_argument("--all", action="store_true", help="Auto-discover and fuse all available datasets")
    args = parser.parse_args()

    try:
        paths = args.dataset if args.dataset else None
        run_training_pipeline(paths)
    except SpaCyModelNotFoundError as exc:
        print(f"\n[ERROR] spaCy model missing: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\n[ERROR] Training failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
