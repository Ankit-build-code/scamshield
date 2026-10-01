# 🛡️ ScamShield

**AI-powered scam detection for India's elderly — voice-first, hybrid (rules + LLM), and community-reported.**

> **Problem Statement:** How can an elderly person tell whether a call, link, or message is genuine or a scam?
> **Sector:** Technology for Social Good · TATA Social Innovation Challenge (via Internshala)

---

## 🚀 What It Does

ScamShield lets anyone — especially elderly users who may not be comfortable typing — **speak or type** a phone number, link, or message, and instantly get a verdict:

- ✅ **Safe**
- ⚠️ **Suspicious**
- 🚫 **Dangerous**

Each verdict comes with a plain-language explanation and clear advice, read aloud in Hindi/English/Hinglish. Users can also **report** a scam in one tap — once 3 people report the same number/link, it's automatically added to the shared scam database for everyone.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎤 Voice input | Speak a message instead of typing (Web Speech API) |
| 🔊 Voice output | Verdict, explanation & advice read aloud |
| 🌐 Multilingual | Understands Hindi, Hinglish, and English |
| 🧠 Hybrid detection | Rule engine (known scam numbers/links/patterns) + LLM (catches new/unseen scams) |
| 🚩 Community reporting | Anonymous, device-based, duplicate-safe reporting that grows the database |
| 🔒 Privacy-first | No login required; rate-limited API; hashed URLs/numbers |
| 📱 Accessible UI | Large text, big buttons, simple navigation |

---

## 🏗️ Architecture

```
┌─────────────┐      HTTPS       ┌──────────────────┐
│   React     │ ───────────────► │     FastAPI       │
│  Frontend   │ ◄─────────────── │     Backend        │
└─────────────┘                  └─────────┬─────────┘
                                            │
                      ┌─────────────────────┼─────────────────────┐
                      ▼                     ▼                     ▼
              ┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
              │  Rule Engine   │   │   LLM API         │   │   PostgreSQL     │
              │ (patterns,     │   │  (Groq / OpenAI-  │   │  (indexed scam   │
              │  regex, known  │   │   compatible)      │   │   numbers, URLs, │
              │  scam DB)      │   │                    │   │   keywords,      │
              └───────────────┘   └─────────────────┘   │   reports)       │
                                                          └─────────────────┘
```

**Flow:** Input (voice/text) → Rule Engine (fast, offline-capable checks) → LLM layer (if score is inconclusive, adds context-aware reasoning) → Combined verdict + explanation → Optional: speak result aloud / report to community database.

---

## 🧰 Tech Stack

- **Frontend:** React (Vite)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (indexed tables: `scam_numbers`, `scam_urls`, `scam_keywords`, `user_reports`)
- **AI:** LLM via Groq API (OpenAI-compatible)
- **Voice:** Web Speech API (SpeechRecognition + SpeechSynthesis)
- **Security:** `slowapi` (rate limiting), SHA-256 hashing for URLs/numbers, environment-based secrets

---

## 📁 Project Structure

```
scam-shield-app/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── core/
│   │   │   ├── config.py          # Settings from .env
│   │   │   └── limiter.py         # Rate limiter instance
│   │   ├── routers/
│   │   │   ├── check.py           # POST /check
│   │   │   └── report.py          # POST /report
│   │   ├── services/
│   │   │   ├── scam_detector.py   # Rule-based detection logic
│   │   │   ├── llm_analyzer.py    # LLM-based analysis
│   │   │   └── report_service.py  # Crowdsourced reporting logic
│   │   ├── models/
│   │   │   └── scam.py            # SQLAlchemy models
│   │   ├── schemas/
│   │   │   ├── check.py           # Pydantic request/response models
│   │   │   └── report.py
│   │   └── db/
│   │       └── session.py         # DB connection/session
│   ├── seed.py                    # Seeds demo scam data
│   ├── requirements.txt
│   └── .env                       # Environment variables (not committed)
│
└── frontend/
    ├── src/
    │   ├── App.jsx                # Main UI (tabs, voice, result card, report)
    │   └── App.css
    └── package.json
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 1. Clone & configure

```bash
git clone <your-repo-url>
cd scam-shield-app
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:<your-password>@localhost:5432/scamshield
SECRET_KEY=<a-long-random-string>
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
XAI_API_KEY=<your-groq-api-key>
XAI_MODEL=openai/gpt-oss-120b
XAI_BASE_URL=https://api.groq.com/openai/v1
```

### 2. Database

```sql
CREATE DATABASE scamshield;
```

### 3. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python seed.py                 # loads demo scam numbers/links/keywords
uvicorn app.main:app --reload --reload-dir app
```

Backend runs at `http://127.0.0.1:8000` (interactive docs at `/docs`).

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` (or next available port).

---

## 🔌 API Endpoints

### `POST /check`

Check a number, link, or message.

```json
// Request
{
  "input_type": "message",   // "number" | "url" | "message"
  "content": "Aapka KYC expire ho gaya, OTP bhejein"
}

// Response
{
  "verdict": "dangerous",    // "safe" | "suspicious" | "dangerous"
  "score": 85,
  "reasons": ["Urgency बनाने वाली भाषा", "OTP/PIN/password share करने को कहा जा रहा है"],
  "explanation": "...",
  "advice": "..."
}
```

### `POST /report`

Report a scam number/link/message (anonymous, device-based).

```json
// Request
{
  "report_type": "number",
  "content": "9123456789",
  "note": "KYC scam call",
  "device_id": "dev_xxxxxxxxx"
}

// Response
{
  "id": 3,
  "status": "verified",      // "pending" until 3+ reports, then "verified"
  "message": "धन्यवाद! ..."
}
```

Both endpoints are rate-limited (`/check`: 10/min, `/report`: 5/min per IP).

---

## 🧪 Testing

The detection engine has been manually validated against real-world scam patterns, including:

- Digital arrest / fake police threats
- Fake bank KYC / phishing links
- Lottery & prize scams
- Family emergency ("send money urgently") scams
- Fake job offers
- **False-positive checks:** casual safe messages and genuine bank OTP SMS correctly marked `safe`

---

## 🗺️ Roadmap

- [ ] Family alerts — notify a trusted contact on a `dangerous` verdict
- [ ] WhatsApp / SMS bot integration
- [ ] More Indian languages (Tamil, Telugu, Bengali, Marathi)
- [ ] Optional opt-in login for shared family dashboard
- [ ] Partnerships with NGOs, banks, telecom operators, and the national 1930 cybercrime helpline

---

## 🔒 Security Notes

- No personal data is required to use or report on ScamShield.
- Reports are tied to an anonymous, locally-generated device ID — not to any personal identity.
- URLs and phone numbers are stored as SHA-256 hashes where used for matching.
- API keys and secrets are loaded from `.env` and are never committed to version control (`.gitignore` included).

---

## 👥 Team

**Team ScamShield**
[Your Name] · [Email / Phone]

---

## 📄 License

[Add your license here, e.g. MIT]