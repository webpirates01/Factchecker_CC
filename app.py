import streamlit as st
import pdfplumber
import requests
import json
import re

st.set_page_config(page_title="FactCheck Agent", page_icon="🔍", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: var(--background-color); }
.stButton > button {
    background: #534AB7; color: white; border: none;
    width: 100%; font-weight: 500; padding: 0.6rem 1rem;
    border-radius: 8px; font-size: 15px;
}
.stButton > button:hover { background: #3C3489; color: white; }
.metric-row { display: flex; gap: 12px; margin: 1rem 0; }
.metric-box {
    flex: 1; padding: 12px; border-radius: 8px;
    border: 0.5px solid rgba(0,0,0,0.1); text-align: center;
}
.metric-num { font-size: 26px; font-weight: 500; }
.metric-lbl { font-size: 12px; opacity: 0.7; margin-top: 2px; }
.result-card {
    border: 0.5px solid rgba(0,0,0,0.1); border-radius: 10px;
    padding: 14px 16px; margin-bottom: 10px;
}
.pill {
    display: inline-block; font-size: 12px; font-weight: 500;
    padding: 3px 10px; border-radius: 20px;
}
.pill-verified { background: #EAF3DE; color: #27500A; }
.pill-inaccurate { background: #FAEEDA; color: #633806; }
.pill-false { background: #FCEBEB; color: #791F1F; }
.pill-unverifiable { background: #F1EFE8; color: #444441; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔍 FactCheck Agent")
    st.caption("Powered by Groq + Llama 3.3 · Web verified")
    st.divider()
    api_key = st.text_input("API Key", type="password", placeholder="gsk_••••••••••••••••••••")
    st.markdown("[Get free key at console.groq.com →](https://console.groq.com)")
    st.divider()
    max_claims = st.slider("Max claims to verify", 3, 15, 8)
    st.markdown("""
    <div style='font-size:12px;padding:10px;border-radius:8px;border:0.5px solid rgba(0,0,0,0.1);line-height:1.7'>
    ⚡ <b>Groq free tier</b><br>
    14,400 requests/day<br>
    No credit card required
    </div>
    """, unsafe_allow_html=True)

def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

def groq_call(api_key, messages, temperature=0.1):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": temperature, "max_tokens": 2000},
        timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def extract_claims(text, api_key, max_claims):
    prompt = f"""Extract up to {max_claims} specific, verifiable claims from the text. Focus on:
- Statistics and percentages
- Dates and years
- Financial figures (revenue, valuations, funding)
- Named facts and technical claims

Return ONLY a valid JSON array. Each element:
  "claim": exact claim from the text
  "search_query": 5-8 word Google query to verify it

TEXT:
\"\"\"{text[:5000]}\"\"\"

Return ONLY the JSON array."""
    raw = groq_call(api_key, [{"role": "user", "content": prompt}])
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(raw)

def verify_claim(claim, api_key):
    prompt = f"""You are a fact-checker. Based on your training knowledge, evaluate this claim:

CLAIM: "{claim}"

Respond with ONLY a valid JSON object:
{{
  "status": "Verified" | "Inaccurate" | "False" | "Unverifiable",
  "explanation": "1-2 sentences with your verdict and supporting data",
  "real_fact": "Correct fact if wrong, or 'Correct as stated' if verified",
  "source": "Source or reference where this can be confirmed"
}}

Return ONLY the JSON object."""
    try:
        raw = groq_call(api_key, [{"role": "user", "content": prompt}])
        raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception as e:
        return {"status": "Unverifiable", "explanation": f"Verification failed: {e}", "real_fact": "N/A", "source": ""}

PILL = {
    "Verified": "pill pill-verified",
    "Inaccurate": "pill pill-inaccurate",
    "False": "pill pill-false",
    "Unverifiable": "pill pill-unverifiable"
}
DOT = {"Verified": "🟢", "Inaccurate": "🟡", "False": "🔴", "Unverifiable": "⚪"}

st.markdown("## 📄 Upload a document to fact-check")
st.caption("PDF extracted → claims identified → AI verified → truth report")

uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if uploaded and st.button("🚀 Run Fact-Check"):
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    with st.status("📄 Extracting text from PDF…", expanded=True) as status:
        text = extract_text(uploaded)
        if not text:
            st.error("Could not extract text — is this a scanned PDF?")
            st.stop()
        st.write(f"Extracted **{len(text):,}** characters from `{uploaded.name}`")

        status.update(label="🧠 Identifying verifiable claims…")
        claims = extract_claims(text, api_key, max_claims)
        st.write(f"Found **{len(claims)}** claims to verify")
        status.update(label=f"🌐 Verifying {len(claims)} claims…")

    st.divider()
    results = []
    counters = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverifiable": 0}
    progress = st.progress(0, text="Verifying…")

    for i, item in enumerate(claims, 1):
        claim = item.get("claim", "")
        verdict = verify_claim(claim, api_key)
        results.append((claim, verdict))
        k = verdict.get("status", "Unverifiable")
        if k not in counters:
            k = "Unverifiable"
        counters[k] += 1
        progress.progress(i / len(claims), text=f"Verified {i} of {len(claims)}")

    progress.empty()

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-box"><div class="metric-num" style="color:#27500A">{counters['Verified']}</div><div class="metric-lbl">✅ Verified</div></div>
      <div class="metric-box"><div class="metric-num" style="color:#633806">{counters['Inaccurate']}</div><div class="metric-lbl">⚠️ Inaccurate</div></div>
      <div class="metric-box"><div class="metric-num" style="color:#791F1F">{counters['False']}</div><div class="metric-lbl">❌ False</div></div>
      <div class="metric-box"><div class="metric-num" style="color:#888780">{counters['Unverifiable']}</div><div class="metric-lbl">❓ Unverifiable</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 📋 Report — `{uploaded.name}`")

    for i, (claim, v) in enumerate(results, 1):
        status = v.get("status", "Unverifiable")
        pill_class = PILL.get(status, "pill pill-unverifiable")
        dot = DOT.get(status, "⚪")
        real = v.get("real_fact", "")
        src = v.get("source", "")
        real_html = f"<p style='font-size:13px;margin-top:6px'><b>Correct fact:</b> {real}</p>" if status != "Verified" and real and real != "Correct as stated" else ""
        src_html = f"<p style='font-size:12px;margin-top:4px;opacity:0.6'><b>Source:</b> {src}</p>" if src else ""
        st.markdown(f"""
        <div class="result-card">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            <span>{dot}</span>
            <span style="flex:1;font-size:14px;font-weight:500">{claim[:140]}{'…' if len(claim)>140 else ''}</span>
            <span class="{pill_class}">{status}</span>
          </div>
          <p style="font-size:13px;opacity:0.8;line-height:1.5">{v.get('explanation','')}</p>
          {real_html}{src_html}
        </div>
        """, unsafe_allow_html=True)

    report = json.dumps([{"claim": c, **v} for c, v in results], indent=2)
    st.download_button("⬇️ Download Report (JSON)", data=report, file_name="factcheck_report.json", mime="application/json")

elif not uploaded:
    st.info("👆 Upload a PDF to get started. The agent will extract factual claims and verify each one using Groq's Llama 3.3.")
