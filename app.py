import streamlit as st
import pdfplumber
import requests
import json
import re

st.set_page_config(page_title="FactCheck Agent", page_icon="🔍", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0C447C 0%, #185FA5 60%, #1a6bb5 100%);
}
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stTextInput input[type="password"] { -webkit-text-fill-color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
    -webkit-text-security: disc !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: rgba(255,255,255,0.5) !important; }
[data-testid="stSidebar"] a { color: #B5D4F4 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }

.stButton > button {
    background: #185FA5; color: white; border: none;
    width: 100%; font-weight: 500; padding: 0.65rem 1rem;
    border-radius: 10px; font-size: 15px; letter-spacing: 0.2px;
    transition: background 0.2s;
}
.stButton > button:hover { background: #0C447C; color: white; }

.page-header {
    background: linear-gradient(135deg, #0C447C 0%, #185FA5 50%, #378ADD 100%);
    border-radius: 16px;
    padding: 2.2rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.page-header-icon {
    width: 56px; height: 56px;
    background: rgba(255,255,255,0.15);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; flex-shrink: 0;
}
.page-header h1 { font-size: 24px; font-weight: 500; color: #fff; margin: 0 0 4px; }
.page-header p  { font-size: 13px; color: #B5D4F4; margin: 0; line-height: 1.5; }

.feat-strip {
    display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 1.25rem;
}
.feat-card {
    background: #E6F1FB; border-radius: 12px;
    padding: 1rem; display: flex; align-items: flex-start; gap: 10px;
}
.feat-icon-wrap {
    width: 34px; height: 34px; background: #185FA5; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}
.feat-title { font-size: 13px; font-weight: 500; color: #0C447C; margin-bottom: 3px; }
.feat-text  { font-size: 12px; color: #185FA5; line-height: 1.5; }

.upload-wrap {
    border: 1.5px dashed #378ADD;
    border-radius: 12px; background: #E6F1FB;
    padding: 0.5rem 1rem 1rem; margin-bottom: 1rem;
}

.metric-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin: 1.2rem 0; }
.metric-box {
    border-radius: 12px; padding: 14px 10px; text-align: center;
}
.metric-box.m-v { background: #EAF3DE; }
.metric-box.m-i { background: #FAEEDA; }
.metric-box.m-f { background: #FCEBEB; }
.metric-box.m-u { background: #F1EFE8; }
.metric-num { font-size: 28px; font-weight: 500; }
.metric-lbl { font-size: 12px; margin-top: 2px; opacity: 0.8; }

.section-title {
    font-size: 15px; font-weight: 500; color: #0C447C;
    border-left: 3px solid #185FA5; padding-left: 10px; margin: 1rem 0 0.75rem;
}

.result-card {
    border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    border-left: 4px solid transparent;
}
.rc-v { background: #EAF3DE; border-left-color: #639922; }
.rc-i { background: #FAEEDA; border-left-color: #BA7517; }
.rc-f { background: #FCEBEB; border-left-color: #E24B4A; }
.rc-u { background: #F1EFE8; border-left-color: #888780; }

.rc-top { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px; }
.rc-claim { flex: 1; font-size: 14px; font-weight: 500; line-height: 1.4; }
.badge { font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; }
.b-v { background: #C0DD97; color: #173404; }
.b-i { background: #FAC775; color: #412402; }
.b-f { background: #F09595; color: #501313; }
.b-u { background: #D3D1C7; color: #2C2C2A; }
.rc-body { font-size: 13px; line-height: 1.5; opacity: 0.85; }
.rc-fact { font-size: 13px; margin-top: 5px; font-weight: 500; }
.rc-src  { font-size: 12px; margin-top: 3px; color: #185FA5; }

.download-wrap .stDownloadButton button {
    background: #185FA5 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    -webkit-text-security: disc !important; font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem'>
      <div style='font-size:32px;margin-bottom:8px'>🔍</div>
      <div style='font-size:17px;font-weight:500;margin-bottom:4px'>FactCheck Agent</div>
      <div style='font-size:12px;opacity:0.75'>Powered by Groq · Llama 3.3</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    api_key = st.text_input("API Key", type="password", placeholder="gsk_••••••••••••••••••••", autocomplete="off")
    st.markdown("[🔑 Get free key at console.groq.com →](https://console.groq.com)")
    st.divider()
    st.markdown("""
    <div style='background:rgba(255,255,255,0.12);border-radius:10px;padding:12px 14px;font-size:12px;line-height:1.8'>
      <b>⚡ Groq free tier</b><br>
      14,400 requests / day<br>
      No credit card required<br>
      Llama 3.3 70B model
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div style='font-size:12px;opacity:0.7;line-height:1.7'>
      <b>How it works</b><br>
      1. Upload your PDF<br>
      2. AI extracts claims<br>
      3. Each claim verified<br>
      4. Download report
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <div class="page-header-icon">🔍</div>
  <div>
    <h1>FactCheck Agent</h1>
    <p>Upload any PDF — AI extracts every verifiable claim and checks each one<br>
    against current knowledge. Get a color-coded truth report instantly.</p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feat-strip">
  <div class="feat-card">
    <div class="feat-icon-wrap">📋</div>
    <div>
      <div class="feat-title">Claim extraction</div>
      <div class="feat-text">Identifies every verifiable statistic, date, and figure.</div>
    </div>
  </div>
  <div class="feat-card">
    <div class="feat-icon-wrap">🤖</div>
    <div>
      <div class="feat-title">AI verification</div>
      <div class="feat-text">Each claim evaluated by Llama 3.3 70B via Groq.</div>
    </div>
  </div>
  <div class="feat-card">
    <div class="feat-icon-wrap">📊</div>
    <div>
      <div class="feat-title">Truth report</div>
      <div class="feat-text">Color-coded results with sources, downloadable JSON.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="upload-wrap">', unsafe_allow_html=True)
uploaded = st.file_uploader("Drop a PDF here or click to browse", type=["pdf"])
st.markdown('</div>', unsafe_allow_html=True)

def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

def groq_call(api_key, messages):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.1, "max_tokens": 2000},
        timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def extract_claims(text, api_key):
    prompt = f"""Extract up to 10 specific, verifiable claims from the text. Focus on:
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
    prompt = f"""You are a fact-checker. Evaluate this claim based on your knowledge:

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

RC   = {"Verified":"rc-v","Inaccurate":"rc-i","False":"rc-f","Unverifiable":"rc-u"}
BC   = {"Verified":"b-v","Inaccurate":"b-i","False":"b-f","Unverifiable":"b-u"}
ICON = {"Verified":"✅","Inaccurate":"⚠️","False":"❌","Unverifiable":"❓"}

if uploaded:
    if st.button("🚀 Run Fact-Check"):
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
            claims = extract_claims(text, api_key)
            st.write(f"Found **{len(claims)}** claims to verify")
            status.update(label=f"🌐 Verifying {len(claims)} claims…")

        results = []
        counters = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverifiable": 0}
        prog = st.progress(0, text="Verifying…")
        for i, item in enumerate(claims, 1):
            v = verify_claim(item.get("claim", ""), api_key)
            results.append((item.get("claim", ""), v))
            k = v.get("status", "Unverifiable")
            if k not in counters:
                k = "Unverifiable"
            counters[k] += 1
            prog.progress(i / len(claims), text=f"Verified {i} of {len(claims)}")
        prog.empty()

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box m-v"><div class="metric-num" style="color:#27500A">{counters['Verified']}</div><div class="metric-lbl" style="color:#3B6D11">✅ Verified</div></div>
          <div class="metric-box m-i"><div class="metric-num" style="color:#633806">{counters['Inaccurate']}</div><div class="metric-lbl" style="color:#854F0B">⚠️ Inaccurate</div></div>
          <div class="metric-box m-f"><div class="metric-num" style="color:#791F1F">{counters['False']}</div><div class="metric-lbl" style="color:#A32D2D">❌ False</div></div>
          <div class="metric-box m-u"><div class="metric-num" style="color:#444441">{counters['Unverifiable']}</div><div class="metric-lbl" style="color:#5F5E5A">❓ Unverifiable</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="section-title">📋 Report — {uploaded.name}</div>', unsafe_allow_html=True)

        for i, (claim, v) in enumerate(results, 1):
            s = v.get("status", "Unverifiable")
            rc = RC.get(s, "rc-u")
            bc = BC.get(s, "b-u")
            icon = ICON.get(s, "❓")
            real = v.get("real_fact", "")
            src  = v.get("source", "")
            real_html = f'<div class="rc-fact">💡 {real}</div>' if s != "Verified" and real and real != "Correct as stated" else ""
            src_html  = f'<div class="rc-src">🔗 {src}</div>' if src else ""
            st.markdown(f"""
            <div class="result-card {rc}">
              <div class="rc-top">
                <span style="font-size:18px">{icon}</span>
                <div class="rc-claim">{claim[:160]}{'…' if len(claim)>160 else ''}</div>
                <span class="badge {bc}">{s}</span>
              </div>
              <div class="rc-body">{v.get('explanation','')}</div>
              {real_html}{src_html}
            </div>
            """, unsafe_allow_html=True)

        report = json.dumps([{"claim": c, **v} for c, v in results], indent=2)
        st.markdown('<div class="download-wrap">', unsafe_allow_html=True)
        st.download_button("⬇️ Download Report (JSON)", data=report, file_name="factcheck_report.json", mime="application/json")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("👆 Upload a PDF above to get started. The agent will extract factual claims and verify each one using Groq's Llama 3.3.")
