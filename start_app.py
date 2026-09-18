"""
start_app.py
============

Cross-platform Python launcher for the AI-Based Software Requirement Analyzer.
Guarantees correct working directory, checks model artifacts, and launches
the FastAPI Uvicorn server with auto-browser opening.
"""

import os
import sys
import time
import webbrowser
import threading
import uvicorn

# Guarantee working directory is the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)


def open_browser():
    """Wait briefly for the server to start, then open the default web browser."""
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")


def main():
    print("=" * 75)
    print("        AI-BASED SOFTWARE REQUIREMENT ANALYZER — SERVER LAUNCHER")
    print("=" * 75)
    print(f"Project Directory : {BASE_DIR}")
    print(f"Web Interface URL : http://127.0.0.1:8000")
    print(f"Interactive Docs  : http://127.0.0.1:8000/docs")
    print("=" * 75)
    print()

    # Check model artifacts
    clf_path = os.path.join(BASE_DIR, "models", "classifier.pkl")
    if not os.path.isfile(clf_path):
        print("[INFO] Model files not found. Running training pipeline...")
        from train_model import run_training_pipeline
        run_training_pipeline()

    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn ASGI Server
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
