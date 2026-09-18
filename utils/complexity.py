"""
complexity.py
=============

Predicts overall project complexity (Low / Medium / High) based on
statistical and structural features derived from the analyzed SRS document,
including volume, functional/non-functional distribution, ambiguity,
duplicate density, and domain coverage gaps.
"""

from typing import Dict, TypedDict, Any


class ComplexityFactor(TypedDict):
    """Normalized factor with value and human description."""
    score: float  # 0.0 to 100.0
    weight: float
    description: str


class ComplexityResult(TypedDict):
    """Type definition for a project complexity prediction result."""
    complexity_level: str  # "Low", "Medium", "High"
    complexity_score: float  # 0.0 to 100.0
    tier: str  # Alias for UI compatibility
    factors: Dict[str, float]
    factor_breakdown: Dict[str, ComplexityFactor]
    explanation: str


def _normalize(value: float, max_value: float) -> float:
    """Normalize a value into the [0.0, 1.0] range."""
    if max_value <= 0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))


def predict_complexity(
    total_requirements: int,
    functional_count: int,
    non_functional_count: int,
    ambiguous_ratio: float,
    duplicate_ratio: float,
    missing_category_ratio: float,
) -> ComplexityResult:
    """
    Predict project complexity using a multi-factor weighted scoring model.
    """
    # 1. Size Factor (0 to 1) - reference max 80 requirements
    size_norm = _normalize(total_requirements, 80)
    
    # 2. Non-Functional Ratio Factor (0 to 1) - balanced ratio is ~0.3 to 0.5
    nfr_ratio = (non_functional_count / total_requirements) if total_requirements > 0 else 0.0
    nfr_norm = _normalize(nfr_ratio, 0.5)

    # 3. Ambiguity Factor (0 to 1)
    ambiguity_norm = _normalize(ambiguous_ratio, 0.4)

    # 4. Duplicate Factor (0 to 1)
    duplicate_norm = _normalize(duplicate_ratio, 0.3)

    # 5. Missing Coverage Factor (0 to 1)
    missing_norm = _normalize(missing_category_ratio, 0.7)

    weights = {
        "size": 0.25,
        "nfr_ratio": 0.20,
        "ambiguity": 0.20,
        "duplicate": 0.15,
        "missing_coverage": 0.20,
    }

    weighted_score = (
        size_norm * weights["size"]
        + nfr_norm * weights["nfr_ratio"]
        + ambiguity_norm * weights["ambiguity"]
        + duplicate_norm * weights["duplicate"]
        + missing_norm * weights["missing_coverage"]
    )

    complexity_score = round(weighted_score * 100, 1)

    if complexity_score < 35.0:
        level = "Low"
        explanation = (
            f"Low complexity project ({complexity_score}/100). The specification contains a manageable scope "
            f"({total_requirements} requirements) with low ambiguity ({ambiguous_ratio*100:.1f}%) and "
            f"minimal structural overlap, indicating straightforward implementation."
        )
    elif complexity_score < 68.0:
        level = "Medium"
        explanation = (
            f"Moderate complexity project ({complexity_score}/100). Balanced functional scope ({functional_count} FRs, "
            f"{non_functional_count} NFRs) with manageable quality considerations. Some refinement of non-functional "
            f"constraints and ambiguous terms is recommended prior to development."
        )
    else:
        level = "High"
        explanation = (
            f"High complexity project ({complexity_score}/100). Characterized by high requirement volume, "
            f"substantial non-functional/architectural constraints ({non_functional_count} NFRs), "
            f"or notable domain coverage gaps requiring rigorous architectural review."
        )

    factors_dict = {
        "size_factor": round(size_norm * 100, 1),
        "non_functional_ratio_factor": round(nfr_norm * 100, 1),
        "ambiguity_factor": round(ambiguity_norm * 100, 1),
        "duplicate_factor": round(duplicate_norm * 100, 1),
        "missing_coverage_factor": round(missing_norm * 100, 1),
    }

    factor_breakdown = {
        "Requirement Volume": {
            "score": round(size_norm * 100, 1),
            "weight": weights["size"],
            "description": f"{total_requirements} total requirements extracted"
        },
        "Non-Functional Scope": {
            "score": round(nfr_norm * 100, 1),
            "weight": weights["nfr_ratio"],
            "description": f"{non_functional_count} Non-Functional requirements ({nfr_ratio*100:.1f}%)"
        },
        "Ambiguity Density": {
            "score": round(ambiguity_norm * 100, 1),
            "weight": weights["ambiguity"],
            "description": f"{ambiguous_ratio*100:.1f}% requirements contain ambiguous wording"
        },
        "Duplicate Overlap": {
            "score": round(duplicate_norm * 100, 1),
            "weight": weights["duplicate"],
            "description": f"{duplicate_ratio*100:.1f}% requirement semantic overlap"
        },
        "Domain Gap Ratio": {
            "score": round(missing_norm * 100, 1),
            "weight": weights["missing_coverage"],
            "description": f"{missing_category_ratio*100:.1f}% domain category gap"
        }
    }

    return {
        "complexity_level": level,
        "complexity_score": complexity_score,
        "tier": level,
        "factors": factors_dict,
        "factor_breakdown": factor_breakdown,
        "explanation": explanation
    }
