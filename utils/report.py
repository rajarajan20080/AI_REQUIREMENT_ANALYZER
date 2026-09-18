"""
report.py
=========

Builds a clean, production-grade analysis report from all pipeline results
and formats it for on-screen viewing, text file download, or markdown export.
"""

import os
from datetime import datetime
from typing import Dict, List, Any

LINE_WIDTH = 80


def generate_markdown_report(data: Dict[str, Any], source_title: str = "SRS Document") -> str:
    """
    Assemble the full analysis report formatted in rich GitHub Flavored Markdown.
    """
    summary = data.get("summary", {})
    quality = data.get("quality", {})
    complexity = data.get("complexity", {})
    ambiguity = data.get("ambiguity", {})
    duplicates = data.get("duplicates", {})
    missing_categories = data.get("missing_categories", [])
    classifications = data.get("classifications", [])

    total_reqs = summary.get("total_requirements", len(classifications))
    func_count = summary.get("functional_count", 0)
    nfr_count = summary.get("non_functional_count", 0)
    quality_score = quality.get("overall_score", 0.0)
    completeness_score = summary.get("completeness_score", 0.0)
    overall_confidence = summary.get("overall_confidence", 0.0)
    complexity_level = complexity.get("complexity_level", "Medium")

    md: List[str] = []
    md.append(f"# 📊 AI Requirement Analysis Report — {source_title}")
    md.append(f"**Generated On:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    md.append(f"**Analysis Engine:** AI-Based Software Requirement Analyzer v2.0 (NLP & ML Pipeline)")
    md.append("\n---\n")

    # Executive Summary Card
    md.append("## 📌 Executive Summary")
    md.append(f"| Metric | Value | Rating / Status |")
    md.append("| :--- | :--- | :--- |")
    md.append(f"| **Overall Quality Score** | `{quality_score} / 100` | **{quality.get('quality_tier', 'Good Quality')}** |")
    md.append(f"| **Completeness Score** | `{completeness_score}%` | Domain Coverage Index |")
    md.append(f"| **Project Complexity** | **{complexity_level}** | Score: `{complexity.get('complexity_score', 0.0)}/100` |")
    md.append(f"| **Total Requirements** | `{total_reqs}` | `{func_count}` Functional, `{nfr_count}` Non-Functional |")
    md.append(f"| **Avg AI Confidence** | `{overall_confidence}%` | Model Certainty |")
    md.append(f"| **Ambiguous Statements** | `{ambiguity.get('ambiguous_count', 0)}` (`{ambiguity.get('ambiguity_percentage', 0)}%`) | Flagged for Revision |")
    md.append(f"| **Duplicate Overlaps** | `{len(duplicates.get('pairs', []))}` pairs | Semantic Cosine Distance |")
    md.append(f"| **Domain Gap Warnings** | `{len(missing_categories)}` categories | AI Recommendations |")
    md.append("\n")

    if quality.get("executive_summary"):
        md.append(f"> **Assessment:** {quality.get('executive_summary')}\n")

    # Quality Dimensions
    md.append("## 🎯 Multidimensional Quality Breakdown")
    md.append("| Dimension | Score | Description |")
    md.append("| :--- | :--- | :--- |")
    md.append(f"| **Clarity** | `{quality.get('clarity', 0)} / 100` | Syntactic clarity, absence of ambiguous clauses |")
    md.append(f"| **Completeness** | `{quality.get('completeness', 0)} / 100` | Standard actor-action-outcome structure & domain coverage |")
    md.append(f"| **Consistency** | `{quality.get('consistency', 0)} / 100` | Absence of semantic duplication or contradictions |")
    md.append(f"| **Specificity** | `{quality.get('specificity', 0)} / 100` | Presence of quantifiable units, metrics, and parameters |")
    md.append(f"| **Testability** | `{quality.get('testability', 0)} / 100` | Verifiable pass/fail criteria and measurable boundaries |")
    md.append("\n")

    # Key Strengths & Recommendations
    if quality.get("key_strengths"):
        md.append("### ✅ Key Strengths")
        for s in quality.get("key_strengths", []):
            md.append(f"- {s}")
        md.append("")

    if quality.get("improvement_recommendations"):
        md.append("### 💡 Recommended Actions")
        for r in quality.get("improvement_recommendations", []):
            md.append(f"- {r}")
        md.append("")

    # Ambiguity Details
    md.append("## ⚠️ Ambiguity Analysis")
    amb_items = [c for c in classifications if c.get("ambiguity", {}).get("is_ambiguous", False)]
    if not amb_items:
        md.append("✅ **No ambiguous requirement statements detected.** All statements use precise, measurable phrasing.\n")
    else:
        md.append(f"Found **{len(amb_items)}** requirement(s) with vague or subjective phrasing:\n")
        for item in amb_items:
            req_id = item.get("id", "REQ")
            text = item.get("requirement", "")
            amb = item.get("ambiguity", {})
            terms = ", ".join([f"`{t}`" for t in amb.get("ambiguous_terms", [])])
            md.append(f"#### `{req_id}` — {text}")
            md.append(f"- **Flagged Terms:** {terms} (Severity: **{amb.get('severity', 'Medium')}**)")
            md.append(f"- **Problem:** {amb.get('explanation', '')}")
            md.append(f"- **AI Suggested Rewrite:** *\"{amb.get('suggested_rewrite', '')}\"*")
            md.append("")

    # Duplicates Details
    md.append("## 👥 Duplicate & Semantic Similarity Analysis")
    dup_pairs = duplicates.get("pairs", [])
    if not dup_pairs:
        md.append("✅ **No duplicate requirement statements detected.** Semantic similarity threshold satisfied.\n")
    else:
        md.append(f"Detected **{len(dup_pairs)}** pair(s) with high semantic similarity:\n")
        for pair in dup_pairs:
            sim_pct = pair.get("similarity_percentage", round(pair.get("similarity_score", 0.8) * 100, 1))
            status = pair.get("status", "Duplicate")
            md.append(f"- **Similarity: {sim_pct}%** (`{status}`)")
            md.append(f"  - **{pair.get('req_id_a', 'REQ-A')}:** {pair.get('requirement_a', '')}")
            md.append(f"  - **{pair.get('req_id_b', 'REQ-B')}:** {pair.get('requirement_b', '')}")
            md.append("")

    # Missing Domain Recommendations
    md.append("## 💡 Potentially Missing Domain Requirements")
    if not missing_categories:
        md.append("✅ **Comprehensive domain coverage.** All major software architecture categories are addressed.\n")
    else:
        md.append("The following domain categories were not detected in the SRS. These are AI recommendations to ensure completeness:\n")
        for m in missing_categories:
            cat = m.get("category", "")
            prio = m.get("priority", "Medium")
            sugg = m.get("suggested_requirement", "")
            reason = m.get("reason", "")
            md.append(f"### 🔹 {cat} (Priority: `{prio}`)")
            md.append(f"- **Rationale:** {reason}")
            md.append(f"- **Recommended Baseline Requirement:** *\"{sugg}\"*")
            supp = m.get("supporting_items", [])
            if supp:
                md.append("- **Recommended Capabilities:**")
                for s in supp:
                    md.append(f"  - {s}")
            md.append("")

    # Full Requirements Table
    md.append("## 📋 Extracted Requirements Inventory")
    md.append("| ID | Classification | Conf. | Quality | Ambiguity | Requirement Statement |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for item in classifications:
        req_id = item.get("id", "REQ")
        label = item.get("label", "Functional")
        conf = f"{round(item.get('confidence', 0.8)*100, 1)}%"
        q_score = item.get("quality", {}).get("overall_score", "-")
        is_amb = "⚠️ Ambiguous" if item.get("ambiguity", {}).get("is_ambiguous", False) else "✅ Clear"
        text = item.get("requirement", "").replace("|", "\\|")
        md.append(f"| `{req_id}` | **{label}** | `{conf}` | `{q_score}` | {is_amb} | {text} |")
    md.append("\n---\n*Report generated by AI-Based Software Requirement Analyzer.*")

    return "\n".join(md)


def generate_text_report(data: Dict[str, Any], source_title: str = "SRS Document") -> str:
    """
    Assemble the full analysis report formatted as plain text with clean borders.
    """
    summary = data.get("summary", {})
    quality = data.get("quality", {})
    complexity = data.get("complexity", {})
    ambiguity = data.get("ambiguity", {})
    duplicates = data.get("duplicates", {})
    missing_categories = data.get("missing_categories", [])
    classifications = data.get("classifications", [])

    lines: List[str] = []
    lines.append("=" * LINE_WIDTH)
    lines.append("AI-BASED SOFTWARE REQUIREMENT ANALYZER".center(LINE_WIDTH))
    lines.append("EXECUTIVE ANALYSIS REPORT".center(LINE_WIDTH))
    lines.append("=" * LINE_WIDTH)
    lines.append(f"Source Document : {source_title}")
    lines.append(f"Generated On    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Extracted : {summary.get('total_requirements', len(classifications))} requirements")
    lines.append("-" * LINE_WIDTH)

    lines.append("\n[1] EXECUTIVE METRICS")
    lines.append(f"  * Overall Quality Score    : {quality.get('overall_score', 0)} / 100 ({quality.get('quality_tier', 'Good Quality')})")
    lines.append(f"  * Completeness Score       : {summary.get('completeness_score', 0)} / 100")
    lines.append(f"  * Average AI Confidence    : {summary.get('overall_confidence', 0)}%")
    lines.append(f"  * Project Complexity Level : {complexity.get('complexity_level', 'Medium')} ({complexity.get('complexity_score', 0)}/100)")
    lines.append(f"  * Functional Requirements  : {summary.get('functional_count', 0)}")
    lines.append(f"  * Non-Functional Reqs      : {summary.get('non_functional_count', 0)}")
    lines.append(f"  * Ambiguous Requirements   : {ambiguity.get('ambiguous_count', 0)} ({ambiguity.get('ambiguity_percentage', 0)}%)")
    lines.append(f"  * Duplicate Overlaps       : {len(duplicates.get('pairs', []))} pair(s)")

    lines.append("\n[2] QUALITY DIMENSIONS")
    lines.append(f"  * Clarity Score      : {quality.get('clarity', 0)} / 100")
    lines.append(f"  * Completeness Score : {quality.get('completeness', 0)} / 100")
    lines.append(f"  * Consistency Score  : {quality.get('consistency', 0)} / 100")
    lines.append(f"  * Specificity Score  : {quality.get('specificity', 0)} / 100")
    lines.append(f"  * Testability Score  : {quality.get('testability', 0)} / 100")

    lines.append("\n[3] AMBIGUITY FINDINGS")
    amb_items = [c for c in classifications if c.get("ambiguity", {}).get("is_ambiguous", False)]
    if not amb_items:
        lines.append("  No ambiguous requirements detected.")
    else:
        for item in amb_items:
            lines.append(f"  - [{item.get('id', 'REQ')}] {item.get('requirement', '')}")
            lines.append(f"      Terms: {', '.join(item.get('ambiguity', {}).get('ambiguous_terms', []))}")
            lines.append(f"      Issue: {item.get('ambiguity', {}).get('explanation', '')}")
            lines.append(f"      Rewrite: {item.get('ambiguity', {}).get('suggested_rewrite', '')}")

    lines.append("\n[4] DUPLICATE FINDINGS")
    dup_pairs = duplicates.get("pairs", [])
    if not dup_pairs:
        lines.append("  No duplicate requirements detected.")
    else:
        for pair in dup_pairs:
            sim_pct = pair.get("similarity_percentage", round(pair.get("similarity_score", 0.8)*100, 1))
            lines.append(f"  - Similarity: {sim_pct}% ({pair.get('status', 'Duplicate')})")
            lines.append(f"      [{pair.get('req_id_a', 'REQ-A')}]: {pair.get('requirement_a', '')}")
            lines.append(f"      [{pair.get('req_id_b', 'REQ-B')}]: {pair.get('requirement_b', '')}")

    lines.append("\n[5] POTENTIALLY MISSING DOMAIN RECOMMENDATIONS")
    if not missing_categories:
        lines.append("  All primary domain categories are covered.")
    else:
        for m in missing_categories:
            lines.append(f"  - Category: {m.get('category', '')} (Priority: {m.get('priority', 'Medium')})")
            lines.append(f"      Rationale: {m.get('reason', '')}")
            lines.append(f"      Suggested: {m.get('suggested_requirement', '')}")

    lines.append("\n" + "=" * LINE_WIDTH)
    lines.append("END OF REPORT".center(LINE_WIDTH))
    lines.append("=" * LINE_WIDTH)

    return "\n".join(lines)


def save_report(report_text: str, output_path: str = "report.txt") -> str:
    """Save report to a local text file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return os.path.abspath(output_path)
