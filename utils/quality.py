"""
quality.py
==========

Evaluates requirement quality across multiple standard software engineering
dimensions:
1. Clarity - assesses readability, sentence structure, lack of obscure clauses
2. Completeness - verifies presence of actor, action, trigger/outcome, and condition
3. Consistency - checks lack of contradictory or overlapping statements
4. Specificity - assesses quantifiable criteria, concrete constraints, and numbers
5. Testability - assesses verifiability with explicit pass/fail observable conditions
6. Ambiguity - inverse penalty of detected subjective/vague language

Computes an Overall Quality Score (0-100) and actionable improvement advice.
"""

import re
from typing import Dict, List, TypedDict, Any


class RequirementQuality(TypedDict):
    """Quality metrics for an individual requirement statement."""
    requirement_id: str
    requirement: str
    overall_score: float  # 0 to 100
    clarity_score: float
    completeness_score: float
    consistency_score: float
    specificity_score: float
    testability_score: float
    status: str  # "Excellent", "Good", "Needs Improvement", "Poor"
    issues: List[str]
    suggestions: List[str]


class QualityAnalysisSummary(TypedDict):
    """Overall quality analysis results across the full SRS document."""
    overall_score: float  # 0 to 100
    clarity: float
    completeness: float
    consistency: float
    specificity: float
    testability: float
    ambiguity_penalty: float
    quality_tier: str  # "Production Ready", "Good Quality", "Moderate Risk", "Action Required"
    executive_summary: str
    key_strengths: List[str]
    improvement_recommendations: List[str]
    per_requirement_quality: List[RequirementQuality]


def _evaluate_single_requirement(
    req_id: str,
    text: str,
    is_ambiguous: bool,
    ambiguity_score: float,
    duplicate_count: int,
    confidence: float
) -> RequirementQuality:
    """
    Score a single requirement across clarity, completeness, consistency,
    specificity, and testability.
    """
    issues: List[str] = []
    suggestions: List[str] = []

    words = text.split()
    word_count = len(words)
    lowered = text.lower()

    # 1. Clarity (0 - 100)
    # Ideal requirement length is 10 - 30 words. Too short = missing context; too long = run-on sentence.
    clarity = 90.0
    if word_count < 6:
        clarity -= 25.0
        issues.append("Statement is excessively brief, potentially omitting critical context.")
        suggestions.append("Expand requirement with explicit actor and system outcome.")
    elif word_count > 35:
        clarity -= 20.0
        issues.append("Statement is overly verbose and may combine multiple requirements.")
        suggestions.append("Split into multiple atomic requirement statements.")

    if is_ambiguous:
        clarity -= (ambiguity_score * 35.0)

    clarity = max(10.0, min(100.0, clarity))

    # 2. Completeness (0 - 100)
    # Does it have an actor (e.g. system, user, admin), action modal (shall, must, will), and target?
    completeness = 70.0
    has_modal = bool(re.search(r"\b(shall|must|will|should|can|requires)\b", lowered))
    has_actor = bool(re.search(r"\b(system|user|admin|administrator|client|customer|service|api|application)\b", lowered))
    has_action = bool(re.search(r"\b(allow|provide|support|display|generate|validate|encrypt|store|send|receive|authenticate|log|process|update|delete|create)\b", lowered))

    if has_modal:
        completeness += 10.0
    else:
        issues.append("Missing standard modal verb ('shall', 'must').")
        suggestions.append("Use standard IEEE formulation ('The system shall...').")

    if has_actor:
        completeness += 10.0
    else:
        issues.append("Subject/actor not explicitly stated.")
        suggestions.append("Specify exactly who or what triggers or executes this requirement.")

    if has_action:
        completeness += 10.0

    completeness = max(10.0, min(100.0, completeness))

    # 3. Consistency (0 - 100)
    consistency = 95.0
    if duplicate_count > 0:
        consistency -= (min(40.0, duplicate_count * 20.0))
        issues.append(f"Shares high semantic overlap with {duplicate_count} other requirement(s).")
        suggestions.append("Consolidate overlapping requirements to prevent duplicate implementation.")
    consistency = max(20.0, min(100.0, consistency))

    # 4. Specificity (0 - 100)
    # Quantifiable criteria, numbers, concrete algorithms or protocols
    specificity = 60.0
    has_digits = bool(re.search(r"\d", text))
    has_units = bool(re.search(r"\b(seconds|sec|ms|minutes|hours|days|%|percent|kb|mb|gb|bytes|records|users|tps)\b", lowered))
    has_standards = bool(re.search(r"\b(aes|tls|sha|oauth|jwt|gdpr|wcag|rest|json|http|https|sql)\b", lowered))

    if has_digits:
        specificity += 15.0
    if has_units:
        specificity += 15.0
    if has_standards:
        specificity += 10.0
    if is_ambiguous:
        specificity -= 20.0

    specificity = max(10.0, min(100.0, specificity))

    # 5. Testability (0 - 100)
    # Verifiable verbs, lack of vague words
    testability = 75.0
    untestable_words = ["user-friendly", "easy", "intuitive", "efficient", "appropriate", "adequate", "robust"]
    if any(uw in lowered for uw in untestable_words):
        testability -= 30.0
        issues.append("Contains subjective assertions that cannot be validated in automated or manual tests.")
        suggestions.append("Replace subjective assertions with quantitative pass/fail criteria.")
    if has_digits or has_units:
        testability += 15.0
    if not is_ambiguous:
        testability += 10.0

    testability = max(10.0, min(100.0, testability))

    # Weighted Overall Score
    overall = (
        clarity * 0.25 +
        completeness * 0.20 +
        consistency * 0.15 +
        specificity * 0.20 +
        testability * 0.20
    )
    overall = round(max(0.0, min(100.0, overall)), 1)

    if overall >= 85.0:
        status = "Excellent"
    elif overall >= 70.0:
        status = "Good"
    elif overall >= 55.0:
        status = "Needs Improvement"
    else:
        status = "Poor"

    return {
        "requirement_id": req_id,
        "requirement": text,
        "overall_score": overall,
        "clarity_score": round(clarity, 1),
        "completeness_score": round(completeness, 1),
        "consistency_score": round(consistency, 1),
        "specificity_score": round(specificity, 1),
        "testability_score": round(testability, 1),
        "status": status,
        "issues": issues,
        "suggestions": suggestions
    }


def analyze_srs_quality(
    requirements: List[str],
    ambiguity_results: List[Dict],
    duplicate_pairs: List[Dict],
    classifications: List[Dict],
    missing_categories_count: int,
    total_categories_count: int
) -> QualityAnalysisSummary:
    """
    Compute multidimensional quality scores across all requirements and generate
    an executive quality report with actionable recommendations.
    """
    if not requirements:
        return {
            "overall_score": 0.0,
            "clarity": 0.0,
            "completeness": 0.0,
            "consistency": 0.0,
            "specificity": 0.0,
            "testability": 0.0,
            "ambiguity_penalty": 0.0,
            "quality_tier": "Action Required",
            "executive_summary": "No requirement statements to analyze.",
            "key_strengths": [],
            "improvement_recommendations": ["Upload a populated SRS document with clear requirement statements."],
            "per_requirement_quality": []
        }

    # Count duplicate involvements per requirement index
    dup_counts: Dict[int, int] = {i: 0 for i in range(len(requirements))}
    for pair in duplicate_pairs:
        idx_a = pair.get("index_a", 0)
        idx_b = pair.get("index_b", 0)
        dup_counts[idx_a] = dup_counts.get(idx_a, 0) + 1
        dup_counts[idx_b] = dup_counts.get(idx_b, 0) + 1

    per_req_list: List[RequirementQuality] = []
    for idx, req_text in enumerate(requirements):
        req_id = f"REQ-{idx+1:03d}"
        amb_info = ambiguity_results[idx] if idx < len(ambiguity_results) else {}
        is_amb = amb_info.get("is_ambiguous", False)
        amb_score = amb_info.get("ambiguity_score", 0.0)
        conf = classifications[idx].get("confidence", 0.8) if idx < len(classifications) else 0.8
        dups = dup_counts.get(idx, 0)

        item_quality = _evaluate_single_requirement(
            req_id=req_id,
            text=req_text,
            is_ambiguous=is_amb,
            ambiguity_score=amb_score,
            duplicate_count=dups,
            confidence=conf
        )
        per_req_list.append(item_quality)

    avg_clarity = round(sum(q["clarity_score"] for q in per_req_list) / len(per_req_list), 1)
    avg_completeness = round(sum(q["completeness_score"] for q in per_req_list) / len(per_req_list), 1)
    avg_consistency = round(sum(q["consistency_score"] for q in per_req_list) / len(per_req_list), 1)
    avg_specificity = round(sum(q["specificity_score"] for q in per_req_list) / len(per_req_list), 1)
    avg_testability = round(sum(q["testability_score"] for q in per_req_list) / len(per_req_list), 1)

    # Domain coverage modifier for completeness
    if total_categories_count > 0:
        coverage_pct = ((total_categories_count - missing_categories_count) / total_categories_count) * 100
        avg_completeness = round((avg_completeness * 0.7) + (coverage_pct * 0.3), 1)

    # Overall Aggregate Quality Score
    overall_quality = round(
        (avg_clarity * 0.22) +
        (avg_completeness * 0.24) +
        (avg_consistency * 0.18) +
        (avg_specificity * 0.18) +
        (avg_testability * 0.18),
        1
    )

    ambiguous_total = sum(1 for q in ambiguity_results if q.get("is_ambiguous", False))
    ambiguity_penalty = round((ambiguous_total / len(requirements)) * 100, 1)

    # Quality Tier
    if overall_quality >= 85.0:
        quality_tier = "Production Ready"
        exec_summary = "The SRS exhibits high structural clarity, well-defined test criteria, and strong consistency across functional domains."
    elif overall_quality >= 70.0:
        quality_tier = "Good Quality"
        exec_summary = "The SRS is generally well-structured with minor ambiguity or missing non-functional constraints that should be refined before development."
    elif overall_quality >= 55.0:
        quality_tier = "Moderate Risk"
        exec_summary = "The SRS contains noticeable ambiguity, non-measurable language, or coverage gaps that introduce architectural and testing risks."
    else:
        quality_tier = "Action Required"
        exec_summary = "The SRS has substantial quality defects including high ambiguity, low testability, or duplicate statements that require urgent rework."

    # Key Strengths
    strengths: List[str] = []
    if avg_clarity >= 80:
        strengths.append("High syntactic clarity and readable sentence structure.")
    if avg_consistency >= 85:
        strengths.append("Low semantic duplication and consistent functional definitions.")
    if avg_testability >= 75:
        strengths.append("Clear observable actions and verifiable pass/fail criteria.")
    if avg_completeness >= 80:
        strengths.append("Strong domain category coverage and clear actor-action relationships.")
    if not strengths:
        strengths.append("Clear functional statements identified for core system operations.")

    # Actionable Recommendations
    recommendations: List[str] = []
    if ambiguous_total > 0:
        recommendations.append(f"Resolve {ambiguous_total} ambiguous requirement(s) by replacing subjective words (e.g. 'quickly', 'user-friendly') with quantitative metrics.")
    if len(duplicate_pairs) > 0:
        recommendations.append(f"Review and merge {len(duplicate_pairs)} duplicate or overlapping requirement pair(s) to streamline engineering backlog.")
    if missing_categories_count > 0:
        recommendations.append(f"Address {missing_categories_count} potentially missing architecture/security domain categories (e.g., Session Management, Backup, Audit).")
    if avg_specificity < 70:
        recommendations.append("Enhance specificity by adding concrete numeric criteria (e.g. response time in ms, uptime %, concurrent users).")
    if not recommendations:
        recommendations.append("Requirements meet all primary IEEE 830 quality guidelines. Ready for engineering sprint planning.")

    return {
        "overall_score": overall_quality,
        "clarity": avg_clarity,
        "completeness": avg_completeness,
        "consistency": avg_consistency,
        "specificity": avg_specificity,
        "testability": avg_testability,
        "ambiguity_penalty": ambiguity_penalty,
        "quality_tier": quality_tier,
        "executive_summary": exec_summary,
        "key_strengths": strengths,
        "improvement_recommendations": recommendations,
        "per_requirement_quality": per_req_list
    }
