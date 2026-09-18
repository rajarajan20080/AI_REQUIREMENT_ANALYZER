"""
ambiguity.py
============

Rule-based and linguistic detection of ambiguous requirement statements.
Identifies unclear, subjective, non-measurable, or non-verifiable terms.
Provides detailed explanations:
1. What is ambiguous (flagged terms and clauses)
2. Why it is ambiguous (linguistic and engineering rationale)
3. How to improve (actionable suggested rewrites and precision templates)
"""

import re
from typing import Dict, List, TypedDict, Optional

# Detailed knowledge dictionary for ambiguous terms with explanations and rewrite guidelines
AMBIGUITY_KNOWLEDGE: Dict[str, Dict[str, str]] = {
    "quickly": {
        "reason": "'Quickly' is subjective and not measurable. It does not define specific latency, response time, or throughput thresholds.",
        "suggestion": "Specify an exact quantitative response time (e.g., 'within 2 seconds under standard network load').",
        "severity": "High"
    },
    "fast": {
        "reason": "'Fast' lacks concrete performance metrics such as round-trip time, processing latency, or frame rate.",
        "suggestion": "Define measurable performance criteria (e.g., 'render results in under 500 milliseconds').",
        "severity": "High"
    },
    "user-friendly": {
        "reason": "'User-friendly' cannot be tested directly without empirical usability metrics or task completion criteria.",
        "suggestion": "Define specific usability criteria (e.g., 'allow a trained user to complete checkout in less than 3 minutes with zero critical errors').",
        "severity": "High"
    },
    "user friendly": {
        "reason": "'User friendly' is subjective and open to divergent interpretations.",
        "suggestion": "Define concrete usability benchmarks, such as SUS (System Usability Scale) >= 80 or task completion rate >= 95%.",
        "severity": "High"
    },
    "easy to use": {
        "reason": "'Easy to use' is an untestable subjective assertion.",
        "suggestion": "Specify maximum training time required or maximum number of clicks/steps to complete the target action.",
        "severity": "High"
    },
    "easy-to-use": {
        "reason": "'Easy-to-use' cannot be objectively verified during QA testing.",
        "suggestion": "State quantitative UX requirements (e.g., 'first-time user onboarding achievable within 5 minutes without external assistance').",
        "severity": "High"
    },
    "easily": {
        "reason": "'Easily' is non-verifiable and subjective.",
        "suggestion": "State the exact mechanism and maximum interaction steps (e.g., 'within 2 clicks from the main navigation menu').",
        "severity": "Medium"
    },
    "efficient": {
        "reason": "'Efficient' does not quantify resource consumption (CPU, memory, disk I/O, network bandwidth).",
        "suggestion": "Quantify resource constraints (e.g., 'consuming less than 256MB of RAM and under 15% CPU utilization under peak load').",
        "severity": "High"
    },
    "efficiently": {
        "reason": "'Efficiently' does not provide measurable computational or algorithmic bounds.",
        "suggestion": "Specify target resource limits or algorithmic complexity expectations.",
        "severity": "High"
    },
    "secure": {
        "reason": "'Secure' is overly broad. It does not define specific security standards, encryption algorithms, or threat models.",
        "suggestion": "Specify concrete security standards (e.g., 'encrypt data at rest using AES-256 and in transit using TLS 1.3 with SHA-256').",
        "severity": "High"
    },
    "secure enough": {
        "reason": "'Secure enough' is dangerously ambiguous with no clear compliance baseline.",
        "suggestion": "Mandate compliance with an established standard (e.g., OWASP Top 10, NIST SP 800-53, or SOC 2 Type II).",
        "severity": "High"
    },
    "reasonable": {
        "reason": "'Reasonable' leaves boundary conditions undefined and subject to dispute.",
        "suggestion": "Define explicit upper and lower bounds for acceptable behavior.",
        "severity": "Medium"
    },
    "reasonably": {
        "reason": "'Reasonably' introduces ambiguity into system boundaries.",
        "suggestion": "Replace with explicit numerical bounds.",
        "severity": "Medium"
    },
    "sufficient": {
        "reason": "'Sufficient' does not define the minimum or maximum capacity, storage, or bandwidth required.",
        "suggestion": "Provide exact capacity parameters (e.g., 'support at least 10,000 concurrent user sessions with 50GB storage capacity').",
        "severity": "Medium"
    },
    "sufficiently": {
        "reason": "'Sufficiently' fails to specify operational thresholds.",
        "suggestion": "Provide exact measurable criteria.",
        "severity": "Medium"
    },
    "adequate": {
        "reason": "'Adequate' provides no verifiable metric for pass/fail testing.",
        "suggestion": "State the minimum acceptable threshold explicitly (e.g., 'maintain a minimum of 99.9% uptime').",
        "severity": "Medium"
    },
    "appropriate": {
        "reason": "'Appropriate' leaves the choice of action or behavior unspecified.",
        "suggestion": "Explicitly define the specific response or algorithm to be executed.",
        "severity": "Medium"
    },
    "robust": {
        "reason": "'Robust' does not specify error recovery protocols or fault-tolerance limits.",
        "suggestion": "Define failure handling (e.g., 'automatically retry failed database connections up to 3 times with exponential backoff before logging an alert').",
        "severity": "Medium"
    },
    "seamless": {
        "reason": "'Seamless' is marketing terminology without technical engineering meaning.",
        "suggestion": "State whether data synchronization occurs in real-time (e.g., within 500ms) or via asynchronous background jobs.",
        "severity": "Low"
    },
    "seamlessly": {
        "reason": "'Seamlessly' fails to specify synchronization latency or transition protocols.",
        "suggestion": "Define data sync time and failover behavior explicitly.",
        "severity": "Low"
    },
    "flexible": {
        "reason": "'Flexible' does not clarify which configuration options, plugins, or extensions are supported.",
        "suggestion": "Specify the exact configuration parameters, file formats, or APIs supported.",
        "severity": "Low"
    },
    "scalable": {
        "reason": "'Scalable' does not define horizontal/vertical scaling targets or auto-scaling triggers.",
        "suggestion": "Specify target load capacity (e.g., 'scale horizontally from 2 to 20 instances when CPU utilization exceeds 75% for 3 consecutive minutes').",
        "severity": "Medium"
    },
    "intuitive": {
        "reason": "'Intuitive' is subjective and cannot be objectively validated in software testing.",
        "suggestion": "Specify standard UI guidelines (e.g., 'adhere to Material Design guidelines with clear visual hierarchy').",
        "severity": "Medium"
    },
    "simple": {
        "reason": "'Simple' is subjective.",
        "suggestion": "Define the maximum number of steps or cognitive load criteria.",
        "severity": "Low"
    },
    "as needed": {
        "reason": "'As needed' does not define the conditions, triggers, or schedules under which the action occurs.",
        "suggestion": "Specify exact triggering events or recurring cron schedules (e.g., 'every 24 hours at 02:00 UTC or upon administrator request').",
        "severity": "High"
    },
    "as required": {
        "reason": "'As required' fails to specify the business rules or governance conditions.",
        "suggestion": "State the precise business logic condition (e.g., 'when account balance drops below $0.00').",
        "severity": "Medium"
    },
    "as necessary": {
        "reason": "'As necessary' lacks deterministic triggers.",
        "suggestion": "Define the exact boolean conditions for triggering.",
        "severity": "Medium"
    },
    "etc": {
        "reason": "'Etc' leaves the requirement scope unbounded and open-ended, risking scope creep.",
        "suggestion": "Enumerate the full, exhaustive list of supported items or entities.",
        "severity": "High"
    },
    "etc.": {
        "reason": "'Etc.' leaves the requirement scope open-ended and unverified.",
        "suggestion": "Replace with an exhaustive list of all supported options or states.",
        "severity": "High"
    },
    "several": {
        "reason": "'Several' is an imprecise quantity.",
        "suggestion": "Specify an exact integer or range (e.g., 'between 3 and 7').",
        "severity": "Medium"
    },
    "some": {
        "reason": "'Some' is indeterminate.",
        "suggestion": "Specify the exact count, percentage, or selection criteria.",
        "severity": "Medium"
    },
    "many": {
        "reason": "'Many' does not define capacity limits.",
        "suggestion": "Provide exact minimum/maximum load quantities (e.g., 'up to 5,000 items').",
        "severity": "Medium"
    },
    "few": {
        "reason": "'Few' is non-specific.",
        "suggestion": "State the precise number or threshold.",
        "severity": "Medium"
    },
    "normal": {
        "reason": "'Normal' assumes shared context without defining normal operating parameters.",
        "suggestion": "Define normal parameters (e.g., 'under standard operating load of 1,000 req/sec').",
        "severity": "Low"
    },
    "typical": {
        "reason": "'Typical' is undefined in formal specifications.",
        "suggestion": "Define the baseline operating conditions.",
        "severity": "Low"
    },
    "should": {
        "reason": "'Should' expresses preference rather than a mandatory requirement (RFC 2119).",
        "suggestion": "Use 'shall' for mandatory requirements, or clarify if this is an optional feature.",
        "severity": "Medium"
    },
    "could": {
        "reason": "'Could' creates ambiguity regarding whether the feature is in scope.",
        "suggestion": "Decide scope: use 'shall' if mandatory or move to future enhancements.",
        "severity": "Medium"
    },
    "might": {
        "reason": "'Might' indicates uncertainty in requirement specification.",
        "suggestion": "Clarify contractual requirement obligation using 'shall'.",
        "severity": "Medium"
    },
    "may": {
        "reason": "'May' denotes optionality. If the feature is mandatory, 'shall' must be used.",
        "suggestion": "Use 'shall' if required, or 'may' only when explicitly granting permission to users.",
        "severity": "Low"
    },
    "state-of-the-art": {
        "reason": "'State-of-the-art' is promotional phrasing without technical criteria.",
        "suggestion": "Specify explicit algorithms, libraries, or architectural specifications.",
        "severity": "High"
    },
    "modern": {
        "reason": "'Modern' changes with time and provides no technical test criteria.",
        "suggestion": "Specify target browsers, framework versions, or architectural standards.",
        "severity": "Low"
    },
    "timely": {
        "reason": "'Timely' does not specify maximum allowable delay.",
        "suggestion": "Specify maximum delivery window (e.g., 'within 60 seconds of event occurrence').",
        "severity": "High"
    },
    "regularly": {
        "reason": "'Regularly' does not specify a periodic schedule.",
        "suggestion": "Define explicit recurrence intervals (e.g., 'daily at 00:00 UTC').",
        "severity": "Medium"
    },
    "periodically": {
        "reason": "'Periodically' does not specify execution intervals.",
        "suggestion": "Specify an exact schedule (e.g., 'every 15 minutes').",
        "severity": "Medium"
    },
    "handle a reasonably large": {
        "reason": "Vague volume description with no upper bound for stress testing.",
        "suggestion": "Specify the maximum load (e.g., 'support up to 50,000 transactions per hour').",
        "severity": "High"
    }
}


class AmbiguityDetail(TypedDict):
    """Structured detail for a single ambiguous term occurrence."""
    term: str
    reason: str
    suggestion: str
    severity: str


class AmbiguityResult(TypedDict):
    """Type definition for a single requirement ambiguity analysis result."""
    requirement: str
    ambiguous_terms: List[str]
    details: List[AmbiguityDetail]
    has_measurable_criteria: bool
    ambiguity_score: float  # 0.0 to 1.0
    is_ambiguous: bool
    severity: str  # High, Medium, Low, None
    explanation: str
    suggested_rewrite: str


def _has_measurable_criteria(text: str) -> bool:
    """
    Determine whether the requirement contains measurable criteria
    such as digits, percentages, time units (ms, sec, min, hr), or data units (KB, MB, GB).
    """
    patterns = [
        r"\b\d+(\.\d+)?\b",
        r"\b\d+%",
        r"\b\d+\s*(ms|milliseconds|seconds|sec|minutes|min|hours|hrs|days)\b",
        r"\b\d+\s*(kb|mb|gb|tb|req/sec|tps|users)\b"
    ]
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            return True
    return False


def _generate_suggested_rewrite(original_text: str, details: List[AmbiguityDetail]) -> str:
    """
    Create an AI-recommended rewrite template for an ambiguous requirement.
    """
    if not details:
        return original_text

    rewrite = original_text
    
    # Common replacement rules
    replacements = {
        r"\bquickly\b": "within 2 seconds",
        r"\bfast\b": "in under 500ms",
        r"\buser-friendly\b": "intuitive (achieving >=90% task completion in usability testing)",
        r"\buser friendly\b": "intuitive (achieving >=90% task completion in usability testing)",
        r"\beasy to use\b": "requiring <= 3 user interaction steps",
        r"\beasily\b": "within 2 clicks from the navigation menu",
        r"\befficiently\b": "using <= 256MB of memory",
        r"\befficient\b": "optimized for low memory (<256MB)",
        r"\bsecure\b": "secured using AES-256 and TLS 1.3 encryption",
        r"\bsecure enough\b": "compliant with OWASP Top 10 security standards",
        r"\bas needed\b": "upon user event trigger or every 24 hours",
        r"\betc\.?\b": "[explicitly listed entities]",
        r"\bshould\b": "shall",
        r"\bcould\b": "shall",
        r"\bmight\b": "shall",
        r"\bregularly\b": "every 24 hours at 00:00 UTC",
        r"\bperiodically\b": "every 15 minutes",
        r"\btimely\b": "within 60 seconds",
        r"\brobust\b": "fault-tolerant with automatic 3x retry mechanism",
        r"\bscalable\b": "scalable up to 10,000 concurrent users"
    }

    for pattern, repl in replacements.items():
        rewrite = re.sub(pattern, repl, rewrite, flags=re.IGNORECASE)

    # Ensure "The system shall" prefix if missing standard IEEE modal
    if not re.search(r"\b(shall|must|will)\b", rewrite, flags=re.IGNORECASE):
        if rewrite.lower().startswith("the system "):
            rewrite = "The system shall " + rewrite[11:]
        elif not rewrite.lower().startswith("users "):
            rewrite = "The system shall " + rewrite[0].lower() + rewrite[1:]

    return rewrite


def detect_ambiguous_requirement(text: str) -> AmbiguityResult:
    """
    Analyze a single requirement statement for ambiguity with detailed reasoning.
    """
    lowered = text.lower()
    found_terms: List[str] = []
    details: List[AmbiguityDetail] = []
    
    # Sort keys by length descending to match phrases before individual words
    sorted_keys = sorted(AMBIGUITY_KNOWLEDGE.keys(), key=len, reverse=True)
    
    matched_spans = []
    for term in sorted_keys:
        pattern = r"\b" + re.escape(term) + r"\b"
        matches = list(re.finditer(pattern, lowered))
        if matches:
            # Check if this span is already covered by a longer phrase
            is_new = False
            for m in matches:
                span = (m.start(), m.end())
                if not any(span[0] >= existing[0] and span[1] <= existing[1] for existing in matched_spans):
                    matched_spans.append(span)
                    is_new = True
            if is_new and term not in found_terms:
                found_terms.append(term)
                info = AMBIGUITY_KNOWLEDGE[term]
                details.append({
                    "term": term,
                    "reason": info["reason"],
                    "suggestion": info["suggestion"],
                    "severity": info["severity"]
                })

    measurable = _has_measurable_criteria(text)
    is_ambiguous = len(found_terms) > 0

    # Determine severity
    if not is_ambiguous:
        severity = "None"
        ambiguity_score = 0.0 if measurable else 0.1
    elif any(d["severity"] == "High" for d in details):
        severity = "High"
        ambiguity_score = min(1.0, 0.4 + (len(found_terms) * 0.2) - (0.15 if measurable else 0.0))
    elif any(d["severity"] == "Medium" for d in details):
        severity = "Medium"
        ambiguity_score = min(1.0, 0.25 + (len(found_terms) * 0.15) - (0.1 if measurable else 0.0))
    else:
        severity = "Low"
        ambiguity_score = min(1.0, 0.15 + (len(found_terms) * 0.1))

    ambiguity_score = round(ambiguity_score, 2)

    # Human-readable explanation
    if not is_ambiguous:
        explanation = "Requirement uses clear, non-ambiguous phrasing without vague qualitative modifiers."
        suggested_rewrite = text
    else:
        reasons_list = [f"'{d['term']}': {d['reason']}" for d in details]
        explanation = " ".join(reasons_list)
        suggested_rewrite = _generate_suggested_rewrite(text, details)

    return {
        "requirement": text,
        "ambiguous_terms": found_terms,
        "details": details,
        "has_measurable_criteria": measurable,
        "ambiguity_score": ambiguity_score,
        "is_ambiguous": is_ambiguous,
        "severity": severity,
        "explanation": explanation,
        "suggested_rewrite": suggested_rewrite
    }


def detect_ambiguous_requirements(requirements: List[str]) -> List[AmbiguityResult]:
    """
    Analyze a list of requirement statements for ambiguity.
    """
    return [detect_ambiguous_requirement(req) for req in requirements]


def summarize_ambiguity(results: List[AmbiguityResult]) -> Dict:
    """
    Summarize ambiguity detection results across all requirements.
    """
    total = len(results)
    ambiguous_count = sum(1 for result in results if result["is_ambiguous"])
    ratio = (ambiguous_count / total) if total > 0 else 0.0

    high_severity_count = sum(1 for r in results if r["severity"] == "High")
    med_severity_count = sum(1 for r in results if r["severity"] == "Medium")
    low_severity_count = sum(1 for r in results if r["severity"] == "Low")

    # Frequency of terms
    term_counts: Dict[str, int] = {}
    for r in results:
        for term in r["ambiguous_terms"]:
            term_counts[term] = term_counts.get(term, 0) + 1

    return {
        "total_requirements": total,
        "ambiguous_count": ambiguous_count,
        "ambiguity_ratio": round(ratio, 3),
        "ambiguity_percentage": round(ratio * 100, 1),
        "high_severity_count": high_severity_count,
        "medium_severity_count": med_severity_count,
        "low_severity_count": low_severity_count,
        "frequent_ambiguous_terms": term_counts,
        "clear_count": total - ambiguous_count
    }
