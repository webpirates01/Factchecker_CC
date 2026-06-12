import streamlit as st
import pdfplumber
import google.generativeai as genai
import json
import re

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactCheck Agent",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Fact-Check Agent")
st.caption("Upload a PDF → AI extracts claims → Google-powered verification → Truth report")

# ── Sidebar: API keys ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔑 API Key")
    gemini_key = st.text_input(
        "Google Gemini API Key", type="password",
        value=st.secrets.get("GEMINI_API_KEY") or ""
    )
    st.markdown("Get free key at [Google AI Studio](https://aistudio.google.com/apikey)")
    st.divider()
    max_claims = st.slider("Max claims to verify", 3, 15, 8)
    st.info("Gemini free tier: 1500 requests/day")

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from uploaded PDF."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_claims(text: str, model, max_claims: int) -> list[dict]:
    """Use Gemini to pull out verifiable factual claims."""
    prompt = f"""You are a fact-checking assistant. From the text below, extract up to {max_claims} specific, verifiable claims. Focus on:
- Statistics and percentages
- Named dates and years
- Financial figures (revenue, valuations, funding)
- Scientific or technical facts

Return ONLY a valid JSON array. Each element must have:
  "claim": the exact claim as stated in the text
  "search_query": a short Google search query to verify it (5-8 words)

TEXT:
\"\"\"{text[:6000]}\"\"\"

Return ONLY the JSON array, no markdown, no explanation."""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


def verify_claim(claim: str, search_query: str, model_with_search) -> dict:
    """Search the web using Gemini's built-in Google Search tool and evaluate the claim."""
    prompt = f"""You are a fact-checker with access to Google Search.

Search the web for: "{search_query}"

Then evaluate this claim: "{claim}"

Based on what you find, respond with ONLY a valid JSON object:
{{
  "status": "Verified" | "Inaccurate" | "False" | "Unverifiable",
  "explanation": "1-2 sentences explaining your verdict with actual data found",
  "real_fact": "The correct fact if claim is wrong, or 'Correct as stated' if verified",
  "source": "URL or source name where you found the info"
}}

Definitions:
- Verified: evidence clearly confirms the claim
- Inaccurate: directionally right but figures/dates are wrong or outdated
- False: evidence contradicts the claim
- Unverifiable: insufficient evidence found

Return ONLY the JSON object."""

    try:
        response = model_with_search.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "status": "Unverifiable",
            "explanation": f"Verification failed: {e}",
            "real_fact": "N/A",
            "source": ""
        }


STATUS_EMOJI = {"Verified": "✅", "Inaccurate": "⚠️", "False": "❌", "Unverifiable": "❓"}
STATUS_COLOR = {"Verified": "green", "Inaccurate": "orange", "False": "red", "Unverifiable": "gray"}


def render_result(i: int, claim: str, verdict: dict):
    status = verdict.get("status", "Unverifiable")
    emoji = STATUS_EMOJI.get(status, "❓")
    color = STATUS_COLOR.get(status, "gray")
    with st.expander(f"{emoji} **Claim {i}:** {claim[:120]}{'…' if len(claim) > 120 else ''}", expanded=True):
        st.markdown(f"**Status:** :{color}[**{status}**]")
        st.markdown(f"**Explanation:** {verdict.get('explanation', '')}")
        if status != "Verified":
            st.markdown(f"**Real Fact:** {verdict.get('real_fact', '')}")
        src = verdict.get("source", "")
        if src:
            st.markdown(f"**Source:** {src}")


# ── Main UI ───────────────────────────────────────────────────────────────────

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file and st.button("🚀 Run Fact-Check", type="primary"):

    if not gemini_key:
        st.error("Please enter your Gemini API key in the sidebar.")
        st.stop()

    # Init Gemini
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # FIXED Syntax for search tools initialization
    model_with_search = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools={"google_search": {}}
    )

    # Step 1 — Extract PDF text
    with st.status("📄 Extracting text from PDF…", expanded=True) as status:
        pdf_text = extract_text_from_pdf(uploaded_file)
        if not pdf_text:
            st.error("Could not extract text. Is this a scanned/image PDF?")
            st.stop()
        st.write(f"Extracted {len(pdf_text):,} characters from {uploaded_file.name}")

        # Step 2 — Extract claims
        status.update(label="🧠 Identifying verifiable claims…")
        claims = extract_claims(pdf_text, model, max_claims)
        st.write(f"Found **{len(claims)}** claims to verify")
        status.update(label=f"🌐 Verifying {len(claims)} claims via Google Search…")

    st.divider()
    st.subheader(f"📋 Fact-Check Report — {uploaded_file.name}")

    results = []
    counters = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverifiable": 0}
    progress = st.progress(0, text="Verifying claims…")

    for i, item in enumerate(claims, 1):
        claim = item.get("claim", "")
        query = item.get("search_query", claim)
        verdict = verify_claim(claim, query, model_with_search)
        results.append((claim, verdict))
        
        key = verdict.get("status", "Unverifiable")
        if key not in counters:
            key = "Unverifiable"
        counters[key] += 1
        progress.progress(i / len(claims), text=f"Verified {i}/{len(claims)}")

    progress.empty()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✅ Verified", counters["Verified"])
    col2.metric("⚠️ Inaccurate", counters["Inaccurate"])
    col3.metric("❌ False", counters["False"])
    col4.metric("❓ Unverifiable", counters["Unverifiable"])
    st.divider()

    for i, (claim, verdict) in enumerate(results, 1):
        render_result(i, claim, verdict)

    report_json = json.dumps([{"claim": c, **v} for c, v in results], indent=2)
    st.download_button("⬇️ Download Report (JSON)", data=report_json, file_name="factcheck_report.json", mime="application/json")

elif not uploaded_file:
    st.info("👆 Upload a PDF to get started. The agent will extract factual claims and verify each one via Google Search.")