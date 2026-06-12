# 🔍 Fact-Check Agent

An AI-powered web app that extracts claims from a PDF and verifies each one against live web data.

## Live Demo
👉 **[https://your-app.streamlit.app](https://your-app.streamlit.app)** *(replace after deploy)*

## How It Works
1. User uploads a PDF
2. Claude extracts verifiable claims (stats, dates, figures)
3. Each claim is searched on the live web via Tavily
4. Claude judges each claim: **Verified / Inaccurate / False / Unverifiable**
5. Full report is displayed with sources + downloadable JSON

## Tech Stack
| Layer | Tool |
|-------|------|
| Frontend | Streamlit |
| PDF Parsing | pdfplumber |
| Claim Extraction | Claude (claude-sonnet-4-6) |
| Web Search | Tavily API |
| Deployment | Streamlit Cloud |

## Setup (Local)

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/fact-checker.git
cd fact-checker
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. API Keys
Get free keys:
- Anthropic: https://console.anthropic.com
- Tavily: https://tavily.com (1000 free searches/month)

Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
TAVILY_API_KEY = "tvly-..."
```

### 4. Run
```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push code to GitHub (don't push secrets.toml — it's gitignored)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your repo → set `app.py` as main file
4. Go to **Advanced settings → Secrets** and paste:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
TAVILY_API_KEY = "tvly-..."
```
5. Click **Deploy** — live in ~2 minutes!

## Project Structure
```
fact-checker/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .streamlit/
    └── secrets.toml    # Local secrets (gitignored)
```

## Evaluation
The app is designed to catch "Trap Documents" with intentional lies by:
- Extracting precise numerical claims, dates, and statistics
- Running targeted web searches for each claim
- Using Claude as a judge with access to real-time evidence
