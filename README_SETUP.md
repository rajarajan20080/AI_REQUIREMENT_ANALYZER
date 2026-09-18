# AI-Based Software Requirement Analyzer — Setup & Run Guide

Production-grade AI/NLP platform for Software Requirements Specification (SRS) quality analysis, ambiguity detection, functional/non-functional classification, semantic duplicate identification, and domain completeness scoring.

---

## 🚀 How to Run the Project (Independent of any IDE)

You do **not** need Antigravity, VS Code, or any IDE open to run this application. You can run it directly using any of the options below:

### Option 1: 1-Click Startup Script (Windows Batch)
Double-click `run_app.bat` or run in Command Prompt:
```cmd
run_app.bat
```
* Automatically sets the working directory.
* Automatically detects virtual environments (`.venv` / `venv`) or system Python.
* Automatically checks and trains ML model files if they are missing.
* Starts the backend Uvicorn server and automatically opens your browser to `http://127.0.0.1:8000`.

---

### Option 2: PowerShell Launcher
In PowerShell:
```powershell
.\start_server.ps1
```

---

### Option 3: Python Launcher (Cross-Platform)
In any terminal:
```bash
python start_app.py
```
or directly with FastAPI/Uvicorn:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

---

### Option 4: Console/CLI Mode (Interactive Terminal)
```bash
python main.py
```

---

## 🌐 Application Access Points

Once started, open your web browser to:
* **Web UI Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive OpenAPI Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Diagnostic Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 📦 Prerequisites & Installation

If running on a fresh environment:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python train_model.py
```

---

## 🔑 Environment Variables (.env)
* **No `.env` variables or external API keys are required.**
* The application runs 100% locally with offline-capable Scikit-Learn classifiers, spaCy NLP pipeline, and local Sentence-Transformers embeddings.

---

## 📁 Architecture Overview
* **Backend Framework:** FastAPI + Uvicorn (Python 3.10+)
* **Frontend Framework:** Vanilla HTML5 / CSS3 / JavaScript (ES6+) with Chart.js analytics, served directly from `static/` by FastAPI.
* **Storage / Persistence:** SQLite database stored at `data/history.db`.
* **AI / ML Models:**
  - TF-IDF + Logistic Regression classifier (`models/classifier.pkl`, `models/vectorizer.pkl`)
  - spaCy `en_core_web_sm` NLP text processing pipeline
  - Sentence-Transformers `all-MiniLM-L6-v2` for semantic similarity & duplicate detection
  - Domain completeness knowledge base (`data/knowledge_base.json`)
