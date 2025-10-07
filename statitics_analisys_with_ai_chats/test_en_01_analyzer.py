"""
en_01_analyzer.py
ChatBotAnalyzer - a lightweight analyzer that:
- Loads a CSV into a pandas.DataFrame
- Produces a structured "statistics_struct" dict with common metrics
- Produces a human-readable Markdown report ("statistics_markdown")
- Produces visualizations as Plotly figures in a dict {"title": fig}
- Calls an LLM (OpenRouter-compatible) and requests a two-part response:
    1) A JSON block enclosed in ```json ... ``` with keys: executive_summary, key_findings, recommendations, visualization_suggestions
    2) A human-readable Markdown report
The analyzer returns both the markdown and parsed JSON (if available).
"""

from typing import Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import json
import re
import requests
import os
from datetime import datetime


class ChatBotAnalyzer:
    def __init__(self, openrouter_api_key: str, model: str = "deepseek", timeout: int = 120):
        """
        Parameters
        - openrouter_api_key: API key for OpenRouter-compatible service
        - model: model identifier used by the provider (keeps flexible)
        - timeout: http request timeout in seconds
        """
        self.api_key = openrouter_api_key
        self.model = model
        self.timeout = timeout

    # -------------------- Data loading & basic stats --------------------
    def load_csv(self, path: str, nrows: Optional[int] = None, encoding: str = "utf-8") -> pd.DataFrame:
        """Load CSV into pandas DataFrame. Attempts a few fallbacks on errors."""
        try:
            df = pd.read_csv(path, nrows=nrows, encoding=encoding)
            return df
        except Exception:
            # Try with common separators / latin1
            try:
                df = pd.read_csv(path, nrows=nrows, sep=";", encoding="latin1")
                return df
            except Exception as e:
                raise e

    def generate_statistics_struct(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Return a dictionary with structured statistics useful for programmatic rendering."""
        struct = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "n_rows": int(df.shape[0]),
            "n_columns": int(df.shape[1]),
            "columns": {},
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_counts": df.isnull().sum().to_dict(),
        }
        # Numeric summaries
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        for c in num_cols:
            ser = df[c].dropna()
            struct["columns"][c] = {
                "type": "numeric",
                "count": int(ser.shape[0]),
                "mean": float(ser.mean()) if ser.shape[0] else None,
                "std": float(ser.std()) if ser.shape[0] else None,
                "min": float(ser.min()) if ser.shape[0] else None,
                "25%": float(ser.quantile(0.25)) if ser.shape[0] else None,
                "50%": float(ser.median()) if ser.shape[0] else None,
                "75%": float(ser.quantile(0.75)) if ser.shape[0] else None,
                "max": float(ser.max()) if ser.shape[0] else None,
                "n_unique": int(ser.nunique()),
                "n_missing": int(df[c].isnull().sum()),
            }
        # Categorical / boolean summaries (top values)
        cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        for c in cat_cols:
            ser = df[c].astype("object").dropna()
            top = ser.value_counts().head(10).to_dict()
            struct["columns"][c] = {
                "type": "categorical",
                "count": int(ser.shape[0]),
                "n_unique": int(ser.nunique()),
                "top_values": top,
                "n_missing": int(df[c].isnull().sum()),
            }
        return struct

    def generate_statistics_markdown(self, df: pd.DataFrame, struct: Dict[str, Any]) -> str:
        """Create a human-readable markdown report based on the struct generated above."""
        lines = []
        lines.append(f"# Dataset report\nGenerated at: {struct['generated_at']}\n")
        lines.append("## 📋 Dataset Overview\n")
        lines.append(f"- Rows: **{struct['n_rows']}**\n- Columns: **{struct['n_columns']}**\n")
        # Basic table of dtypes & missing
        lines.append("## 🔢 Column types & missing values\n")
        lines.append("| column | dtype | missing |\n|---:|---:|---:|\n")
        for col, dt in struct["dtypes"].items():
            missing = struct["missing_counts"].get(col, 0)
            lines.append(f"| {col} | {dt} | {missing} |\n")
        # Summaries for numeric columns
        lines.append("\n## 📈 Numeric summaries\n")
        for col, info in struct["columns"].items():
            if info["type"] == "numeric":
                lines.append(f"### `{col}`\n")
                lines.append(f"- count: {info['count']}  \n- mean: {info['mean']}  \n- std: {info['std']}  \n- min: {info['min']}  \n- 25%: {info['25%']}  \n- 50%: {info['50%']}  \n- 75%: {info['75%']}  \n- max: {info['max']}  \n- unique: {info['n_unique']}  \n- missing: {info['n_missing']}\n")
        # Summaries for categorical columns
        lines.append("\n## 🗂️ Categorical summaries\n")
        for col, info in struct["columns"].items():
            if info["type"] == "categorical":
                lines.append(f"### `{col}`\n- count: {info['count']}  \n- unique: {info['n_unique']}  \n- missing: {info['n_missing']}\n")
                # top values small table
                lines.append("\nTop values:\n\n|value|count|\n|---:|---:|\n")
                for k, v in (info.get("top_values") or {}).items():
                    lines.append(f"| {k} | {v} |\n")
        return "\\n".join(lines)

    # -------------------- Visualizations --------------------
    def generate_visualizations(self, df: pd.DataFrame, max_cols: int = 6) -> Dict[str, Any]:
        """
        Return a dict of Plotly figures keyed by descriptive titles.
        - Numeric: histogram and box for top numeric columns
        - Categorical: bar chart for top categories
        """
        figs = {}
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:max_cols]
        for c in num_cols:
            try:
                fig = px.histogram(df, x=c, nbins=40, title=f"Histogram — {c}")
                figs[f"hist_{c}"] = fig
                fig2 = px.box(df, y=c, title=f"Boxplot — {c}")
                figs[f"box_{c}"] = fig2
            except Exception:
                continue
        cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()[:max_cols]
        for c in cat_cols:
            try:
                top = df[c].value_counts().nlargest(20).reset_index()
                top.columns = [c, "count"]
                fig = px.bar(top, x=c, y="count", title=f"Top values — {c}")
                figs[f"bar_{c}"] = fig
            except Exception:
                continue
        return figs

    # -------------------- LLM interaction (OpenRouter style) --------------------
    def create_analysis_prompt(self, struct: Dict[str, Any], markdown_preview: str) -> str:
        """
        Build the instruction prompt that requests a JSON block + markdown.
        We ask the model to always return:
        ```json
        { "executive_summary": "...", "key_findings": [...], "recommendations": [...], "visualization_suggestions": [...] }
        ```
        followed by a human-readable markdown report.
        """
        prompt = [
            "You are an expert data analyst. Analyze the dataset and return TWO parts:\n",
            "1) A JSON block enclosed in ```json ... ``` with these keys:\n",
            "- executive_summary (string) — a 2-3 sentence summary\n            - key_findings (array of short strings)\n            - recommendations (array of short strings)\n            - visualization_suggestions (array of objects with keys: type, columns, rationale)\n",
            "2) A human-readable markdown report (for human consumption), with sections and tables as appropriate.\n",
            "Dataset structural summary (JSON):\n",
            "```json\n" + json.dumps(struct, default=str, indent=2) + "\n```\n",
            "\nProvide the JSON block first, then a clear separator, then the markdown report.\n"
        ]
        return "\\n".join(prompt) + "\\n\n" + "MARKDOWN_PREVIEW:\\n" + markdown_preview

    def call_llm(self, prompt: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Call OpenRouter-compatible endpoint. This function is intentionally simple and
        expects the provider to accept a POST with 'model' and 'input' or similar.
        Adjust as needed for your particular OpenRouter deployment.
        Returns (parsed_json_or_None, full_text_response)
        """
        endpoint = os.environ.get("OPENROUTER_ENDPOINT", "https://api.openrouter.ai/v1/chat/completions")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # A conservative request body compatible with many OpenRouter setups.
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.2,
        }
        try:
            r = requests.post(endpoint, headers=headers, json=body, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            # Attempt to extract textual content in a few known shapes:
            # - OpenRouter chat completions may return choices[0].message.content
            text = None
            if isinstance(data, dict):
                # try common keys
                choices = data.get("choices")
                if choices and isinstance(choices, list):
                    c0 = choices[0]
                    if isinstance(c0, dict):
                        msg = c0.get("message") or c0.get("delta") or c0
                        if isinstance(msg, dict):
                            text = msg.get("content") or msg.get("role") or None
                        elif isinstance(msg, str):
                            text = msg
                # fallback to 'output' key or 'text'
                if not text:
                    text = data.get("output") or data.get("text") or None
            if text is None:
                # fallback: stringify the response
                text = json.dumps(data)
        except Exception as e:
            text = f"LLM call failed: {e}"
            return None, text

        # Try to extract the JSON block enclosed in ```json ... ```
        json_obj = None
        m = re.search(r"```json(.*?)```", text, re.S | re.I)
        if m:
            json_text = m.group(1).strip()
            try:
                json_obj = json.loads(json_text)
            except Exception:
                # sometimes models print trailing commas or python-style quotes; try to sanitize
                json_text_sanitized = json_text.replace("\\'", "'")
                try:
                    json_obj = json.loads(json_text_sanitized)
                except Exception:
                    json_obj = None
        return json_obj, text

    def analyze_csv(self, path: str, nrows: Optional[int] = None) -> Dict[str, Any]:
        """
        Main convenience that ties together loading, stats, visualizations and LLM analysis.
        Returns a dict with keys:
        - dataframe (pd.DataFrame)
        - statistics_struct (dict)
        - statistics_markdown (str)
        - visualizations (dict of plotly figures)
        - ai_analysis_json (dict|None)
        - ai_analysis_markdown (str)
        """
        df = self.load_csv(path, nrows=nrows)
        struct = self.generate_statistics_struct(df)
        md = self.generate_statistics_markdown(df, struct)
        figs = self.generate_visualizations(df)
        # call the LLM (try to keep prompt relatively small)
        prompt = self.create_analysis_prompt(struct, md[:2000])
        ai_json, ai_text = self.call_llm(prompt)
        return {
            "dataframe": df,
            "statistics_struct": struct,
            "statistics_markdown": md,
            "visualizations": figs,
            "ai_analysis_json": ai_json,
            "ai_analysis_markdown": ai_text,
        }


# If executed as script, quick demo using file path argument
if __name__ == "__main__":
    import sys
    fp = sys.argv[1] if len(sys.argv) > 1 else None
    if not fp:
        print("Usage: python en_01_analyzer.py dataset.csv")
    else:
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            print("Please set OPENROUTER_API_KEY in env to call LLM. Running local stats only.")
            analyzer = ChatBotAnalyzer(openrouter_api_key="")
        else:
            analyzer = ChatBotAnalyzer(openrouter_api_key=key)
        res = analyzer.analyze_csv(fp, nrows=5000)
        print("Rows:", res['statistics_struct']['n_rows'])
        print("Columns:", res['statistics_struct']['n_columns'])
        # Save markdown to file for convenience
        with open("dataset_report.md", "w", encoding="utf-8") as f:
            f.write(res['statistics_markdown'])
        print("Report saved to dataset_report.md")