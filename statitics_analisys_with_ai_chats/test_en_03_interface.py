"""
en_03_interface.py
Streamlit-based web interface for the ChatBotAnalyzer (documented version).
Features implemented:
- Upload API key (text input or file)
- Upload CSV
- Cache analysis results with @st.cache_data
- Render dataframe preview, structured statistics, and Plotly visualizations
- Parse and render LLM JSON (if returned) and fallback to markdown
Notes:
- Install dependencies: pip install streamlit pandas plotly requests
- To run: streamlit run en_03_interface.py
"""

import streamlit as st
import pandas as pd
from data_eng_insights.statitics_analisys_with_ai_chats.test_en_01_analyzer import ChatBotAnalyzer
from data_eng_insights.statitics_analisys_with_ai_chats.test_en_02_api_key_reader import get_api_key, read_api_key_from_file
import io
import json
import os

st.set_page_config(page_title="ChatBot Analyzer", layout="wide", initial_sidebar_state="expanded")

# ------------------------ Sidebar: configuration ------------------------
st.sidebar.title("Configuration")
st.sidebar.markdown("Provide your OpenRouter API key or upload a file containing it.")

model_input = st.sidebar.text_input("Model identifier (OpenRouter)", value=os.environ.get("DEFAULT_LLM_MODEL", "deepseek"), help="Set your model identifier for OpenRouter.")

api_method = st.sidebar.radio("API key source:", ["From env", "Paste key", "Upload file"])
api_key = None
if api_method == "From env":
    api_key = get_api_key()  # tries environment variables
    st.sidebar.write("Using environment variable" if api_key else "No API key detected in environment")
elif api_method == "Paste key":
    api_key = st.sidebar.text_input("Paste API key", type="password")
else:
    uploaded = st.sidebar.file_uploader("Upload key file (txt)", type=["txt"])
    if uploaded:
        content = uploaded.read().decode("utf-8")
        # write to a temp file and parse
        tmp = io.StringIO(content)
        api_key = read_api_key_from_file(uploaded.name) or content.strip()

st.sidebar.markdown("---")
uploaded_csv = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
sample_n = st.sidebar.number_input("Preview rows", min_value=5, max_value=2000, value=200)
analyze_btn = st.sidebar.button("Analyze")


# ----------------------- Cached analysis call ---------------------------
@st.cache_data(show_spinner=False)
def analyze_cached(csv_bytes: bytes, api_key: str, model: str, preview_rows: int = 200):
    """
    Run analyzer and cache results for a given CSV content + api_key + model combo.
    We send the CSV bytes to disk, call the analyzer, and return the full dict.
    """
    tmp_path = "._tmp_uploaded_dataset.csv"
    with open(tmp_path, "wb") as f:
        f.write(csv_bytes)
    analyzer = ChatBotAnalyzer(openrouter_api_key=api_key, model=model)
    res = analyzer.analyze_csv(tmp_path, nrows=None)
    return res


# ----------------------- Main layout ---------------------------
st.title("ChatBot Analyzer — Streamlit UI (Updated)")
st.markdown("Upload a CSV and get a structured report + LLM analysis.")

if uploaded_csv is None:
    st.info("Upload a CSV from the sidebar to get started.")
else:
    if not api_key:
        st.warning("No API key provided. You can still see local statistics, but LLM analysis will not run.")
    csv_bytes = uploaded_csv.read()
    if analyze_btn:
        with st.spinner("Running analysis... this may take some time depending on dataset size and LLM response"):
            results = analyze_cached(csv_bytes, api_key or "", model_input, preview_rows=sample_n)
    else:
        results = analyze_cached(csv_bytes, api_key or "", model_input, preview_rows=sample_n)

    # Basic preview and types
    st.subheader("Data preview")
    df = results["dataframe"]
    st.dataframe(df.head(sample_n))
    st.write("Columns and dtypes:")
    st.table(pd.DataFrame(df.dtypes.rename("dtype")).reset_index().rename(columns={"index":"column"}))

    # Structured statistics
    st.subheader("Structured statistics (machine-friendly)")
    st.json(results.get("statistics_struct"))

    # Markdown report (human readable)
    st.subheader("Markdown report")
    md = results.get("statistics_markdown", "")
    st.download_button("Download Markdown report", md.encode("utf-8"), file_name="statistics_report.md")
    st.markdown("----")
    st.markdown(md)

    # Visualizations (Plotly)
    st.subheader("Visualizations")
    figs = results.get("visualizations") or {}
    if figs:
        for title, fig in figs.items():
            st.markdown(f"**{title}**")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No visualizations generated.")

    # LLM analysis: JSON first (preferred), then markdown fallback
    st.subheader("LLM analysis (structured)")
    ai_json = results.get("ai_analysis_json")
    ai_text = results.get("ai_analysis_markdown", "")
    if ai_json:
        st.markdown("**Executive summary**")
        st.write(ai_json.get("executive_summary", ""))
        st.markdown("**Key findings**")
        for k in ai_json.get("key_findings", []):
            st.markdown(f"- {k}")
        st.markdown("**Recommendations**")
        for r in ai_json.get("recommendations", []):
            st.markdown(f"- {r}")
        st.markdown("**Visualization suggestions**")
        for vs in ai_json.get("visualization_suggestions", []):
            st.markdown(f"- {vs}")
        st.download_button("Download AI JSON", json.dumps(ai_json, indent=2).encode("utf-8"), file_name="ai_analysis.json")
    else:
        st.info("No structured JSON returned by LLM; showing raw returned text below.")

    st.subheader("LLM analysis (raw / markdown)")
    st.download_button("Download AI markdown/raw", ai_text.encode("utf-8"), file_name="ai_analysis.md")
    st.markdown("----")
    st.markdown(ai_text)