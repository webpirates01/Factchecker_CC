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
[data-testid="stSidebar"] .stTextInput label { font-size: 15px !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
    border: 1.5px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    padding: 10px 12px !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: rgba(255,255,255,0.45) !important; }
[data-testid="stSidebar"] a { color: #B5D4F4 !important; text-decoration: underline !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }

.stButton > button {
    background: #185FA5; color: white; border: none;
    width: 100%; font-weight: 600; padding: 0.75rem 1rem;
    border-radius: 10px; font-size: 16px; letter-spacing: 0.3px;
}
.stButton > button:hover { background: #0C447C; color: white; }

.page-header {
    background: linear-gradient(135deg, #0C447C 0%, #185FA5 50%, #378ADD 100%);
    border-radius: 18px;
    padding: 2.5rem 2.5rem;
    margin-bottom: 1.75rem;
}
.page-header h1 { font-size: 34px; font-weight: 600; color: #fff; margin: 0 0 10px; }
.page-header p  { font-size: 16px; color: #C8DFF5; margin: 0; line-height: 1.6; max-width: 620px; }

.how-it-works {
    background: #E6F1FB;
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.75rem;
}
.how-title { font-size: 20px; font-weight: 600; color: #0C447C; margin-bottom: 1rem; }
.steps-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; }
.step {
    background: #fff;
    border-radius: 10px;
    padding: 14px;
    border-left: 4px solid #185FA5;
}
.step-num { font-size: 11px; font-weight: 600; color: #185FA5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.step-title { font-size: 14px; font-weight: 600; color: #0C447C; margin-bottom: 4px; }
.step-text { font-size: 12px; color: #185FA5; line-height: 1.5; }

.feat-strip {
    display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 1.75rem;
}
.feat-card {
    background: #E6F1FB; border-radius: 14px;
    padding: 1.2rem 1.2rem; display: flex; align-items: flex-start; gap: 12px;
}
.feat-icon-wrap {
    width: 40px; height: 40px; background: #185FA5; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.feat-title { font-size: 15px; font-weight: 600; color: #0C447C; margin-bottom: 4px; }
.feat-text  { font-size: 13px; color: #185FA5; line-height: 1.5; }

.upload-wrap {
    border: 2px dashed #378ADD;
    border-radius: 14px; background: #EBF4FC;
    padding: 0.75rem 1.25rem 1.25rem; margin-bottom: 1.25rem;
}
.upload-label { font-size: 15px; font-weight: 500; color: #0C447C; margin-bottom: 8px; }

.metric-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin: 1.5rem 0; }
.metric-box { border-radius: 14px; padding: 18px 12px; text-align: center; }
.metric-box.m-v { background: #D4EDBE; }
.metric-box.m-i { background: #FAE0B0; }
.metric-box.m-f { background: #F5C0C0; }
.metric-box.m-u { background: #E5E3D8; }
.metric-num { font-size: 36px; font-weight: 600; }
.metric-lbl { font-size: 13px; margin-top: 4px; font-weight: 500; }

.section-title {
    font-size: 20px; font-weight: 600; color: #0C447C;
    border-left: 4px solid #185FA5; padding-left: 12px; margin: 1.25rem 0 1rem;
}

.result-card {
    border-radius: 14px; padding: 18px 20px; margin-bottom: 12px;
    border-left: 5px solid transparent;
}
.rc-v { background: #EAF3DE; border-left-color: #4A8A1A; }
.rc-i { background: #FAEEDA; border-left-color: #BA7517; }
.rc-f { background: #FCEBEB; border-left-color: #D03030; }
.rc-u { background: #F1EFE8; border-left-color: #888780; }

.rc-top { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.rc-num { font-size: 13px; font-weight: 600; color: #888; min-width: 24px; padding-top: 2px; }
.rc-claim { flex: 1; font-size: 15px; font-weight: 600; line-height: 1.5; }
.badge { font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; }
.b-v { background: #B0D98A; color: #173404; }
.b-i { background: #FAC775; color: #412402; }
.b-f { background: #EF9090; color: #501313; }
.b-u { background: #C8C6BC; color: #2C2C2A; }
.rc-body { font-size: 14px; line-height: 1.6; color: #333; padding-left: 36px; }
.rc-fact { font-size: 14px; margin-top: 6px; font-weight: 600; color: #0C447C; padding-left: 36px; }
.rc-src  { font-size: 13px; margin-top: 4px; color: #185FA5; padding-left: 36px; }

.scroll-top-btn {
    position: fixed; bottom: 28px; right: 28px; z-index: 999;
    background: #185FA5; color: #fff; border: none; border-radius: 50%;
    width: 48px; height: 48px; font-size: 22px; cursor: pointer;
    box-shadow: 0 4px 16px rgba(24,95,165,0.35);
    display: flex; align-items: center; justify-content: center;
}
</style>

<script>
function scrollToResults() {
    const el = document.getElementById('results-anchor');
    if (el) el.scrollIntoView({behavior: 'smooth'});
}
function scrollToTop() {
    window.scrollTo({top: 0, behavior: 'smooth'});
}
</script>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.25rem 0 0.75rem'>
      <div style='font-size:38px;margin-bottom:10px'>🔍</div>
      <div style='font-size:20px;font-weight:600;margin-bottom:4px'>FactCheck Agent</div>
      <div style='font-size:13px;opacity:0.75'>Powered by Groq · Llama 3.3</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    api_key = st.text_input("API Key", type="password", placeholder="Enter your API key…", autocomplete="one-time-code")
    st.markdown("[🔑 Get your free API key →](https://console.groq.com)")
    st.divider()
    st.markdown("""
    <div style='background:rgba(255,255,255,0.12);border-radius:10px;padding:14px 16px;font-size:13px;line-height:2'>
      <b>⚡ Free tier</b><br>
      14,400 requests / day via Groq<br>
      No credit card required
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>🔍 FactCheck Agent</h1>
  <p>Upload any PDF document — our AI reads every verifiable claim and tells you
  what's true, what's wrong, and what's outright false. Get a full color-coded report in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="how-it-works">
  <div class="how-title">⚙️ How it works</div>
  <div class="steps-grid">
    <div class="step">
      <div class="step-num">Step 1</div>
      <div class="step-title">📄 Upload PDF</div>
      <div class="step-text">Drop any PDF — reports, articles, research papers, or news.</div>
    </div>
    <div class="step">
      <div class="step-num">Step 2</div>
      <div class="step-title">🧠 Extract claims</div>
      <div class="step-text">AI identifies every verifiable statistic, date, figure, and named fact.</div>
    </div>
    <div class="step">
      <div class="step-num">Step 3</div>
      <div class="step-title">🤖 Verify each claim</div>
      <div class="step-text">Each claim is individually evaluated and labeled with a verdict.</div>
    </div>
    <div class="step">
      <div class="step-num">Step 4</div>
      <div class="step-title">📊 Truth report</div>
      <div class="step-text">Color-coded results with explanations, correct facts, and sources.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Feature cards ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="feat-strip">
  <div class="feat-card">
    <div class="feat-icon-wrap">📋</div>
    <div>
      <div class="feat-title">Claim extraction</div>
      <div class="feat-text">Pinpoints every verifiable statistic, date, and figure automatically.</div>
    </div>
  </div>
  <div class="feat-card">
    <div class="feat-icon-wrap">🤖</div>
    <div>
      <div class="feat-title">AI verification</div>
      <div class="feat-text">Each claim evaluated by Llama 3.3 70B via Groq — fast and free.</div>
    </div>
  </div>
  <div class="feat-card">
    <div class="feat-icon-wrap">📊</div>
    <div>
      <div class="feat-title">Truth report</div>
      <div class="feat-text">Color-coded results with sources and downloadable JSON report.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown('<div class="upload-wrap"><div class="upload-label">📁 Upload your PDF document</div>', unsafe_allow_html=True)
uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

def groq_call(key, messages):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.1, "max_tokens": 2000},
        timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def extract_claims(text, key):
    prompt = f"""Extract up to 10 specific, verifiable claims from the text. Focus on:
- Statistics and percentages
- Dates and years
- Financial figures (revenue, valuations, funding)
- Named facts and technical claims

Return ONLY a valid JSON array. Each element:
  "claim": exact claim from the text
  "search_query": 5-8 word query to verify it

TEXT:
\"\"\"{text[:5000]}\"\"\"

Return ONLY the JSON array."""
    raw = groq_call(key, [{"role": "user", "content": prompt}])
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(raw)

def verify_claim(claim, key):
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
        raw = groq_call(key, [{"role": "user", "content": prompt}])
        raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception as e:
        return {"status": "Unverifiable", "explanation": f"Verification failed: {e}", "real_fact": "N/A", "source": ""}

RC   = {"Verified":"rc-v","Inaccurate":"rc-i","False":"rc-f","Unverifiable":"rc-u"}
BC   = {"Verified":"b-v","Inaccurate":"b-i","False":"b-f","Unverifiable":"b-u"}
ICON = {"Verified":"✅","Inaccurate":"⚠️","False":"❌","Unverifiable":"❓"}

# ── Run ───────────────────────────────────────────────────────────────────────
if uploaded:
    if st.button("🚀 Run Fact-Check", use_container_width=True):
        if not api_key:
            st.error("Please enter your API key in the sidebar.")
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
            if k not in counters: k = "Unverifiable"
            counters[k] += 1
            prog.progress(i / len(claims), text=f"Verified {i} of {len(claims)}")
        prog.empty()

        # Auto-scroll + back to top button
        st.markdown("""
        <div id="results-anchor"></div>
        <script>
          setTimeout(function(){
            var el = window.parent.document.querySelector('.main');
            if(el) el.scrollTo({top: el.scrollHeight, behavior: 'smooth'});
          }, 400);
        </script>
        """, unsafe_allow_html=True)
        


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
            s    = v.get("status", "Unverifiable")
            rc   = RC.get(s, "rc-u")
            bc   = BC.get(s, "b-u")
            icon = ICON.get(s, "❓")
            real = v.get("real_fact", "")
            src  = v.get("source", "")
            real_html = f'<div class="rc-fact">💡 Correct fact: {real}</div>' if s != "Verified" and real and real != "Correct as stated" else ""
            src_html  = f'<div class="rc-src">🔗 {src}</div>' if src else ""
            st.markdown(f"""
            <div class="result-card {rc}">
              <div class="rc-top">
                <div class="rc-num">#{i}</div>
                <div class="rc-claim">{claim[:180]}{'…' if len(claim)>180 else ''}</div>
                <span class="badge {bc}">{icon} {s}</span>
              </div>
              <div class="rc-body">{v.get('explanation','')}</div>
              {real_html}{src_html}
            </div>
            """, unsafe_allow_html=True)

        report = json.dumps([{"claim": c, **v} for c, v in results], indent=2)
        st.download_button("⬇️ Download Full Report (JSON)", data=report, file_name="factcheck_report.json", mime="application/json", use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬆️ Back to Top", key="scroll_top", use_container_width=True):
            st.markdown('''<script>
              window.parent.document.querySelector('section[data-testid="stMain"] .main').scrollTo({top:0,behavior:'smooth'});
              window.parent.scrollTo({top:0,behavior:'smooth'});
            </script>''', unsafe_allow_html=True)

else:
    st.info("👆 Upload a PDF above to get started — the agent will extract every factual claim and verify each one.")
