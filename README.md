# 🔍 FactCheck Agent

An AI-powered web app that extracts verifiable claims from any PDF and checks each one using Groq's Llama 3.3 — completely free, no credit card required.

## Live Demo
👉 **https://webpirates01-factchecker-cc-app-pg5xxh.streamlit.app/**

## How It Works
1. User uploads a PDF document
2. Groq (Llama 3.3 70B) extracts all verifiable claims — stats, dates, figures, named facts
3. Each claim is individually evaluated against the model's knowledge
4. Every claim is labeled: **Verified / Inaccurate / False / Unverifiable**
5. A color-coded report is displayed with explanations, correct facts, and sources
6. Full report downloadable as JSON

## Tech Stack
| Layer | Tool |
|-------|------|
| Frontend | Streamlit |
| PDF Parsing | pdfplumber |
| Claim Extraction & Verification | Groq API · Llama 3.3 70B |
| Deployment | Streamlit Cloud |

## Setup (Local)

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/Factchecker_CC.git
cd Factchecker_CC
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. API Key
Get your free Groq key (no credit card, 14,400 req/day):
- Groq: https://console.groq.com

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_..."
```

Or just paste your key directly in the sidebar when the app opens.

### 4. Run
```bash
streamlit run app.py
```

## Project Structure
```
Factchecker_CC/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .streamlit/
    └── secrets.toml    # Local secrets (gitignored)
```

## Requirements
```
streamlit==1.35.0
pdfplumber==0.11.0
requests==2.31.0
```

## Verdict Types
| Verdict | Meaning |
|---------|---------|
| ✅ Verified | Evidence clearly confirms the claim |
| ⚠️ Inaccurate | Directionally right but figures/dates are wrong or outdated |
| ❌ False | Evidence directly contradicts the claim |
| ❓ Unverifiable | Insufficient evidence found to judge |

## Why This Catches "Trap Documents"
- Targets precise numerical claims, dates, and statistics — the most common places fabricated facts hide
- Each claim is verified independently with a focused prompt
- Llama 3.3 70B provides explanations and cites the correct fact when a claim is wrong
- Results are color-coded so false claims are immediately visible
