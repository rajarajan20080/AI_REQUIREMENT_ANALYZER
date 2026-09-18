"""
parser.py
=========

Handles extraction of raw requirement statements from Software Requirement
Specification (SRS) documents and datasets in ALL major formats:
- Plain Text (.txt)
- Markdown (.md, .markdown)
- Microsoft Word (.docx)
- Adobe PDF (.pdf)
- Comma-Separated Values (.csv)
- Microsoft Excel (.xlsx, .xls)
- JavaScript Object Notation (.json)
- JSON Lines (.jsonl)

Assigns sequential requirement IDs (REQ-001, REQ-002, ...) to each extracted statement.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Union

import docx
import pandas as pd
import pdfplumber

# Common candidate column/key names for requirements in tabular or JSON data
REQ_FIELD_CANDIDATES = [
    "requirement_text", "requirement", "RequirementText", "text", "content",
    "statement", "sentence", "Description", "description", "req_text", "req",
    "Requirements", "Requirement_Text", "Specification", "specification",
    "user_story", "story", "item", "clause"
]


class UnsupportedFileTypeError(Exception):
    """Raised when a file with an unsupported extension is provided."""


class DocumentParsingError(Exception):
    """Raised when a document cannot be parsed successfully."""


def _clean_line(line: str) -> str:
    """
    Remove common leading numbering/bullets (e.g. '1.', '1)', '-', '*', 'REQ-01:', '### ') and
    strip surrounding whitespace from a single line of text.
    """
    if not line:
        return ""
    cleaned = str(line).strip()
    # Remove markdown headers (e.g., "### ")
    cleaned = re.sub(r"^[#\s]+", "", cleaned)
    # Remove leading numbering like "1.", "1.1", "REQ-1:", "R-01.", bullets, dashes, quotes
    cleaned = re.sub(
        r"^\s*(REQ[\-_]?\d+[\.:\)]?|R[\-_]?\d+[\.:\)]?|\d+(\.\d+)*[\.\)]|\-|\*|•|▪|►|\>)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    # Strip surrounding quotes if present
    cleaned = cleaned.strip("\"' ")
    return cleaned.strip()


def _is_requirement_like(line: str) -> bool:
    """
    Heuristically determine whether a cleaned line looks like an actual
    requirement statement (as opposed to a heading, blank line, table header, or noise).
    """
    if not line:
        return False
    words = line.split()
    if len(words) < 3:
        return False

    # Filter out obvious non-requirement headers
    lowered = line.lower()
    header_patterns = [
        r"^(table of contents|contents|introduction|scope|overview|glossary|appendix|references|revision history)$",
        r"^section \d+(\.\d+)*$",
        r"^(page \d+|version \d+(\.\d+)*)$",
        r"^(software requirements specification|srs document|project name:?)$"
    ]
    for pat in header_patterns:
        if re.match(pat, lowered.strip()):
            return False

    return True


def format_requirement_id(index: int) -> str:
    """
    Format a 1-based index into a standard requirement ID (e.g. REQ-001).
    """
    return f"REQ-{index:03d}"


def parse_raw_text(text: str) -> List[str]:
    """
    Parse a raw multiline text string and extract requirement lines.
    """
    if not text or not text.strip():
        return []

    raw_lines = text.splitlines()
    requirements: List[str] = []
    for raw_line in raw_lines:
        cleaned = _clean_line(raw_line)
        if _is_requirement_like(cleaned):
            requirements.append(cleaned)
    return requirements


def parse_txt(file_path: str) -> List[str]:
    """
    Parse a plain-text (.txt) SRS document and extract requirement lines.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
            raw_text = handle.read()
    except OSError as exc:
        raise DocumentParsingError(f"Unable to read TXT file '{file_path}': {exc}") from exc

    return parse_raw_text(raw_text)


def parse_markdown(file_path: str) -> List[str]:
    """
    Parse a Markdown (.md, .markdown) SRS document and extract requirement statements.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
            raw_text = handle.read()
    except OSError as exc:
        raise DocumentParsingError(f"Unable to read Markdown file '{file_path}': {exc}") from exc

    return parse_raw_text(raw_text)


def parse_docx(file_path: str) -> List[str]:
    """
    Parse a DOCX SRS document and extract requirement paragraphs and table rows.
    """
    try:
        document = docx.Document(file_path)
    except Exception as exc:
        raise DocumentParsingError(f"Unable to read DOCX file '{file_path}': {exc}") from exc

    requirements: List[str] = []
    for paragraph in document.paragraphs:
        cleaned = _clean_line(paragraph.text)
        if _is_requirement_like(cleaned):
            requirements.append(cleaned)

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                cleaned = _clean_line(cell.text)
                if _is_requirement_like(cleaned) and cleaned not in requirements:
                    requirements.append(cleaned)

    return requirements


def parse_pdf(file_path: str) -> List[str]:
    """
    Parse a PDF SRS document and extract requirement lines from every page.
    """
    requirements: List[str] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                for raw_line in text.split("\n"):
                    cleaned = _clean_line(raw_line)
                    if _is_requirement_like(cleaned):
                        requirements.append(cleaned)
    except Exception as exc:
        raise DocumentParsingError(f"Unable to read PDF file '{file_path}': {exc}") from exc

    return requirements


def _find_requirement_column(df: pd.DataFrame) -> Optional[str]:
    """
    Locate the best matching column name in a DataFrame representing requirement text.
    """
    # 1. Exact or case-insensitive candidate match
    for col in df.columns:
        if col in REQ_FIELD_CANDIDATES or str(col).lower() in [c.lower() for c in REQ_FIELD_CANDIDATES]:
            return str(col)

    # 2. Heuristic: string column with highest average length / word count
    best_col = None
    max_avg_words = 0.0
    for col in df.columns:
        series = df[col].dropna().astype(str)
        if len(series) > 0:
            avg_words = series.str.split().apply(len).mean()
            if avg_words > max_avg_words and avg_words >= 3:
                max_avg_words = avg_words
                best_col = str(col)

    return best_col


def parse_csv(file_path: str) -> List[str]:
    """
    Parse a CSV dataset or document and extract requirement statements.
    """
    try:
        # Try comma, semicolon, and tab delimiters with robust fallback
        try:
            df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
        except Exception:
            df = pd.read_csv(file_path, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
    except Exception as exc:
        raise DocumentParsingError(f"Unable to parse CSV file '{file_path}': {exc}") from exc

    if df.empty:
        return []

    req_col = _find_requirement_column(df)
    requirements: List[str] = []

    if req_col:
        for val in df[req_col].dropna():
            cleaned = _clean_line(str(val))
            if _is_requirement_like(cleaned):
                requirements.append(cleaned)
    else:
        # Fallback: inspect each cell in the dataframe
        for _, row in df.iterrows():
            for val in row.dropna():
                cleaned = _clean_line(str(val))
                if _is_requirement_like(cleaned) and cleaned not in requirements:
                    requirements.append(cleaned)

    return requirements


def parse_excel(file_path: str) -> List[str]:
    """
    Parse an Excel (.xlsx, .xls) workbook and extract requirement statements from all sheets.
    """
    try:
        excel_file = pd.ExcelFile(file_path)
        requirements: List[str] = []

        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name)
            if df.empty:
                continue

            req_col = _find_requirement_column(df)
            if req_col:
                for val in df[req_col].dropna():
                    cleaned = _clean_line(str(val))
                    if _is_requirement_like(cleaned) and cleaned not in requirements:
                        requirements.append(cleaned)
            else:
                for _, row in df.iterrows():
                    for val in row.dropna():
                        cleaned = _clean_line(str(val))
                        if _is_requirement_like(cleaned) and cleaned not in requirements:
                            requirements.append(cleaned)

        return requirements
    except Exception as exc:
        raise DocumentParsingError(f"Unable to parse Excel file '{file_path}': {exc}") from exc


def parse_json(file_path: str) -> List[str]:
    """
    Parse a JSON (.json) or JSON Lines (.jsonl) file containing requirements.
    Supports list of strings, list of objects, or nested objects.
    """
    requirements: List[str] = []
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".jsonl":
        return parse_jsonl(file_path)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        def extract_from_obj(obj: Any) -> None:
            if isinstance(obj, str):
                cleaned = _clean_line(obj)
                if _is_requirement_like(cleaned):
                    requirements.append(cleaned)
            elif isinstance(obj, dict):
                # Check known candidate keys
                found_key = next((k for k in obj if k in REQ_FIELD_CANDIDATES or k.lower() in [c.lower() for c in REQ_FIELD_CANDIDATES]), None)
                if found_key and isinstance(obj[found_key], str):
                    cleaned = _clean_line(obj[found_key])
                    if _is_requirement_like(cleaned):
                        requirements.append(cleaned)
                else:
                    for val in obj.values():
                        if isinstance(val, (dict, list)):
                            extract_from_obj(val)
                        elif isinstance(val, str):
                            cleaned = _clean_line(val)
                            if _is_requirement_like(cleaned):
                                requirements.append(cleaned)
            elif isinstance(obj, list):
                for item in obj:
                    extract_from_obj(item)

        extract_from_obj(data)
        return requirements

    except Exception as exc:
        raise DocumentParsingError(f"Unable to parse JSON file '{file_path}': {exc}") from exc


def parse_jsonl(file_path: str) -> List[str]:
    """
    Parse a JSON Lines (.jsonl) file and extract requirement statements line by line.
    """
    requirements: List[str] = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if isinstance(record, str):
                    cleaned = _clean_line(record)
                    if _is_requirement_like(cleaned):
                        requirements.append(cleaned)
                elif isinstance(record, dict):
                    found_key = next((k for k in record if k in REQ_FIELD_CANDIDATES or k.lower() in [c.lower() for c in REQ_FIELD_CANDIDATES]), None)
                    if found_key and isinstance(record[found_key], str):
                        cleaned = _clean_line(record[found_key])
                        if _is_requirement_like(cleaned):
                            requirements.append(cleaned)
                    else:
                        for val in record.values():
                            if isinstance(val, str):
                                cleaned = _clean_line(val)
                                if _is_requirement_like(cleaned):
                                    requirements.append(cleaned)
                                    break
        return requirements
    except Exception as exc:
        raise DocumentParsingError(f"Unable to parse JSONL file '{file_path}': {exc}") from exc


def parse_file(file_path: str) -> List[str]:
    """
    Detect the file type from its extension and dispatch to the appropriate parser.
    Supports .txt, .docx, .pdf, .csv, .xlsx, .xls, .json, .jsonl, .md, .markdown.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: '{file_path}'")

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":
        return parse_txt(file_path)
    if extension in [".md", ".markdown"]:
        return parse_markdown(file_path)
    if extension == ".docx":
        return parse_docx(file_path)
    if extension == ".pdf":
        return parse_pdf(file_path)
    if extension == ".csv":
        return parse_csv(file_path)
    if extension in [".xlsx", ".xls"]:
        return parse_excel(file_path)
    if extension == ".json":
        return parse_json(file_path)
    if extension == ".jsonl":
        return parse_jsonl(file_path)

    raise UnsupportedFileTypeError(
        f"Unsupported file extension '{extension}'. Supported types: .txt, .docx, .pdf, .csv, .xlsx, .xls, .json, .jsonl, .md"
    )
