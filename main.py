"""
main.py
=======

Console entry point for the AI-Based Software Requirement Analyzer.
Provides an interactive menu to parse an SRS document (TXT/DOCX/PDF),
run the full NLP analysis pipeline, and generate a professional report.
"""

import os
import sys
from typing import Dict, List

from utils.ambiguity import (
    detect_ambiguous_requirements,
    summarize_ambiguity,
)
from utils.classify import ModelNotTrainedError, RequirementClassifier
from utils.complexity import predict_complexity
from utils.duplicate import DuplicateDetector
from utils.missing import (
    KnowledgeBaseLoadError,
    load_knowledge_base,
    predict_missing_requirements,
)
from utils.parser import (
    DocumentParsingError,
    UnsupportedFileTypeError,
    parse_file,
)
from utils.preprocess import SpaCyModelNotFoundError, TextPreprocessor
from utils.report import generate_report, save_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_TITLE = "AI-BASED SOFTWARE REQUIREMENT ANALYZER"
DEFAULT_REPORT_PATH = os.path.join(BASE_DIR, "report.txt")
DEFAULT_SAMPLE_PATH = os.path.join(BASE_DIR, "data", "sample_srs.txt")


def print_banner() -> None:
    """Print the application banner to the console."""
    width = 78
    print("=" * width)
    print(APP_TITLE.center(width))
    print("=" * width)
    print("Console-based NLP tool for SRS quality analysis".center(width))
    print("=" * width)


def print_menu() -> None:
    """Print the main interactive menu options."""
    print("\nMAIN MENU")
    print("-" * 40)
    print("1. Analyze an SRS document")
    print("2. Exit")


def prompt_file_path() -> str:
    """
    Prompt the user to enter the path of the SRS file to analyze.

    Returns:
        The file path string entered by the user (whitespace-stripped).
    """
    return input(
        "\nEnter the path to the SRS file (.txt, .docx, .pdf)\n"
        "[Press Enter to use data/sample_srs.txt]: "
    ).strip()


def build_classification_results(
    requirements: List[str],
    cleaned_requirements: List[str],
    classifier: RequirementClassifier,
) -> List[Dict]:
    """
    Classify every requirement and build a structured result list.

    Args:
        requirements: The original (raw) requirement statements.
        cleaned_requirements: The NLP-cleaned versions of the requirements,
            in the same order.
        classifier: A loaded RequirementClassifier instance.

    Returns:
        A list of dictionaries each containing 'requirement', 'label', and
        'confidence' keys.
    """
    results: List[Dict] = []
    predictions = classifier.predict_batch(cleaned_requirements)
    for original_text, (label, confidence) in zip(requirements, predictions):
        results.append({
            "requirement": original_text,
            "label": label,
            "confidence": confidence,
        })
    return results


def compute_completeness_score(
    missing_categories_count: int,
    total_categories: int,
    ambiguity_ratio: float,
    duplicate_ratio: float,
) -> float:
    """
    Compute an overall requirement completeness score.

    Args:
        missing_categories_count: Number of knowledge-base categories with
            no coverage in the SRS.
        total_categories: Total number of knowledge-base categories.
        ambiguity_ratio: Ratio (0.0 - 1.0) of ambiguous requirements.
        duplicate_ratio: Ratio (0.0 - 1.0) of requirements involved in a
            duplicate pair.

    Returns:
        A completeness score in the range [0.0, 100.0].
    """
    coverage_ratio = (
        (total_categories - missing_categories_count) / total_categories
        if total_categories > 0
        else 1.0
    )

    penalty = (ambiguity_ratio * 0.3) + (duplicate_ratio * 0.2)
    score = max(0.0, (coverage_ratio - penalty)) * 100
    return round(min(100.0, score), 2)


def compute_overall_confidence(classifications: List[Dict]) -> float:
    """
    Compute the overall average classifier confidence across all
    requirements.

    Args:
        classifications: List of classification result dictionaries with a
            'confidence' key.

    Returns:
        The average confidence expressed as a percentage (0.0 - 100.0).
    """
    if not classifications:
        return 0.0
    total_confidence = sum(item["confidence"] for item in classifications)
    return round((total_confidence / len(classifications)) * 100, 2)


def compute_duplicate_ratio(duplicate_pairs: List[Dict], total_requirements: int) -> float:
    """
    Compute the ratio of requirements involved in at least one duplicate
    pair.

    Args:
        duplicate_pairs: List of DuplicatePair dictionaries.
        total_requirements: Total number of requirements analyzed.

    Returns:
        A duplicate ratio in the range [0.0, 1.0].
    """
    if total_requirements == 0:
        return 0.0

    involved_indices = set()
    for pair in duplicate_pairs:
        involved_indices.add(pair["index_a"])
        involved_indices.add(pair["index_b"])

    return round(len(involved_indices) / total_requirements, 2)


def run_analysis(file_path: str) -> None:
    """
    Execute the full requirement analysis pipeline for a given SRS file and
    display/save the resulting report.

    Args:
        file_path: Path to the SRS document to analyze.
    """
    try:
        print(f"\n[1/8] Parsing SRS document: '{file_path}' ...")
        requirements = parse_file(file_path)
        if not requirements:
            print("[WARNING] No requirement statements were extracted from this document.")
            return
        print(f"       Extracted {len(requirements)} requirement statements.")

        print("\n[2/8] Initializing NLP preprocessing engine ...")
        preprocessor = TextPreprocessor()

        print("[3/8] Cleaning and normalizing requirement text ...")
        cleaned_requirements = preprocessor.preprocess_batch(requirements)

        print("\n[4/8] Loading trained classifier and predicting FR / NFR labels ...")
        classifier = RequirementClassifier()
        classifications = build_classification_results(
            requirements, cleaned_requirements, classifier
        )

        print("[5/8] Detecting ambiguous requirements ...")
        ambiguity_results = detect_ambiguous_requirements(requirements)
        ambiguity_summary = summarize_ambiguity(ambiguity_results)

        print("[6/8] Detecting duplicate requirements using sentence embeddings ...")
        duplicate_detector = DuplicateDetector()
        duplicate_pairs = duplicate_detector.find_duplicates(requirements)
        duplicate_ratio = compute_duplicate_ratio(duplicate_pairs, len(requirements))

        print("[7/8] Predicting missing requirements from knowledge base ...")
        knowledge_base = load_knowledge_base()
        missing_categories = predict_missing_requirements(requirements, knowledge_base)
        total_categories = len(knowledge_base.get("categories", {}))

        print("[8/8] Predicting project complexity and computing scores ...")
        functional_count = sum(1 for c in classifications if c["label"] == "Functional")
        non_functional_count = sum(
            1 for c in classifications if c["label"] == "Non-Functional"
        )
        complexity_result = predict_complexity(
            total_requirements=len(requirements),
            functional_count=functional_count,
            non_functional_count=non_functional_count,
            ambiguous_ratio=ambiguity_summary["ambiguity_ratio"],
            duplicate_ratio=duplicate_ratio,
            missing_category_ratio=(
                len(missing_categories) / total_categories if total_categories > 0 else 0.0
            ),
        )

        completeness_score = compute_completeness_score(
            missing_categories_count=len(missing_categories),
            total_categories=total_categories,
            ambiguity_ratio=ambiguity_summary["ambiguity_ratio"],
            duplicate_ratio=duplicate_ratio,
        )
        overall_confidence = compute_overall_confidence(classifications)

        report_text = generate_report(
            source_file=file_path,
            requirements=requirements,
            classifications=classifications,
            ambiguity_results=ambiguity_results,
            ambiguity_summary=ambiguity_summary,
            duplicate_pairs=duplicate_pairs,
            missing_categories=missing_categories,
            complexity_result=complexity_result,
            completeness_score=completeness_score,
            overall_confidence=overall_confidence,
        )

        print("\n" + report_text)

        saved_path = save_report(report_text, DEFAULT_REPORT_PATH)
        print(f"\n[INFO] Report successfully saved to: {saved_path}")

    except FileNotFoundError as exc:
        print(f"\n[ERROR] {exc}")
    except UnsupportedFileTypeError as exc:
        print(f"\n[ERROR] {exc}")
    except DocumentParsingError as exc:
        print(f"\n[ERROR] {exc}")
    except SpaCyModelNotFoundError as exc:
        print(f"\n[ERROR] {exc}")
    except ModelNotTrainedError as exc:
        print(f"\n[ERROR] {exc}")
    except KnowledgeBaseLoadError as exc:
        print(f"\n[ERROR] {exc}")
    except RuntimeError as exc:
        print(f"\n[ERROR] {exc}")
    except OSError as exc:
        print(f"\n[ERROR] {exc}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"\n[UNEXPECTED ERROR] {exc}")


def main() -> None:
    """Run the interactive console application main loop."""
    print_banner()

    while True:
        print_menu()
        choice = input("\nSelect an option (1-2): ").strip()

        if choice == "1":
            file_path = prompt_file_path()
            if not file_path:
                file_path = DEFAULT_SAMPLE_PATH
            run_analysis(file_path)
        elif choice == "2":
            print("\nExiting AI-Based Software Requirement Analyzer. Goodbye!")
            sys.exit(0)
        else:
            print("\n[WARNING] Invalid option. Please select 1 or 2.")


if __name__ == "__main__":
    main()
