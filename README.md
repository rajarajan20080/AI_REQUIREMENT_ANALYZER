# 🚀 AI-Based Software Requirement Analyzer (ReqAnalyzer.AI)

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active%20%2F%20production--ready-brightgreen.svg)]()

An enterprise-grade, NLP & Machine Learning platform for Software Requirements Specification (SRS) quality analysis, ambiguity detection, functional vs. non-functional classification, semantic duplicate identification, complexity estimation, domain completeness scoring, and automated report generation.

---

## ✨ Key Features

- **📑 Multi-Format Document Parsing:** Upload & analyze `.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx`, `.xls`, `.json`, `.jsonl`, `.md`, and `.markdown`.
- **🤖 ML-Powered Classification:** Accurately classifies requirements into **Functional (FR)** and **Non-Functional (NFR)** using an optimized TF-IDF + Logistic Regression ensemble (~91%+ accuracy on PROMISE & PURE datasets).
- **⚠️ Ambiguity & Vague Terms Detection:** Pinpoints weak words, non-verifiable phrases, passive voice, and unquantified metrics.
- **🔍 Semantic Duplicate Detection:** Leverages `sentence-transformers` embeddings (`all-MiniLM-L6-v2`) and cosine similarity to discover redundant or conflicting requirements.
- **📊 Quality & Completeness Scoring:** Computes IEEE 830-aligned quality metrics, readability, testability, and identifies missing requirements against domain knowledge bases (Healthcare, E-Commerce, Banking, IoT, etc.).
- **📈 Interactive Web Dashboard:** Dark-mode UI with live Chart.js analytics, radar charts, session history, filtering, search, and instant PDF/Markdown report export.
- **💾 Session Persistence:** Embedded SQLite storage for tracking SRS evolution across iterations.
- **🔒 100% Local & Privacy-Preserving:** Zero external API dependencies required; runs entirely on your local machine.

---

## 🛠️ Architecture & Tech Stack

- **Backend:** FastAPI, Uvicorn, Pydantic, Scikit-Learn, spaCy (`en_core_web_sm`), Sentence-Transformers, NLTK
- **Frontend:** Vanilla HTML5 / Modern CSS3 (Glassmorphism & dark palette) / ES6+ JavaScript, Chart.js
- **Persistence:** SQLite Database (`data/history.db`)
- **Parsers:** `pypdf`, `python-docx`, `openpyxl`, `pandas`

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/rajarajan20080/AI-Requirement-Analyzer.git
cd AI-Requirement-Analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Launch the Application

#### Option A — 1-Click Batch File (Windows):
Double click `run_app.bat` or run:
```cmd
run_app.bat
```

#### Option B — Python Launcher (Cross-Platform):
```bash
python start_app.py
```

#### Option C — Direct Uvicorn Command:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🌐 Application Access & API Documentation

Once launched, visit:
- **Interactive UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🧪 Automated Testing

Run the end-to-end verification suite:
```bash
python test_api.py
```

---

## 📂 Project Structure

```
AI-Requirement-Analyzer/
├── app.py                  # FastAPI server & REST API endpoints
├── start_app.py            # Cross-platform application launcher
├── main.py                 # Interactive CLI terminal interface
├── train_model.py          # ML training pipeline for requirement classification
├── test_api.py             # Automated end-to-end test suite
├── gen_srs.py              # Synthetic SRS generator for testing & benchmarking
├── run_app.bat             # Windows 1-click execution script
├── requirements.txt        # Python dependency manifest
├── frontend/               # Web Application UI (HTML, CSS, JS)
├── data/                   # Datasets, domain knowledge bases, and SQLite database
├── models/                 # Serialized ML models & vectorizers
└── utils/                  # Core NLP, classification, ambiguity & report engines
```

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
