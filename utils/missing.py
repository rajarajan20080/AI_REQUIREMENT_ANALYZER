"""
missing.py
==========

Predicts potentially missing requirements by comparing the extracted requirements
against a domain knowledge base of standard requirement categories.
Produces structured AI recommendations grouped by category with concrete
rationale and priority rankings.
"""

import json
import os
import re
from typing import Dict, List, TypedDict, Any, Optional


class KnowledgeBaseLoadError(Exception):
    """Raised when the knowledge base file cannot be loaded."""


class MissingRecommendation(TypedDict):
    """Type definition for a single missing requirement AI recommendation."""
    category: str
    suggested_requirement: str
    reason: str
    priority: str  # "High", "Medium", "Low"
    supporting_items: List[str]
    is_covered: bool
    matched_keywords: List[str]


CATEGORY_PRIORITIES: Dict[str, str] = {
    "Authentication": "High",
    "Authorization": "High",
    "Session Management": "High",
    "Data Backup": "High",
    "Logging and Audit": "High",
    "Error Handling": "High",
    "Security": "High",
    "Data Validation": "High",
    "Performance": "Medium",
    "Scalability": "Medium",
    "Monitoring": "Medium",
    "Reporting": "Medium",
    "Notification": "Low",
    "Usability": "Low",
    "Payment Processing": "Medium",
    "Accessibility": "Low",
    "Internationalization": "Low",
    "Compliance": "High",
    "Search Functionality": "Low",
    "User Management": "Medium",
    "API Integration": "Medium",
    "Data Retention": "Medium"
}

CATEGORY_SUPPORTING_ITEMS: Dict[str, List[str]] = {
    "Authentication": ["Forgot Password / Password Reset Flow", "Password Complexity Validation", "Multi-Factor Authentication (MFA)", "Account Lockout after N Failed Attempts", "Secure Email Verification"],
    "Authorization": ["Role-Based Access Control (RBAC)", "Privilege Separation (Admin vs User)", "Permission Enforcement on API Endpoints"],
    "Session Management": ["Automatic Session Timeout after Inactivity", "Single-Sign-On (SSO) Support", "Explicit User Logout & Token Revocation"],
    "Data Backup": ["Automated Daily Database Backups", "Point-in-Time Recovery Mechanism", "Disaster Recovery Testing & Offsite Storage"],
    "Logging and Audit": ["Audit Trails for Sensitive Data Mutations", "System Event & Access Logging", "Centralized Log Aggregation"],
    "Error Handling": ["Generic Error Messages for Security", "Structured Exception Logging", "User-Friendly Error Fallback Pages"],
    "Security": ["End-to-End Encryption in Transit (TLS 1.3)", "Data-at-Rest Encryption (AES-256)", "CSRF & XSS Protection Headers"],
    "Data Validation": ["Server-Side Input Sanitization", "Boundary & Type Checking on All Forms", "Regex Format Validation for Emails & Phone Numbers"],
    "Performance": ["Sub-Second API Response Times", "Asset Compression & Caching Headers", "Database Query Indexing & Optimization"],
    "Scalability": ["Stateless Horizontal Auto-Scaling", "Load Balancing across App Replicas", "Database Read/Write Replica Splitting"],
    "Monitoring": ["Health Check Endpoints (/healthz)", "Uptime & Error Rate Alerting", "APM Tracing for Slow Database Queries"]
}

CATEGORY_REASONS: Dict[str, str] = {
    "Authentication": "Secure authentication prevents unauthorized access and protects user credentials across system touchpoints.",
    "Authorization": "Ensures that authenticated users cannot access administrative capabilities or cross-tenant data without proper role permissions.",
    "Session Management": "Protects against session hijacking, replay attacks, and lingering active sessions on shared workstations.",
    "Data Backup": "Crucial for business continuity, disaster recovery, and compliance with data safety standards.",
    "Logging and Audit": "Mandatory for regulatory compliance (SOC2/HIPAA/GDPR), security forensics, and operational debugging.",
    "Error Handling": "Prevents sensitive stack traces from leaking to users and provides resilient degradation during network or service failures.",
    "Security": "Protects data integrity and user privacy against eavesdropping, injection, and unauthorized exfiltration.",
    "Data Validation": "First line of defense against SQL injection, cross-site scripting (XSS), and database corruption.",
    "Performance": "Defines quantitative response time and throughput targets needed for load testing and SLA verification.",
    "Scalability": "Guarantees system elasticity and stability as transaction volumes and concurrent users increase.",
    "Monitoring": "Enables proactive operations alerting before system outages impact end users."
}


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_KB_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")


def load_knowledge_base(
    knowledge_base_path: Optional[str] = None
) -> Dict:
    """
    Load the requirement knowledge base from a JSON file.
    """
    target_path = knowledge_base_path or DEFAULT_KB_PATH

    if not os.path.isfile(target_path):
        # Fallback checks
        alt_path = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.json")
        rel_path = os.path.join("data", "knowledge_base.json")
        if os.path.isfile(alt_path):
            target_path = alt_path
        elif os.path.isfile(rel_path):
            target_path = rel_path
        else:
            raise KnowledgeBaseLoadError(
                f"Knowledge base file not found at '{target_path}'."
            )

    try:
        with open(target_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeBaseLoadError(
            f"Failed to load knowledge base: {exc}"
        ) from exc


def _category_is_covered(category_keywords: List[str], combined_text: str) -> List[str]:
    """
    Check which keywords of a category are present in the combined SRS text.
    """
    found = []
    for keyword in category_keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, combined_text):
            found.append(keyword)
    return found


def predict_missing_requirements(
    requirements: List[str],
    knowledge_base: Dict,
) -> List[Dict[str, Any]]:
    """
    Compare the SRS requirements against every category in the knowledge
    base and report categories that appear to have no coverage.
    """
    combined_text = " ".join(requirements).lower()
    categories = knowledge_base.get("categories", {})

    missing: List[Dict[str, Any]] = []
    for category_name, category_data in categories.items():
        keywords = category_data.get("keywords", [])
        matched = _category_is_covered(keywords, combined_text)
        if not matched:
            priority = CATEGORY_PRIORITIES.get(category_name, "Medium")
            supporting = CATEGORY_SUPPORTING_ITEMS.get(category_name, [])
            reason = CATEGORY_REASONS.get(
                category_name,
                f"No requirements found for the '{category_name}' domain in the uploaded document."
            )
            missing.append({
                "category": category_name,
                "suggested_requirement": category_data.get("description", ""),
                "reason": reason,
                "priority": priority,
                "supporting_items": supporting,
                "is_covered": False,
                "matched_keywords": []
            })

    # Sort by priority: High first, then Medium, then Low
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    missing.sort(key=lambda x: priority_order.get(x["priority"], 3))
    return missing


def get_all_category_statuses(
    requirements: List[str],
    knowledge_base: Dict,
) -> Dict[str, Any]:
    """
    Return comprehensive domain coverage analysis with both covered and missing categories.
    """
    combined_text = " ".join(requirements).lower()
    categories = knowledge_base.get("categories", {})

    covered: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []

    for category_name, category_data in categories.items():
        keywords = category_data.get("keywords", [])
        matched = _category_is_covered(keywords, combined_text)
        priority = CATEGORY_PRIORITIES.get(category_name, "Medium")
        supporting = CATEGORY_SUPPORTING_ITEMS.get(category_name, [])
        reason = CATEGORY_REASONS.get(category_name, f"Standard domain category for software specifications.")

        if matched:
            covered.append({
                "category": category_name,
                "description": category_data.get("description", ""),
                "matched_keywords": matched,
                "is_covered": True,
                "priority": priority
            })
        else:
            missing.append({
                "category": category_name,
                "suggested_requirement": category_data.get("description", ""),
                "reason": reason,
                "priority": priority,
                "supporting_items": supporting,
                "is_covered": False,
                "matched_keywords": []
            })

    total = len(categories)
    covered_count = len(covered)
    coverage_percentage = round((covered_count / total * 100), 1) if total > 0 else 100.0

    return {
        "total_categories": total,
        "covered_count": covered_count,
        "missing_count": len(missing),
        "coverage_percentage": coverage_percentage,
        "covered_categories": covered,
        "missing_categories": missing
    }
