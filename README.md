# 💬 CIRA — WhatsApp Reply Assistant

> AI-powered WhatsApp reply generator that learns your personal messaging style.  
> Supports **English**, **Manglish**, formal, informal, and casual tones.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-frontend-red?logo=streamlit)
![Claude](https://img.shields.io/badge/AI-Claude%20Haiku-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Features

- 🧠 **Style Learning** — Analyzes your actual messages to match your tone
- 🗣️ **Manglish Support** — Detects and replicates Malayalam-English mixing
- 💬 **3 Reply Options** — Personalized, context-aware suggestions
- 📊 **Chat Dashboard** — Hourly/daily activity, mood analysis, top words
- 🔒 **Private by Default** — All data stored locally in SQLite
- 👥 **Multi-user** — Login system with isolated data per user
- 💰 **Credit Efficient** — Uses Claude Haiku; analysis cached (no repeat costs)

```

## 🗂 Project Structure
whatsapp_reply_assistant/
├── backend/
│   ├── main.py              # FastAPI REST API
│   ├── database.py          # SQLite database layer
│   ├── analyzer.py          # WhatsApp chat parser + stats
│   └── reply_generator.py   # Anthropic API calls
├── frontend/
│   ├── app.py               # Streamlit main app
│   ├── api_client.py        # HTTP client for backend
│   └── pages/
│       ├── auth.py          # Login / Register
│       ├── reply.py         # Reply Assistant
│       ├── dashboard.py     # Analytics Dashboard
│       └── upload.py        # Chat Upload
├── requirements.txt
├── start.py                 # One-command launcher
├── .env.example
└── README.md

```

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/cira-whatsapp-assistant.git
cd cira-whatsapp-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 4. Launch the app
```bash
python start.py
```

| Service | URL |
|---|---|
| Frontend UI | http://localhost:8501 |
| Backend API | http://localhost:8000 |

---

## 📖 How to Use

1. **Register / Login** — Create an account
2. **Export your WhatsApp chat** — Open chat → ⋮ → More → Export Chat → Without Media → save `.txt`
3. **Upload** the `.txt` file in the app
4. **Analyze** — One-time style extraction (cached in SQLite)
5. **Generate replies** — Paste any incoming message → get 3 personalized options

---

## 💰 API Cost Estimate

| Action | Approx. Cost |
|---|---|
| Style analysis (one-time per chat) | ~$0.01–0.02 |
| Each reply generation | ~$0.001–0.003 |

> With $5, you can generate **1,500–3,000+ replies** using Claude Haiku.

---

## 🔒 Privacy

- Chat data stored **locally** in `backend/app.db` (never uploaded)
- Only writing samples sent to Anthropic for pattern analysis
- API key stored in session only — never written to disk
- Each user's data is fully isolated

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLite + PyJWT |
| Frontend | Streamlit + Plotly |
| AI | Anthropic Claude Haiku |
| Language | 100% Python |

---

## 📄 License

MIT © 2025 — Built with ❤️ using Claude API
