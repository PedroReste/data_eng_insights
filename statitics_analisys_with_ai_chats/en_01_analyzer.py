# en_01_analyzer.py
import pandas as pd
import requests
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, Optional, List

# Import streamlit at the top level, but handle the case when it's not available
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

class ChatBotAnalyzer:
    def __init__(self, api_key: str = None):
        # Priority: provided key > Streamlit secrets > env var > file
        if api_key is None:
            self.api_key = self.get_api_key_secure()
        else:
            self.api_key = api_key
        
        if not self.api_key:
            raise ValueError("API key not found. Please set OPENROUTER_API_KEY environment variable or create 'api_key.txt' file.")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://data-analyzer-pr.streamlit.app",
            "X-Title": "Data Analyzer"
        }
        self.df = None

    def get_api_key_secure(self) -> Optional[str]:
        """
        Get API key securely with priority:
        1. Streamlit Secrets (if in Streamlit environment)
        2. Environment Variable
        3. Local file (for development only)
        """
        print(f"🔍 Starting API key search...")
        print(f"🔍 STREAMLIT_AVAILABLE: {STREAMLIT_AVAILABLE}")
        
        # 1. Try Streamlit Secrets
        if STREAMLIT_AVAILABLE:
            try:
                print("🔍 Checking Streamlit secrets...")
                if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
                    api_key = st.secrets['OPENROUTER_API_KEY']
                    print(f"🔍 Found key in secrets, length: {len(api_key) if api_key else 0}")
                    if api_key and api_key.strip():
                        print("✅ API key loaded from Streamlit Secrets")
                        return api_key.strip()
                else:
                    print("❌ OPENROUTER_API_KEY not found in Streamlit secrets")
            except Exception as e:
                print(f"⚠️ Streamlit secrets not accessible: {e}")
        
        # 2. Try Environment Variable
        env_key = os.getenv('OPENROUTER_API_KEY')
        print(f"🔍 Environment variable check: {'Found' if env_key else 'Not found'}")
        if env_key and env_key.strip():
            print("✅ API key loaded from environment variable")
            return env_key.strip()
        
        # 3. Try local file (for development only)
        file_key = self.read_api_key_from_file()
        print(f"🔍 File check: {'Found' if file_key else 'Not found'}")
        if file_key:
            print("✅ API key loaded from local file")
            return file_key
        
        print("❌ No API key found in any source")
        return None

    def read_api_key_from_file(self, file_path: str = None) -> Optional[str]:
        """
        Read API key from local file (for development only)
        """
        try:
            if file_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, "api_key.txt")
            
            print(f"🔍 Looking for API key file at: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ API key file not found: {file_path}")
                # Try alternative locations
                alternative_paths = [
                    "api_key.txt",
                    "./api_key.txt", 
                    "../api_key.txt",
                ]
                
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        file_path = alt_path
                        print(f"✅ Found API key file at: {file_path}")
                        break
                else:
                    print("❌ API key file not found in any common locations")
                    return None
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                print(f"📄 API key file content length: {len(content)} characters")
                
                # Handle different possible formats
                if content.startswith('open_router:'):
                    key = content.split('open_router:')[1].strip()
                elif ':' in content:
                    key = content.split(':', 1)[1].strip()
                else:
                    key = content.strip()
                
                if key:
                    print(f"✅ API key loaded successfully (first 5 chars): {key[:5]}...")
                    return key
                else:
                    print("❌ No API key found in file")
                    return None
                    
        except Exception as e:
            print(f"❌ Error reading API key file: {e}")
            return None

    def get_simple_column_types(self) -> Dict[str, List[str]]:
        """Get simplified column types grouped by category"""
        if self.df is None:
            return {}
        
        numerical_cols = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        boolean_cols = self.df.select_dtypes(include='bool').columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64', 'timedelta64']).columns.tolist()
        
        return {
            'Numerical': numerical_cols,
            'Categorical': categorical_cols,
            'True/False': boolean_cols,
            'Date/Time': datetime_cols
        }

    def get_detailed_column_info(self) -> pd.DataFrame:
        """Get detailed information about each column"""
        if self.df is None:
            return pd.DataFrame()
        
        column_info = []
        
        for col in self.df.columns:
            col_type = self._get_simple_dtype(self.df[col].dtype)
            non_null_count = self.df[col].count()
            null_count = self.df[col].isnull().sum()
            null_percentage = (null_count / len(self.df)) * 100
            
            column_info.append({
                'Column Name': col,
                'Type': col_type,
                'Non-Null Count': non_null_count,
                'Null Count': null_count,
                'Null Percentage': f"{null_percentage:.2f}%"
            })
        
        return pd.DataFrame(column_info)

    def _get_simple_dtype(self, dtype):
        """Convert detailed dtype to simplified category"""
        if np.issubdtype(dtype, np.number):
            return "Numerical"
        elif np.issubdtype(dtype, np.bool_):
            return "True/False"
        elif np.issubdtype(dtype, np.datetime64):
            return "Date/Time"
        else:
            return "Categorical"

    def detect_file_format(self, file_path: str) -> str:
        """Detect file format based on extension and content"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext in ['.xlsx', '.xls']:
            return 'excel'
        elif ext == '.json':
            return 'json'
        else:
            # Try to detect by content for files without extension or unknown
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    # Check if it's JSON
                    if first_line.startswith('{') or first_line.startswith('['):
                        return 'json'
                    # Check if it's CSV (comma separated)
                    elif ',' in first_line:
                        return 'csv'
            except:
                pass
            
            # Default to CSV for unknown formats
            return 'csv'

    def load_and_preview_data(self, file_path: str, sheet_name: str = None) -> pd.DataFrame:
        """Load CSV, Excel, or JSON file and return basic information"""
        try:
            file_format = self.detect_file_format(file_path)
            print(f"📁 Detected file format: {file_format}")
            
            if file_format == 'csv':
                self.df = pd.read_csv(file_path)
            elif file_format == 'excel':
                if sheet_name:
                    self.df = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    # Load first sheet by default
                    self.df = pd.read_excel(file_path)
            elif file_format == 'json':
                self.df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
            
            print(f"✅ Dataset loaded successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            print(f"📊 Data types: {dict(self.df.dtypes)}")
            return self.df
            
        except Exception as e:
            print(f"❌ Error loading file {file_path}: {e}")
            # Try alternative loading methods for JSON
            if file_format == 'json':
                try:
                    print("🔄 Trying alternative JSON loading method...")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.df = pd.json_normalize(data)
                    print(f"✅ JSON loaded successfully with json_normalize: {self.df.shape}")
                    return self.df
                except Exception as json_error:
                    print(f"❌ Alternative JSON loading also failed: {json_error}")
            return None

    def get_excel_sheets(self, file_path: str) -> List[str]:
        """Get list of available sheets in Excel file"""
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            print(f"❌ Error reading Excel sheets: {e}")
            return []

    def generate_descriptive_stats(self) -> str:
        """Generate comprehensive descriptive statistics in Markdown format"""
        if self.df is None:
            return "## ❌ No data loaded\n\nPlease load a dataset first."
            
        stats_summary = "# 📊 Descriptive Statistics Report\n\n"
        
        # Dataset Overview
        stats_summary += "## 📋 Dataset Overview\n\n"
        stats_summary += f"- **Total Rows**: {self.df.shape[0]:,}\n"
        stats_summary += f"- **Total Columns**: {self.df.shape[1]}\n"
        stats_summary += f"- **Missing Values**: {self.df.isnull().sum().sum()}\n"
        stats_summary += f"- **Duplicate Rows**: {self.df.duplicated().sum()}\n\n"
        
        # Data Types Summary
        stats_summary += "## 🔧 Data Types Summary\n\n"
        
        # Count by category instead of iterating through individual dtypes
        numerical_count = len(self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns)
        categorical_count = len(self.df.select_dtypes(include=['object', 'category', 'string']).columns)
        boolean_count = len(self.df.select_dtypes(include='bool').columns)
        datetime_count = len(self.df.select_dtypes(include=['datetime64', 'timedelta64']).columns)
        
        if numerical_count > 0:
            stats_summary += f"- **Numerical**: {numerical_count} columns\n"
        if categorical_count > 0:
            stats_summary += f"- **Categorical**: {categorical_count} columns\n"
        if boolean_count > 0:
            stats_summary += f"- **True/False**: {boolean_count} columns\n"
        if datetime_count > 0:
            stats_summary += f"- **Date/Time**: {datetime_count} columns\n"
        
        stats_summary += "\n"
        
        # Numerical columns
        numerical_cols = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(numerical_cols) > 0:
            stats_summary += "## 🔢 Numerical Columns\n\n"
            for col in numerical_cols:
                stats_summary += f"### 📈 {col}\n\n"
                stats_summary += f"- **Mean**: {self.df[col].mean():.2f}\n"
                stats_summary += f"- **Median**: {self.df[col].median():.2f}\n"
                stats_summary += f"- **Variance**: {self.df[col].var():.2f}\n"
                stats_summary += f"- **Standard Deviation**: {self.df[col].std():.2f}\n"
                stats_summary += f"- **Minimum**: {self.df[col].min():.2f}\n"
                stats_summary += f"- **Maximum**: {self.df[col].max():.2f}\n"
                stats_summary += f"- **Range**: {self.df[col].max() - self.df[col].min():.2f}\n"
                stats_summary += f"- **Missing Values**: {self.df[col].isnull().sum()}\n\n"
        
        # Categorical columns
        categorical_cols = self.df.select_dtypes(include=['object', 'category', 'string']).columns
        if len(categorical_cols) > 0:
            stats_summary += "## 📝 Categorical Columns\n\n"
            for col in categorical_cols:
                stats_summary += f"### 🏷️ {col}\n\n"
                stats_summary += f"- **Unique Values**: {self.df[col].nunique()}\n"
                stats_summary += f"- **Missing Values**: {self.df[col].isnull().sum()}\n"
                stats_summary += f"- **Top 3 Values**:\n"
                top_values = self.df[col].value_counts().head(3)
                for value, count in top_values.items():
                    stats_summary += f"  - `{value}`: {count} occurrences\n"
                stats_summary += "\n"
        
        # Boolean columns
        boolean_cols = self.df.select_dtypes(include='bool').columns
        if len(boolean_cols) > 0:
            stats_summary += "## ✅ True/False Columns\n\n"
            for col in boolean_cols:
                stats_summary += f"### 🔘 {col}\n\n"
                value_counts = self.df[col].value_counts()
                percentage = self.df[col].value_counts(normalize=True) * 100
                stats_summary += f"- **Distribution**:\n"
                for val, count in value_counts.items():
                    stats_summary += f"  - `{val}`: {count} ({percentage[val]:.1f}%)\n"
                stats_summary += f"- **Variance**: {self.df[col].var():.2f}\n"
                stats_summary += f"- **Standard Deviation**: {self.df[col].std():.2f}\n"
                stats_summary += f"- **Missing Values**: {self.df[col].isnull().sum()}\n\n"
        
        return stats_summary
    
    def create_analysis_prompt(self, stats_summary: str) -> str:
        """Create detailed prompt for API with markdown formatting request"""
        if self.df is None:
            return "No data available for analysis"
            
        prompt = f"""
        You are an expert data analyst. Please analyze the following dataset and provide a comprehensive descriptive statistics report with elaborate textual interpretation.

        DATASET OVERVIEW:
        - Shape: {self.df.shape}
        - Columns: {list(self.df.columns)}
        - Data types: {dict(self.df.dtypes)}

        DESCRIPTIVE STATISTICS:
        {stats_summary}

        Please provide a detailed analysis in MARKDOWN format including:

        # Executive Summary
        Brief overview of key findings and data quality assessment.

        ## Detailed Statistical Analysis
        Interpretation of measures and distribution analysis.

        ## Pattern Identification
        Trends, outliers, and interesting patterns.

        ## Business/Research Implications
        What the data reveals and practical significance.

        ## Recommendations
        Suggested next steps and improvements.

        Use proper markdown formatting with headers, bullet points, and emphasis. Be professional and insightful.
        """
        
        return prompt
    
    def generate_visualizations(self) -> Dict[str, go.Figure]:
        """Generate interactive visualizations for the dataset"""
        if self.df is None:
            return {}
        
        visualizations = {}
        
        # Data types pie chart - Fixed with proper dtype categorization
        def categorize_dtype(dtype):
            if np.issubdtype(dtype, np.number):
                return "Numerical"
            elif np.issubdtype(dtype, np.bool_):
                return "Boolean"
            elif np.issubdtype(dtype, np.datetime64):
                return "Date/Time"
            else:
                return "Categorical"
        
        dtype_counts = self.df.dtypes.apply(categorize_dtype).value_counts()
        
        if len(dtype_counts) > 0:
            fig_dtypes = px.pie(
                values=dtype_counts.values,
                names=dtype_counts.index,
                title="Data Types Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_dtypes.update_traces(textposition='inside', textinfo='percent+label')
            fig_dtypes.update_layout(height=400, showlegend=False)
            visualizations['data_types'] = fig_dtypes
        
        # Missing data bar chart
        missing_data = self.df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if len(missing_data) > 0:
            fig_missing = px.bar(
                x=missing_data.values,
                y=missing_data.index,
                orientation='h',
                title="Missing Values by Column",
                color=missing_data.values,
                color_continuous_scale='Viridis'
            )
            fig_missing.update_layout(height=400, xaxis_title="Missing Values Count", yaxis_title="Columns")
            visualizations['missing_data'] = fig_missing
        
        # Numerical columns distributions
        numerical_cols = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(numerical_cols) > 0:
            n_cols = min(3, len(numerical_cols))
            n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
            
            fig_dist = make_subplots(
                rows=n_rows, cols=n_cols,
                subplot_titles=numerical_cols[:n_rows*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(numerical_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                fig_dist.add_trace(
                    go.Histogram(x=self.df[col], name=col, nbinsx=20),
                    row=row, col=col_num
                )
            
            fig_dist.update_layout(height=300*n_rows, title_text="Numerical Variables Distributions", showlegend=False)
            visualizations['numerical_distributions'] = fig_dist
        
        # Categorical columns distributions - FIXED
        categorical_cols = self.df.select_dtypes(include=['object', 'category', 'string']).columns
        if len(categorical_cols) > 0:
            n_cols = min(3, len(categorical_cols))
            n_rows = (len(categorical_cols) + n_cols - 1) // n_cols

            fig_cat_dist = make_subplots(  # Changed variable name to avoid conflict
                rows=n_rows, cols=n_cols,
                subplot_titles=categorical_cols[:n_rows*n_cols],  # Fixed: use categorical_cols
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(categorical_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # For categorical data, use bar chart with value counts
                value_counts = self.df[col].value_counts().head(10)  # Top 10 values only
                fig_cat_dist.add_trace(
                    go.Bar(x=value_counts.index, y=value_counts.values, name=col),  # Fixed: go.Bar not go.bar
                    row=row, col=col_num
                )
            
            fig_cat_dist.update_layout(height=300*n_rows, title_text="Categorical Variables Distributions", showlegend=False)
            visualizations['categorical_distributions'] = fig_cat_dist

        # Boolean columns distributions - FIXED
        boolean_cols = self.df.select_dtypes(include='bool').columns
        if len(boolean_cols) > 0:
            n_cols = min(3, len(boolean_cols))
            n_rows = (len(boolean_cols) + n_cols - 1) // n_cols

            fig_bool_dist = make_subplots(  # Changed variable name
                rows=n_rows, cols=n_cols,
                subplot_titles=boolean_cols[:n_rows*n_cols],  # Fixed: use boolean_cols
                horizontal_spacing=0.1,
                vertical_spacing=0.15,
                specs=[[{"type": "pie"} for _ in range(n_cols)] for _ in range(n_rows)]  # Specify pie chart type
            )
            
            for i, col in enumerate(boolean_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # For boolean data, use pie chart
                value_counts = self.df[col].value_counts()
                fig_bool_dist.add_trace(
                    go.Pie(labels=[str(label) for label in value_counts.index], 
                        values=value_counts.values, name=col),  # Fixed: go.Pie not go.pie
                    row=row, col=col_num
                )
            
            fig_bool_dist.update_layout(height=300*n_rows, title_text="Boolean Variables Distributions", showlegend=False)
            visualizations['boolean_distributions'] = fig_bool_dist

        # Date/time columns distributions - FIXED
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns  # Removed timedelta64 for simplicity
        if len(datetime_cols) > 0:
            n_cols = min(3, len(datetime_cols))
            n_rows = (len(datetime_cols) + n_cols - 1) // n_cols

            fig_date_dist = make_subplots(  # Changed variable name
                rows=n_rows, cols=n_cols,
                subplot_titles=datetime_cols[:n_rows*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(datetime_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # For datetime data, use line chart with value counts over time
                date_counts = self.df[col].value_counts().sort_index()
                fig_date_dist.add_trace(
                    go.Scatter(x=date_counts.index, y=date_counts.values, mode='lines', name=col),  # Fixed: go.Scatter for line chart
                    row=row, col=col_num
                )
            
            fig_date_dist.update_layout(height=300*n_rows, title_text="Date/Time Variables Distributions", showlegend=False)  # Fixed title
            visualizations['datetime_distributions'] = fig_date_dist  # Fixed key name

        # Correlation heatmap for numerical data only - FIXED
        numerical_cols_for_corr = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(numerical_cols_for_corr) > 1:
            corr_matrix = self.df[numerical_cols_for_corr].corr()
            fig_corr = px.imshow(
                corr_matrix,
                title="Correlation Heatmap (Numerical Variables)",
                color_continuous_scale='RdBu_r',
                aspect="auto"
            )
            fig_corr.update_layout(height=500)
            visualizations['correlation_heatmap'] = fig_corr
        
        return visualizations
         
    def call_open_router_api(self, prompt: str) -> Optional[str]:
        """Make API call to Open Router"""
        payload = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert data analyst with strong statistical knowledge. Provide detailed, accurate analyses with practical interpretations. Format your response in beautiful markdown with proper headers, bullet points, and emphasis. Be thorough and professional."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 4000,
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def analyze_file(self, file_path: str, sheet_name: str = None, save_output: bool = False, output_dir: str = None) -> Dict[str, Any]:
        """Main method to analyze data file (CSV, Excel, JSON)"""
        
        print("🚀 Starting Data Analysis...")
        
        # Load data
        df = self.load_and_preview_data(file_path, sheet_name)
        if df is None:
            return None
        
        # Generate descriptive stats
        print("📈 Generating descriptive statistics...")
        stats_summary = self.generate_descriptive_stats()
        
        # Generate visualizations
        print("🎨 Creating visualizations...")
        visualizations = self.generate_visualizations()
        
        # Create analysis prompt
        prompt = self.create_analysis_prompt(stats_summary)
        
        # Call API
        print("🤖 Calling API for detailed analysis...")
        analysis_result = self.call_open_router_api(prompt)
        
        if analysis_result:
            results = {
                'dataframe': df,
                'statistics': stats_summary,
                'ai_analysis': analysis_result,
                'visualizations': visualizations
            }
            
            # Save results if requested
            if save_output:
                self.save_results(results, file_path, output_dir)
            
            return results
        else:
            print("❌ Failed to get analysis from API")
            return None
    
    def save_results(self, results: Dict[str, Any], original_file_path: str, output_dir: str = None):
        """Save analysis results to TXT files"""
        base_name = os.path.splitext(os.path.basename(original_file_path))[0]
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_path = os.path.join(output_dir, base_name)
        else:
            base_path = base_name
        
        # Save statistics as markdown
        with open(f"{base_path}_statistics.txt", "w", encoding="utf-8") as f:
            f.write(results['statistics'])
        
        # Save AI analysis as markdown
        with open(f"{base_path}_ai_analysis.txt", "w", encoding="utf-8") as f:
            f.write(results['ai_analysis'])
        
        # Save combined report as markdown
        combined_report = f"""# 📊 Data Analysis Report

## Dataset: {base_name}

## Descriptive Statistics

{results['statistics']}

## Analysis

{results['ai_analysis']}

---
*Report generated automatically with AI Data Analyzer*
"""
        with open(f"{base_path}_complete_report.txt", "w", encoding="utf-8") as f:
            f.write(combined_report)
        
        print(f"💾 Results saved as Markdown files:")
        print(f"   - {base_path}_statistics.txt")
        print(f"   - {base_path}_ai_analysis.txt")
        print(f"   - {base_path}_complete_report.txt")