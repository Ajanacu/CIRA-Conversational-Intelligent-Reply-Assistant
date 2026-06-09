#!/usr/bin/env python3
"""
WhatsApp Reply Assistant - Startup Script
Launches both the FastAPI backend and Streamlit frontend
"""
import subprocess
import sys
import os
import time
import threading
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

processes = []


def run_backend():
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND_DIR
    p = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR,
        env=env,
    )
    processes.append(p)
    p.wait()


def run_frontend():
    time.sleep(5)  # Wait for backend to start
    env = os.environ.copy()
    env["PYTHONPATH"] = FRONTEND_DIR
    p = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.port", "8501",
         "--server.address", "localhost",
         "--theme.base", "dark",
         "--theme.primaryColor", "#25D366",
         "--theme.backgroundColor", "#0d1117",
         "--theme.secondaryBackgroundColor", "#111827",
         "--theme.textColor", "#f9fafb",
         ],
        cwd=FRONTEND_DIR,
        env=env,
    )
    processes.append(p)
    p.wait()


def shutdown(sig, frame):
    print("\n🛑 Shutting down...")
    for p in processes:
        p.terminate()
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

print("=" * 55)
print("  💬 WhatsApp Reply Assistant")
print("=" * 55)
print("  🚀 Starting backend  → http://localhost:8000")
print("  🌐 Starting frontend → http://localhost:8501")
print("  Press Ctrl+C to stop")
print("=" * 55)

t1 = threading.Thread(target=run_backend, daemon=True)
t2 = threading.Thread(target=run_frontend, daemon=True)

t1.start()
t2.start()

t1.join()
t2.join()
