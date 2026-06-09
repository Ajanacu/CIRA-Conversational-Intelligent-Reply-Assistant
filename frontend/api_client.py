"""
API client for communicating with FastAPI backend
"""
import requests
import streamlit as st

BASE_URL = "http://localhost:8000"


def get_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_post(endpoint: str, data: dict = None, files=None, authenticated: bool = True):
    headers = get_headers() if authenticated else {}
    try:
        if files:
            resp = requests.post(f"{BASE_URL}{endpoint}", headers=headers, files=files, timeout=60)
        else:
            resp = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, timeout=60)
        return resp
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure the backend server is running on port 8000.")
        return None


def api_get(endpoint: str, authenticated: bool = True):
    headers = get_headers() if authenticated else {}
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=30)
        return resp
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure the backend server is running on port 8000.")
        return None
