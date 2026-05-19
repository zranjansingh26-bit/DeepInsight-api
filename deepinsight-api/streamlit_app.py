import streamlit as st

st.set_page_config(
    page_title="DeepInsight | AI Analytics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
import httpx
import plotly.graph_objects as go
import plotly.express as px
import json
import time
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────

API_BASE_URL = st.sidebar.text_input("API Base URL", value="http://localhost:8000")
AUTH_TOKEN = st.sidebar.text_input("Auth Token (Optional)", value="", type="password")

# ── Custom CSS ────────────────────────────────────────────────

st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton>button {
        background-color: #6366f1;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4f46e5;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        transform: translateY(-1px);
    }
    .stMetric {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    .stFileUploader {
        border: 2px dashed #4f46e5;
        border-radius: 12px;
        background-color: #1e293b;
        padding: 1rem;
    }
    div[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    h1, h2, h3 {
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    .status-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 16px;
        border-left: 5px solid #6366f1;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #334155;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #6366f1;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────

def get_headers():
    headers = {}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    return headers

def check_health():
    try:
        response = httpx.get(f"{API_BASE_URL}/health", timeout=5.0)
        return response.status_code == 200
    except:
        return False

def show_api_error(prefix: str, resp):
    try:
        data = resp.json()
        if isinstance(data, dict) and "detail" in data:
            st.error(f"❌ {prefix}: {data['detail']}")
        else:
            st.error(f"❌ {prefix}: {resp.text}")
    except Exception:
        st.error(f"❌ {prefix}: {resp.text}")

# ── State Management ──────────────────────────────────────────

if "dataset_id" not in st.session_state:
    st.session_state["dataset_id"] = None
if "dataset_meta" not in st.session_state:
    st.session_state["dataset_meta"] = None

# ── Header ────────────────────────────────────────────────────

col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
with col2:
    st.title("DeepInsight Starter Suite")
    st.caption("AI-Powered Analytics Dashboard")

# ── Sidebar Status ────────────────────────────────────────────

st.sidebar.markdown("### System Status")
is_healthy = check_health()
if is_healthy:
    st.sidebar.success("API Connected")
else:
    st.sidebar.error("API Disconnected")

# ── Main Content ──────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📤 Upload", "📊 Overview", "🤖 AI Chat", "🧪 Model Comparison Lab", 
    "📈 Time Series Forecast", "🚨 Anomaly Detection"
])

# ── Tab 1: Upload ─────────────────────────────────────────────

with tab1:
    st.markdown('<div class="status-card"><h2>Upload New Dataset</h2><p>Upload a CSV, XLSX, or JSON file to begin your AI-powered analysis.</p></div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"])
    
    if uploaded_file is not None:
        if st.button("Start Processing"):
            with st.spinner("Analyzing data and uploading to storage..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    response = httpx.post(
                        f"{API_BASE_URL}/api/datasets/upload",
                        headers=get_headers(),
                        files=files,
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        meta = response.json()
                        st.session_state["dataset_meta"] = meta
                        st.session_state["dataset_id"] = meta["id"]
                        st.success(f"Successfully processed {uploaded_file.name}!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {str(e)}")

# ── Tab 2: Overview ───────────────────────────────────────────

with tab2:
    st.markdown("### 📊 Dataset Overview")
    
    # Dataset Selector
    try:
        resp_list = httpx.get(f"{API_BASE_URL}/api/datasets/", headers=get_headers())
        if resp_list.status_code == 200:
            datasets = resp_list.json()
            if datasets:
                ds_options = {f"{d['file_name']} ({d['id'][:8]})": d['id'] for d in datasets}
                # Default index logic: find current ID in list
                current_id = st.session_state.get("dataset_id")
                opt_list = ["-- Select Dataset --"] + list(ds_options.keys())
                
                selected_ds_label = st.selectbox(
                    "Load an existing dataset:",
                    options=opt_list,
                    index=0 if not current_id else (opt_list.index(next((k for k, v in ds_options.items() if v == current_id), opt_list[0])) if any(v == current_id for v in ds_options.values()) else 0)
                )
                
                if selected_ds_label != "-- Select Dataset --":
                    selected_id = ds_options[selected_ds_label]
                    if st.session_state.get("dataset_id") != selected_id:
                        st.session_state["dataset_id"] = selected_id
                        # Fetch details
                        resp_det = httpx.get(f"{API_BASE_URL}/api/datasets/{selected_id}", headers=get_headers())
                        if resp_det.status_code == 200:
                            st.session_state["dataset_meta"] = resp_det.json()
                            st.rerun()
    except Exception as e:
        st.warning(f"Could not fetch dataset list: {e}")

    dataset_id = st.session_state.get("dataset_id")
    if not dataset_id:
        st.info("No dataset uploaded yet. Please go to the Upload tab.")
    else:
        meta = st.session_state.dataset_meta
        
        st.markdown(f"### Dataset: `{meta['file_name']}`")
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", f"{meta['row_count']:,}")
        m2.metric("Columns", f"{meta['column_count']}")
        m3.metric("Quality Score", f"{meta['quality_score']}%")
        m4.metric("Null %", f"{meta['null_percentage']}%")
        
        # Column Details
        st.markdown("---")
        st.markdown("### Column Metadata")
        cols_df = pd.DataFrame(meta["columns"])
        
        # Convert list columns to string for better display and Arrow compatibility
        if "sample_values" in cols_df.columns:
            cols_df["sample_values"] = cols_df["sample_values"].apply(lambda x: ", ".join(map(str, x)) if isinstance(x, list) else str(x))
            
        st.dataframe(cols_df, use_container_width=True)
        
        # Action Buttons
        st.markdown("### Run Advanced Analysis")
        
        analysis_options = {
            "Descriptive Statistics": "descriptive_stats",
            "Correlation Matrix": "correlation",
            "Distribution Analysis": "distribution",
            "Bar Charts (Categorical)": "bar",
            "Pie Charts (Categorical)": "pie",
        }
        
        selected_types = st.multiselect(
            "Select analysis types to generate:",
            options=list(analysis_options.keys()),
            default=["Descriptive Statistics", "Distribution Analysis"]
        )
        
        if st.button("Generate Selected Analysis"):
            if not selected_types:
                st.warning("Please select at least one analysis type.")
            else:
                with st.spinner("Generating insights and charts..."):
                    types_to_run = [analysis_options[t] for t in selected_types]
                    try:
                        resp = httpx.post(
                            f"{API_BASE_URL}/api/analysis/run/{st.session_state.dataset_id}",
                            headers=get_headers(),
                            json={"analysis_types": types_to_run},
                            timeout=120.0
                        )
                        
                        if resp.status_code == 200:
                            st.success("Analysis complete!")
                            analysis_data = resp.json()
                            
                            # Render results for each analysis
                            for analysis in analysis_data.get("analyses", []):
                                with st.expander(f"Analysis: {analysis['analysis_type'].replace('_', ' ').title()}", expanded=True):
                                    # Show insights
                                    if analysis["results"].get("insights"):
                                        st.markdown("#### Key Insights")
                                        for insight in analysis["results"]["insights"]:
                                            st.info(insight)
                                    
                                    # Render charts
                                    for chart in analysis.get("charts", []):
                                        st.markdown(f"#### {chart['title']}")
                                        try:
                                            # Plotly figure data is in chart['data']
                                            fig_dict = chart["data"]
                                            st.plotly_chart(fig_dict, use_container_width=True)
                                        except Exception as e:
                                            st.error(f"Could not render chart: {str(e)}")
                                    
                                    # Show detailed data in JSON
                                    if st.checkbox("Show Raw Data", key=f"raw_{analysis['analysis_type']}"):
                                        st.json(analysis["results"])
                        else:
                            show_api_error("Analysis failed", resp)
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")

# ── Tab 3: AI Chat ────────────────────────────────────────────

# Speech-to-Text: compact mic button that injects text into chat input
SPEECH_TO_TEXT_HTML = """
<div id="stt">
  <button id="mb" onclick="toggle()">
    <svg id="mi" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
  </button>
  <span id="st">🎤 Click to speak</span>
  <span id="dots"></span>
  <span id="pv"></span>
</div>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:transparent;overflow:hidden;height:100%}
#stt{
  display:flex;align-items:center;gap:10px;
  padding:6px 14px;height:42px;
  background:rgba(15,23,42,0.9);
  border-radius:24px;border:1px solid #334155;
  font-family:Inter,-apple-system,system-ui,sans-serif;
  width:fit-content;margin:0 auto;
}
#mb{
  width:32px;height:32px;min-width:32px;
  border-radius:50%;border:2px solid #6366f1;
  background:rgba(99,102,241,0.1);
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:all 0.3s;
}
#mb:hover{background:rgba(99,102,241,0.25);transform:scale(1.1)}
#mb.on{background:rgba(239,68,68,0.15);border-color:#ef4444;animation:glow 1.5s infinite}
#mb svg{width:16px;height:16px;fill:#a5b4fc;transition:fill 0.3s}
#mb.on svg{fill:#ef4444}
@keyframes glow{
  0%{box-shadow:0 0 0 0 rgba(239,68,68,0.4)}
  70%{box-shadow:0 0 0 10px rgba(239,68,68,0)}
  100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}
}
#st{font-size:12px;color:#94a3b8;white-space:nowrap}
#st.ok{color:#34d399}
#st.err{color:#f87171}
#st.on{color:#e2e8f0}
#dots{display:none}
#dots.on{display:inline-flex;gap:3px;align-items:center}
#dots .d{width:4px;height:4px;background:#ef4444;border-radius:50%;animation:b 1.4s infinite both}
#dots .d:nth-child(2){animation-delay:.16s}
#dots .d:nth-child(3){animation-delay:.32s}
@keyframes b{0%,80%,100%{transform:scale(0)}40%{transform:scale(1)}}
#pv{font-size:11px;color:#cbd5e1;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:none}
#pv.on{display:inline}
</style>
<script>
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
const mb=document.getElementById('mb'),st=document.getElementById('st');
const dots=document.getElementById('dots'),pv=document.getElementById('pv');
let rec,on=false,tid;

if(!SR){st.textContent='⚠ Not supported in this browser';st.className='err';mb.style.opacity='.4';mb.style.cursor='not-allowed'}

function inject(t){
  try{
    const ta=window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
    if(!ta){st.textContent='⚠ Chat input not found';st.className='err';return}
    const s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
    s.call(ta,t);ta.dispatchEvent(new Event('input',{bubbles:true}));ta.focus();
    st.textContent='✅ Press Enter to send';st.className='ok';
    clearTimeout(tid);tid=setTimeout(()=>{st.textContent='🎤 Click to speak';st.className='';},3500);
  }catch(e){st.textContent='⚠ Insert failed';st.className='err'}
}

function toggle(){
  if(!SR)return;
  if(on){rec.stop();return}
  rec=new SR();rec.continuous=false;rec.interimResults=true;rec.lang='en-US';
  rec.onstart=()=>{
    on=true;mb.className='on';st.textContent='Listening...';st.className='on';
    dots.className='on';dots.innerHTML='<span class="d"></span><span class="d"></span><span class="d"></span>';
    pv.className='on';pv.textContent='';
  };
  rec.onresult=(e)=>{
    let f='',im='';
    for(let i=0;i<e.results.length;i++){
      if(e.results[i].isFinal)f+=e.results[i][0].transcript;
      else im+=e.results[i][0].transcript;
    }
    pv.textContent=f+im||'...';
    if(f){inject(f.trim());rec.stop();}
  };
  rec.onerror=(e)=>{
    on=false;mb.className='';dots.className='';pv.className='';
    const m={'not-allowed':'🚫 Mic denied','no-speech':'🔇 No speech heard',
      'audio-capture':'⚠ No mic found','network':'⚠ Network error'};
    st.textContent=m[e.error]||('⚠ '+e.error);st.className='err';
    clearTimeout(tid);tid=setTimeout(()=>{st.textContent='🎤 Click to speak';st.className='';},3500);
  };
  rec.onend=()=>{on=false;mb.className='';dots.className='';pv.className='';};
  try{rec.start();}catch(x){st.textContent='⚠ Mic failed';st.className='err';}
}
</script>
"""

with tab3:
    if not st.session_state.dataset_id:
        st.info("Upload a dataset first to start chatting.")
    else:
        # ── Header row: title + mic button at the start ──────────
        import streamlit.components.v1 as components

        hcol1, hcol2 = st.columns([6, 1])
        with hcol1:
            st.markdown("### 💬 Chat with your Data")
            st.caption("Ask questions like 'What is the average sales by region?' or 'Are there any anomalies?'")
        with hcol2:
            st.markdown("<div style='padding-top:8px'>", unsafe_allow_html=True)
            components.html(SPEECH_TO_TEXT_HTML, height=52)
            st.markdown("</div>", unsafe_allow_html=True)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # ── TTS helper: generates a speak button for any text ────
        def tts_button(text: str, key: str):
            """Render a speak 🔊 button that reads `text` aloud via browser TTS."""
            # Escape backticks and backslashes for JS string safety
            safe = text.replace("\\", "\\\\").replace("`", "\\`")
            html = f"""
<div style="display:inline-block;margin-top:6px">
  <button id="tts_{key}"
    onclick="(function(){{
      const btn=document.getElementById('tts_{key}');
      if(window.__tts_{key}_speaking){{
        window.speechSynthesis.cancel();
        window.__tts_{key}_speaking=false;
        btn.innerHTML='🔊 Read aloud';
        btn.style.color='#a5b4fc';btn.style.borderColor='#6366f1';
        return;
      }}
      const u=new SpeechSynthesisUtterance(`{safe}`);
      u.rate=1;u.pitch=1;u.lang='en-US';
      u.onend=()=>{{window.__tts_{key}_speaking=false;btn.innerHTML='🔊 Read aloud';btn.style.color='#a5b4fc';btn.style.borderColor='#6366f1';}};
      u.onerror=()=>{{window.__tts_{key}_speaking=false;btn.innerHTML='🔊 Read aloud';}};
      window.speechSynthesis.cancel();
      window.__tts_{key}_speaking=true;
      btn.innerHTML='⏹ Stop';btn.style.color='#f87171';btn.style.borderColor='#ef4444';
      window.speechSynthesis.speak(u);
    }})()"
    style="background:transparent;border:1px solid #6366f1;color:#a5b4fc;
           border-radius:20px;padding:3px 12px;font-size:12px;
           font-family:Inter,system-ui,sans-serif;cursor:pointer;
           transition:all 0.2s;white-space:nowrap">
    🔊 Read aloud
  </button>
</div>"""
            import streamlit.components.v1 as components
            components.html(html, height=38)

        # ── Render message history ───────────────────────────────
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # Show TTS button only on assistant messages
                if message["role"] == "assistant":
                    tts_button(message["content"], f"hist_{i}")

        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                try:
                    # Create session if needed
                    if "chat_session_id" not in st.session_state:
                        session_resp = httpx.post(
                            f"{API_BASE_URL}/api/chat/sessions",
                            headers=get_headers(),
                            json={"dataset_id": st.session_state.dataset_id},
                            timeout=30.0
                        )
                        if session_resp.status_code == 200:
                            st.session_state.chat_session_id = session_resp.json()["id"]
                    
                    if "chat_session_id" in st.session_state:
                        chat_resp = httpx.post(
                            f"{API_BASE_URL}/api/chat/{st.session_state.chat_session_id}/message",
                            headers=get_headers(),
                            json={"message": prompt},
                            timeout=60.0
                        )
                        if chat_resp.status_code == 200:
                            full_response = chat_resp.json()["content"]
                            message_placeholder.markdown(full_response)
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                            # TTS button for the new response
                            tts_button(full_response, f"new_{len(st.session_state.messages)}")
                        else:
                            message_placeholder.markdown("Error: Could not get response from AI.")
                    else:
                        message_placeholder.markdown("Error: Could not create chat session.")
                except Exception as e:
                    message_placeholder.markdown(f"Error: {str(e)}")



# ── Tab 4: ML Studio ──────────────────────────────────────────

with tab4:
    if not st.session_state.dataset_id:
        st.info("Upload a dataset first to train models.")
    else:
        st.header("🔬 ML Studio — Modern AutoML Dashboard")
        
        ml_tab1, ml_tab2, ml_tab3 = st.tabs(["🚀 Training Studio", "📈 Deep Visualizations", "🏆 Model Leaderboard"])
        
        with ml_tab1:
            st.markdown("### Model Configuration")
            
            # 1. Task & Model Selection
            meta = st.session_state.dataset_meta
            col_names = [c["name"] for c in meta["columns"]]
            
            c1, c2, c3 = st.columns(3)
            with c1:
                task_type = st.selectbox("Task Type", ["classification", "regression"])
            with c2:
                # Fetch available models based on task
                available_models = []
                try:
                    m_resp = httpx.get(f"{API_BASE_URL}/api/ml/available-models?problem_type={task_type}", headers=get_headers())
                    if m_resp.status_code == 200:
                        available_models = m_resp.json()
                except: pass
                model_name = st.selectbox("Choose Algorithm", available_models if available_models else ["Random Forest", "Linear Regression"])
            with c3:
                target_col = st.selectbox("Target Column", options=col_names)
                
            if st.button("🏗️ Train Model", use_container_width=True):
                with st.spinner(f"Training {model_name}..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE_URL}/api/ml/run-task",
                            headers=get_headers(),
                            params={
                                "dataset_id": st.session_state.dataset_id,
                                "task_type": task_type,
                                "model_name": model_name,
                                "target_column": target_col
                            },
                            timeout=180.0
                        )
                        
                        if resp.status_code == 200:
                            st.session_state["last_trained_full"] = resp.json()
                            st.success(f"Model {model_name} trained successfully!")
                        else:
                            st.error(f"Training failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            # Display Metrics
            if "last_trained_full" in st.session_state:
                res = st.session_state["last_trained_full"]
                st.markdown("---")
                st.markdown(f"#### 📊 Performance: {res['model_name']}")
                
                metrics = res["metrics"]
                duration = res.get("duration", 0)
                
                m1, m2, m3, m4 = st.columns(4)
                if task_type == "classification":
                    accuracy = metrics.get("accuracy") if metrics.get("accuracy") is not None else 0
                    precision = metrics.get("precision") if metrics.get("precision") is not None else 0
                    recall = metrics.get("recall") if metrics.get("recall") is not None else 0
                    f1_score = metrics.get("f1_score") if metrics.get("f1_score") is not None else 0
                    with m1:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Accuracy</div><div class="metric-value">{accuracy*100:.1f}%</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Precision</div><div class="metric-value">{precision*100:.1f}%</div></div>', unsafe_allow_html=True)
                    with m3:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Recall</div><div class="metric-value">{recall*100:.1f}%</div></div>', unsafe_allow_html=True)
                    with m4:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">F1 Score</div><div class="metric-value">{f1_score*100:.1f}%</div></div>', unsafe_allow_html=True)
                else:
                    r2_score = metrics.get("r2_score") if metrics.get("r2_score") is not None else 0
                    rmse = metrics.get("rmse") if metrics.get("rmse") is not None else 0
                    mae = metrics.get("mae") if metrics.get("mae") is not None else 0
                    with m1:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">R² Score</div><div class="metric-value">{r2_score:.4f}</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">RMSE</div><div class="metric-value">{rmse:.2f}</div></div>', unsafe_allow_html=True)
                    with m3:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">MAE</div><div class="metric-value">{mae:.2f}</div></div>', unsafe_allow_html=True)
                    with m4:
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Time (s)</div><div class="metric-value">{duration:.2f}s</div></div>', unsafe_allow_html=True)

        with ml_tab2:
            if "last_trained_full" in st.session_state:
                res = st.session_state["last_trained_full"]
                charts = res.get("charts", {})
                
                c1, c2 = st.columns(2)
                with c1:
                    if "confusion_matrix" in charts:
                        st.plotly_chart(go.Figure(charts["confusion_matrix"]), use_container_width=True)
                    elif "residual_plot" in charts:
                        st.plotly_chart(go.Figure(charts["residual_plot"]), use_container_width=True)
                
                with c2:
                    if "feature_importance" in charts:
                        st.plotly_chart(go.Figure(charts["feature_importance"]), use_container_width=True)
                
                st.markdown("#### 🔍 Prediction Summary")
                st.info("This model is now ready for live inference in the 'AI Chat' or via the Prediction API.")
            else:
                st.info("Train a model to see deep visualizations.")

        with ml_tab3:
            st.markdown("### 🏆 Comparison Leaderboard")
            if "last_trained_full" in st.session_state:
                comparison = st.session_state["last_trained_full"].get("comparison", [])
                if comparison:
                    l_data = []
                    for m in comparison:
                        row = {
                            "Model": m["model_name"],
                            "Time (s)": round(m.get("training_time", 0) or 0, 2)
                        }
                        # Extract metrics
                        met_list = m.get("model_metrics") or []
                        met = (met_list[0] if met_list and met_list[0] is not None else {})
                        
                        if task_type == "classification":
                            accuracy = met.get('accuracy') if met.get('accuracy') is not None else 0
                            f1_score = met.get('f1_score') if met.get('f1_score') is not None else 0
                            row["Accuracy"] = f"{accuracy*100:.1f}%"
                            row["F1 Score"] = f"{f1_score*100:.1f}%"
                            sort_key = accuracy
                        else:
                            r2_score = met.get('r2_score') if met.get('r2_score') is not None else 0
                            rmse = met.get('rmse') if met.get('rmse') is not None else 0
                            row["R² Score"] = f"{r2_score:.4f}"
                            row["RMSE"] = f"{rmse:.2f}"
                            sort_key = r2_score
                        
                        row["_sort"] = sort_key
                        l_data.append(row)
                    
                    df_leader = pd.DataFrame(l_data).sort_values(by="_sort", ascending=False).reset_index(drop=True)
                    df_leader.index = df_leader.index + 1
                    df_leader.index.name = "Rank"
                    
                    st.dataframe(df_leader.drop(columns=["_sort"]), use_container_width=True)
                    
                    # Visual Comparison
                    st.markdown("#### 📊 Comparative Performance")
                    df_viz = pd.DataFrame(l_data).sort_values(by="_sort", ascending=True)
                    metric_name = "Accuracy" if task_type == "classification" else "R² Score"
                    
                    # Clean up percentage string for plotting if classification
                    if task_type == "classification":
                        df_viz["PlotValue"] = df_viz["Accuracy"].str.rstrip('%').astype('float') / 100
                    else:
                        df_viz["PlotValue"] = df_viz["R² Score"].astype('float')
                        
                    fig_comp = px.bar(
                        df_viz, x="PlotValue", y="Model", 
                        orientation="h", title=f"Model Rank by {metric_name}",
                        template="plotly_dark", color="PlotValue", color_continuous_scale="Viridis"
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info("No comparison data available yet.")
            else:
                st.info("Train at least one model to enable comparison.")

# ── Tab 5: Time Series Forecast ─────────────────────────────────

with tab5:
    if not st.session_state.dataset_id:
        st.info("Upload a dataset first to run time series forecasting.")
    else:
        st.header("📈 Time Series Forecasting")
        st.markdown("Predict future values using advanced statistical models.")
        
        meta = st.session_state.dataset_meta
        col_names = [c["name"] for c in meta["columns"]]
        date_candidates = [c["name"] for c in meta["columns"] if "date" in str(c.get("dtype", "")).lower() or "object" in str(c.get("dtype", "")).lower() or "datetime" in str(c.get("dtype", "")).lower()]
        numeric_cols = [c["name"] for c in meta["columns"] if "int" in str(c.get("dtype", "")).lower() or "float" in str(c.get("dtype", "")).lower()]

        fc_c1, fc_c2, fc_c3, fc_c4 = st.columns(4)
        with fc_c1:
            date_col = st.selectbox("Date Column (Optional)", ["Auto-detect"] + col_names, index=0)
        with fc_c2:
            val_col = st.selectbox("Target Value Column", ["Auto-detect"] + numeric_cols, index=0)
        with fc_c3:
            model_opts = {
                "ARIMA / SARIMA": "sarima",
                "Exponential Smoothing": "exponential_smoothing",
                "Moving Average": "moving_average",
                "Prophet": "prophet"
            }
            model_disp = st.selectbox("Forecasting Algorithm", list(model_opts.keys()))
            model_type = model_opts[model_disp]
        with fc_c4:
            periods = st.number_input("Forecast Horizon (periods)", min_value=1, max_value=365, value=30)
            
        if st.button("🚀 Run Forecast", use_container_width=True):
            with st.spinner(f"Running {model_disp} forecast..."):
                payload = {
                    "model": model_type,
                    "target_column": None if val_col == "Auto-detect" else val_col,
                    "date_column": None if date_col == "Auto-detect" else date_col,
                    "forecast_horizon": periods
                }
                try:
                    resp = httpx.post(
                        f"{API_BASE_URL}/api/forecast/run/{st.session_state.dataset_id}",
                        headers=get_headers(),
                        json=payload,
                        timeout=180.0
                    )
                    if resp.status_code == 200:
                        st.success("Forecast generated successfully!")
                        st.session_state["last_forecast"] = resp.json()
                    else:
                        show_api_error("Forecast failed", resp)
                except Exception as e:
                    st.error(f"Error: {e}")
                    
        if "last_forecast" in st.session_state:
            res = st.session_state["last_forecast"]
            st.markdown("---")
            
            if res.get("charts"):
                st.plotly_chart(res["charts"][0]["data"], use_container_width=True)
            
            st.markdown("### 📊 Forecast Summary")
            r_data = res.get("results", {})
            model_name_mapped = {
                "sarima": "ARIMA / SARIMA (Seasonal Autoregressive Integrated Moving Average)",
                "exponential_smoothing": "Holt-Winters Exponential Smoothing",
                "moving_average": "Simple Moving Average (Rolling Mean)",
                "prophet": "Prophet (Additive Regression Trend + Seasonality)"
            }.get(r_data.get("model_type", "").lower(), r_data.get("model_type", "Unknown"))
            
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Forecasting Algorithm", r_data.get("model_type", "Unknown").upper())
            col_s2.metric("Target Value Column", r_data.get("value_column", "Unknown"))
            col_s3.metric("Horizon (periods)", f"{r_data.get('periods', periods)}")
            
            with st.expander("⚙️ Model Parameters & Details", expanded=True):
                st.markdown(f"**Forecasting Method:** {model_name_mapped}")
                st.markdown(f"**Data Frequency:** `{r_data.get('frequency', 'Unknown')}`")
                st.markdown(f"**Detected Seasonal Period:** `{r_data.get('seasonal_period', 1)}`")
                if r_data.get("model_type") == "sarima":
                    st.markdown("**Order Parameters:** `(p, d, q) = (1, 1, 1)`")
                elif r_data.get("model_type") == "exponential_smoothing":
                    st.markdown("**Smoothing Parameters:** `Trend: Additive | Seasonality: Additive`")
                elif r_data.get("model_type") == "moving_average":
                    st.markdown("**Window Size:** `7 periods (default)`")
                elif r_data.get("model_type") == "prophet":
                    st.markdown("**Growth Mode:** `Linear` | **Seasonalities:** `Yearly, Weekly`")
                
                if st.checkbox("Show Raw Forecast JSON Data"):
                    st.json(r_data)

# ── Tab 6: Anomaly Detection ──────────────────────────────────

with tab6:
    if not st.session_state.dataset_id:
        st.info("Upload a dataset first to run anomaly detection.")
    else:
        st.header("🚨 Anomaly Detection")
        st.markdown("Detect outliers, unusual patterns, and data anomalies.")
        
        an_c1, an_c2 = st.columns(2)
        with an_c1:
            an_method = st.selectbox("Detection Algorithm", [
                "isolation_forest", "lof", "dbscan", "iqr", "zscore"
            ], format_func=lambda x: x.replace("_", " ").title() if x != "lof" and x != "iqr" else x.upper())
        with an_c2:
            if an_method in ["isolation_forest", "lof"]:
                an_thresh = st.slider("Contamination (Sensitivity)", min_value=0.01, max_value=0.5, value=0.05, step=0.01)
            elif an_method == "dbscan":
                an_thresh = st.number_input("EPS Distance", value=0.5, step=0.1)
            elif an_method == "zscore":
                an_thresh = st.slider("Z-Score Cutoff", min_value=1.0, max_value=5.0, value=3.0, step=0.1)
            else:
                an_thresh = st.slider("IQR Multiplier", min_value=1.0, max_value=5.0, value=1.5, step=0.1)
                
        if st.button("🔍 Detect Anomalies", use_container_width=True):
            with st.spinner(f"Running {an_method} anomaly detection..."):
                payload = {
                    "method": an_method,
                    "threshold": an_thresh
                }
                try:
                    resp = httpx.post(
                        f"{API_BASE_URL}/api/anomaly/run/{st.session_state.dataset_id}",
                        headers=get_headers(),
                        json=payload,
                        timeout=180.0
                    )
                    if resp.status_code == 200:
                        st.success("Anomalies detected successfully!")
                        st.session_state["last_anomaly"] = resp.json()
                    else:
                        show_api_error("Anomaly detection failed", resp)
                except Exception as e:
                    st.error(f"Error: {e}")
                    
        if "last_anomaly" in st.session_state:
            res = st.session_state["last_anomaly"]
            st.markdown("---")
            total = res.get("results", {}).get("total_anomalies", 0)
            
            st.markdown(f'<div class="status-card" style="border-left-color: #ef4444;"><h3 style="margin:0;color:#ef4444">{total} Total Anomalies Detected</h3></div>', unsafe_allow_html=True)
            
            charts = res.get("charts", [])
            if charts:
                cols = st.columns(len(charts) if len(charts) <= 2 else 2)
                for idx, chart in enumerate(charts):
                    with cols[idx % 2]:
                        st.plotly_chart(chart["data"], use_container_width=True)
                        
            with st.expander("View Detailed Anomaly Stats"):
                st.json(res.get("results", {}).get("anomalies_by_column", {}))

# ── Footer ────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #64748b;">DeepInsight Starter Suite v1.0.0 | Built with Streamlit & FastAPI</p>',
    unsafe_allow_html=True
)
