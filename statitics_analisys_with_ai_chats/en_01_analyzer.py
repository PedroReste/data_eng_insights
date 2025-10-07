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

class ChatBotAnalyzer:
    def __init__(self, api_key: str = None):
        # If no API key provided, try to read from file
        if api_key is None:
            api_key = self.read_api_key_from_file()
        
        if not api_key:
            raise ValueError("API key not found. Please create an 'api_key.txt' file in the same folder.")
        
        self.api_key = api_key.strip()
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://data-analyzer.streamlit.app",
            "X-Title": "Data Analyzer"
        }
        self.df = None

    def read_api_key_from_file(self, file_path: str = None) -> Optional[str]:
        """
        Read API key from text file in the same folder
        Supports formats: 'open_router:your_key' or just 'your_key'
        """
        try:
            # Use relative path to current script directory
            if file_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, "api_key.txt")
            
            print(f"🔍 Looking for API key file at: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ API key file not found: {file_path}")
                # Try alternative locations
                alternative_paths = [
                    "api_key.txt",  # Current working directory
                    "./api_key.txt",  # Current working directory
                    "../api_key.txt",  # Parent directory
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
                    print(f"✅ API key loaded successfully (first 05 chars): {key[:5]}...")
                    return key
                else:
                    print("❌ No API key found in file")
                    return None
                    
        except Exception as e:
            print(f"❌ Error reading API key file: {e}")
            return None

    def load_and_preview_data(self, file_path: str) -> pd.DataFrame:
        """Load CSV file and return basic information"""
        try:
            self.df = pd.read_csv(file_path)
            print(f"✅ Dataset loaded successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return self.df
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return None
    
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

        ## Visualization Suggestions
        Recommended charts and analysis approaches.

        Use proper markdown formatting with headers, bullet points, and emphasis. Be professional and insightful.
        """
        
        return prompt
    
    def generate_visualizations(self) -> Dict[str, go.Figure]:
        """Generate interactive visualizations for the dataset"""
        if self.df is None:
            return {}
        
        visualizations = {}
        
        # Data types pie chart
        dtype_counts = self.df.dtypes.value_counts()
        fig_dtypes = px.pie(
            values=dtype_counts.values,
            names=[str(dtype) for dtype in dtype_counts.index],
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
            # Create subplots for numerical distributions
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
        
        # Correlation heatmap for numerical data
        if len(numerical_cols) > 1:
            corr_matrix = self.df[numerical_cols].corr()
            fig_corr = px.imshow(
                corr_matrix,
                title="Correlation Heatmap",
                color_continuous_scale='RdBu_r',
                aspect="auto"
            )
            fig_corr.update_layout(height=500)
            visualizations['correlation_heatmap'] = fig_corr
        
        return visualizations
         
    def call_open_router_api(self, prompt: str) -> Optional[str]:
        """Make API call to Open Router"""
        payload = {
            "model": "deepseek/deepseek-chat-v3.1:free",
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
    
    def analyze_csv(self, file_path: str, save_output: bool = False, output_dir: str = None) -> Dict[str, Any]:
        """Main method to analyze CSV file"""
        
        print("🚀 Starting CSV Analysis...")
        
        # Load data
        df = self.load_and_preview_data(file_path)
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
        """Save analysis results to markdown files"""
        base_name = os.path.splitext(os.path.basename(original_file_path))[0]
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_path = os.path.join(output_dir, base_name)
        else:
            base_path = base_name
        
        # Save statistics as markdown
        with open(f"{base_path}_statistics.md", "w", encoding="utf-8") as f:
            f.write(results['statistics'])
        
        # Save AI analysis as markdown
        with open(f"{base_path}_ai_analysis.md", "w", encoding="utf-8") as f:
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
        with open(f"{base_path}_complete_report.md", "w", encoding="utf-8") as f:
            f.write(combined_report)
        
        print(f"💾 Results saved as Markdown files:")
        print(f"   - {base_path}_statistics.md")
        print(f"   - {base_path}_ai_analysis.md")
        print(f"   - {base_path}_complete_report.md")