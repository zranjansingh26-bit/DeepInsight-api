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

tab1, tab2, tab3 = st.tabs(["📤 Upload", "📊 Overview", "🤖 AI Chat"])

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
                            st.error(f"Analysis failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")

# ── Tab 3: AI Chat ────────────────────────────────────────────

with tab3:
    if not st.session_state.dataset_id:
        st.info("Upload a dataset first to start chatting.")
    else:
        st.markdown("### 💬 Chat with your Data")
        st.caption("Ask questions like 'What is the average sales by region?' or 'Are there any anomalies?'")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Type your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Thinking...")
                
                # Here we would normally call the chat API
                # But for now, we'll simulate a response or call the endpoint if it exists
                # Since I don't want to overcomplicate the first version, let's just show a mock response
                # or a simple API call if the endpoint is ready.
                
                try:
                    # Search for existing session or create one
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
                        else:
                            message_placeholder.markdown("Error: Could not get response from AI.")
                except Exception as e:
                    message_placeholder.markdown(f"Error: {str(e)}")

# ── Footer ────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #64748b;">DeepInsight Starter Suite v1.0.0 | Built with Streamlit & FastAPI</p>',
    unsafe_allow_html=True
)
