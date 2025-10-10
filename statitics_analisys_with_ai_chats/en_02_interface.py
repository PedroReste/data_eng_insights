# en_02_interface.py
import streamlit as st
import pandas as pd
import tempfile
import os
import re
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Import from our modules
from en_01_analyzer import ChatBotAnalyzer

# Set page configuration
st.set_page_config(
    page_title="Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
        font-weight: 700;
    }
    .subsection-header {
        font-size: 1.4rem;
        color: #34495e;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        background: linear-gradient(90deg, #3498db, transparent);
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3498db;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
    }
    .variable-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #e74c3c;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .categorical-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .boolean-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #2ecc71;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .progress-bar {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .distribution-bar {
        background: linear-gradient(90deg, #3498db, #2980b9);
        height: 20px;
        border-radius: 10px;
        margin: 0.25rem 0;
        color: white;
        padding: 0 1rem;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .ai-insight-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .recommendation-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .highlight-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #e74c3c;
        background: #f8f9fa;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        margin: 0 0.2rem;
    }
    .data-type-tag {
        display: inline-block;
        background: #3498db;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    .value-tag {
        display: inline-block;
        background: #2ecc71;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.7rem;
        margin: 0.1rem;
    }
    .preview-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def create_stat_card(value, label, icon="📊", color="#667eea"):
    def darken_color(hex_color, factor=0.8):
        """Darken a hex color"""
        import colorsys
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        hls = colorsys.rgb_to_hls(*[x/255.0 for x in rgb])
        darker = colorsys.hls_to_rgb(hls[0], max(0, hls[1] * factor), hls[2])
        return '#{:02x}{:02x}{:02x}'.format(*(int(x * 255) for x in darker))
    
    darkened_color = darken_color(color)
    
    return f"""
    <div class="stat-card" style="background: linear-gradient(135deg, {color} 0%, {darkened_color} 100%);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def display_data_preview(uploaded_file, tmp_file_path):
    """Display data preview in the main area"""
    st.markdown('<div class="section-header">👀 Data Preview</div>', unsafe_allow_html=True)
    
    try:
        df_preview = pd.read_csv(tmp_file_path)
        
        # File info card
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_stat_card(
                f"{df_preview.shape[0]:,}", 
                "Total Rows", 
                "📈", 
                "#2ecc71"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_stat_card(
                f"{df_preview.shape[1]}", 
                "Total Columns", 
                "📊", 
                "#3498db"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_stat_card(
                f"{df_preview.isnull().sum().sum():,}", 
                "Missing Values", 
                "⚠️", 
                "#f39c12"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_stat_card(
                f"{df_preview.duplicated().sum():,}",
                "Duplicated Rows",
                "🔎",
                "#f31212"
            ), unsafe_allow_html=True)
        
        # Data preview with expandable sections
        tab1, tab2, tab3 = st.tabs(["📋 Data Sample", "🔍 Column Info", "📊 Quick Stats"])
        
        with tab1:
            st.markdown(f"**First 10 rows of {uploaded_file.name}:**")
            st.dataframe(df_preview.head(10), use_container_width=True)
        
        with tab2:
            st.markdown("**Column Information:**")
            col_info = pd.DataFrame({
                'Column': df_preview.columns,
                'Data Type': df_preview.dtypes.values,
                'Non-Null Count': df_preview.count().values,
                'Null Count': df_preview.isnull().sum().values
            })
            st.dataframe(col_info, use_container_width=True)
        
        with tab3:
            st.markdown("**Quick Statistics:**")
            if len(df_preview.select_dtypes(include=['number']).columns) > 0:
                st.dataframe(df_preview.describe(), use_container_width=True)
            else:
                st.info("No numerical columns for statistical summary")
        
        return df_preview
        
    except Exception as e:
        st.error(f"Error previewing data: {e}")
        return None

def display_enhanced_statistics(results):
    """Display enhanced statistics with visualizations"""
    st.markdown('<div class="section-header">📊 Dataset Overview & Statistics</div>', unsafe_allow_html=True)
    
    # Display visualizations first
    if 'visualizations' in results and results['visualizations']:
        st.markdown("### 📈 Interactive Visualizations")
        
        # Data types distribution
        if 'data_types' in results['visualizations']:
            st.plotly_chart(results['visualizations']['data_types'], use_container_width=True)
        
        # Missing data
        if 'missing_data' in results['visualizations']:
            st.plotly_chart(results['visualizations']['missing_data'], use_container_width=True)
        
        # Numerical distributions
        if 'numerical_distributions' in results['visualizations']:
            st.plotly_chart(results['visualizations']['numerical_distributions'], use_container_width=True)
        
        # Categorical distributions
        if 'categorical_distributions' in results['visualizations']:
            st.plotly_chart(results['visualizations']['categorical_distributions'], use_container_width=True)
        
        # Boolean distributions
        if 'boolean_distributions' in results['visualizations']:
            st.plotly_chart(results['visualizations']['boolean_distributions'], use_container_width=True)

        # Date/time distributions
        if 'datetime_distributions' in results['visualizations']:
            st.plotly_chart(results['visualizations']['datetime_distributions'], use_container_width=True)
        
        # Correlation heatmap
        if 'correlation_heatmap' in results['visualizations']:
            st.plotly_chart(results['visualizations']['correlation_heatmap'], use_container_width=True)
    
    # Parse the statistics text
    stats_text = results['statistics']
    
    # Display dataset overview in a beautiful grid
    display_dataset_overview(stats_text)
    
    # Display data types summary
    display_data_types_summary(stats_text)
    
    # Display variables in organized tabs
    display_variables_analysis(stats_text)

def display_dataset_overview(stats_text):
    """Display dataset overview metrics"""
    st.markdown("### 📋 Dataset Overview")
    
    # Extract overview metrics using regex for better parsing
    total_rows_match = re.search(r"- \*\*Total Rows\*\*:?\s*([\d,]+)", stats_text)
    total_cols_match = re.search(r"- \*\*Total Columns\*\*:?\s*(\d+)", stats_text)
    missing_vals_match = re.search(r"- \*\*Missing Values\*\*:?\s*([\d,]+)", stats_text)
    duplicate_rows_match = re.search(r"- \*\*Duplicate Rows\*\*:?\s*([\d,]+)", stats_text)
    
    # Create metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rows = total_rows_match.group(1) if total_rows_match else "N/A"
        st.markdown(create_stat_card(
            total_rows, 
            "Total Rows", 
            "📈", 
            "#2ecc71"
        ), unsafe_allow_html=True)
    
    with col2:
        total_cols = total_cols_match.group(1) if total_cols_match else "N/A"
        st.markdown(create_stat_card(
            total_cols, 
            "Total Columns", 
            "📊", 
            "#3498db"
        ), unsafe_allow_html=True)
    
    with col3:
        missing_vals = missing_vals_match.group(1) if missing_vals_match else "N/A"
        st.markdown(create_stat_card(
            missing_vals, 
            "Missing Values", 
            "⚠️", 
            "#f39c12"
        ), unsafe_allow_html=True)
    
    with col4:
        duplicate_rows = duplicate_rows_match.group(1) if duplicate_rows_match else "N/A"
        st.markdown(create_stat_card(
            duplicate_rows, 
            "Duplicate Rows", 
            "🔍", 
            "#e74c3c" 
        ), unsafe_allow_html=True)

def display_data_types_summary(stats_text):
    """Display data types summary"""
    st.markdown("### 🔧 Data Types Distribution")
    
    # Extract data types using regex
    numerical_match = re.search(r"- \*\*Numerical\*\*:?\s*(\d+)", stats_text)
    categorical_match = re.search(r"- \*\*Categorical\*\*:?\s*(\d+)", stats_text)
    boolean_match = re.search(r"- \*\*True/False\*\*:?\s*(\d+)", stats_text)
    datetime_match = re.search(r"- \*\*Date/Time\*\*:?\s*(\d+)", stats_text)
    
    data_types = []
    if numerical_match:
        data_types.append(("Numerical", numerical_match.group(1)))
    if categorical_match:
        data_types.append(("Categorical", categorical_match.group(1)))
    if boolean_match:
        data_types.append(("True/False", boolean_match.group(1)))
    if datetime_match:
        data_types.append(("Date/Time", datetime_match.group(1)))
    
    # Create data types display
    if data_types:
        cols = st.columns(len(data_types))
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
        
        for i, (dtype, count) in enumerate(data_types):
            with cols[i % len(cols)]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: {colors[i % len(colors)]}; 
                         color: white; border-radius: 10px; margin: 0.5rem;">
                    <div style="font-size: 1.2rem; font-weight: bold;">{count}</div>
                    <div style="font-size: 0.9rem;">{dtype}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No data type information available.")

def display_variables_analysis(stats_text):
    """Display variables analysis in organized tabs"""
    st.markdown("### 📈 Variables Analysis")
    
    # Check which types of variables exist
    has_numerical = "## 🔢 Numerical Columns" in stats_text
    has_categorical = "## 📝 Categorical Columns" in stats_text
    has_boolean = "## ✅ True/False Columns" in stats_text
    
    tabs = []
    if has_numerical:
        tabs.append("🔢 Numerical Variables")
    if has_categorical:
        tabs.append("📝 Categorical Variables")
    if has_boolean:
        tabs.append("✅ True/False Variables")
    
    if tabs:
        created_tabs = st.tabs(tabs)
        
        tab_index = 0
        if has_numerical:
            with created_tabs[tab_index]:
                display_numerical_variables(stats_text)
            tab_index += 1
        
        if has_categorical:
            with created_tabs[tab_index]:
                display_categorical_variables(stats_text)
            tab_index += 1
        
        if has_boolean:
            with created_tabs[tab_index]:
                display_boolean_variables(stats_text)
    else:
        st.info("No variable analysis available.")

def display_numerical_variables(stats_text):
    """Display numerical variables with enhanced visualization"""
    if '## 🔢 Numerical Columns' not in stats_text:
        st.info("No numerical variables found in the dataset.")
        return
    
    # Extract numerical section
    numerical_section = stats_text.split('## 🔢 Numerical Columns')[1]
    if '## 📝 Categorical Columns' in numerical_section:
        numerical_section = numerical_section.split('## 📝 Categorical Columns')[0]
    elif '## ✅ Boolean Columns' in numerical_section:
        numerical_section = numerical_section.split('## ✅ Boolean Columns')[0]
    
    # Extract individual variables
    variables = re.split(r'### 📈 ', numerical_section)[1:]
    
    for var_content in variables:
        if var_content.strip():
            lines = var_content.split('\n')
            var_name = lines[0].strip()
            
            # Extract statistics using regex
            stats = {}
            stats_patterns = {
                'Mean': r"- \*\*Mean\*\*:?\s*([\d.-]+)",
                'Median': r"- \*\*Median\*\*:?\s*([\d.-]+)", 
                'Variance': r"- \*\*Variance\*\*:?\s*([\d.-]+)",
                'Standard Deviation': r"- \*\*Standard Deviation\*\*:?\s*([\d.-]+)",
                'Minimum': r"- \*\*Minimum\*\*:?\s*([\d.-]+)",
                'Maximum': r"- \*\*Maximum\*\*:?\s*([\d.-]+)",
                'Range': r"- \*\*Range\*\*:?\s*([\d.-]+)",
                'Missing Values': r"- \*\*Missing Values\*\*:?\s*(\d+)"
            }
            
            for stat_name, pattern in stats_patterns.items():
                match = re.search(pattern, var_content)
                if match:
                    stats[stat_name] = match.group(1)
            
            st.markdown(f'<div class="variable-card">', unsafe_allow_html=True)
            
            # Variable header
            st.markdown(f"#### 📈 {var_name}")
            
            # Create a grid for statistics
            col1, col2 = st.columns(2)
            
            with col1:
                # Central tendency metrics
                if 'Mean' in stats:
                    st.metric("Mean", f"{float(stats['Mean']):.2f}")
                if 'Median' in stats:
                    st.metric("Median", f"{float(stats['Median']):.2f}")
                if 'Standard Deviation' in stats:
                    st.metric("Std Dev", f"{float(stats['Standard Deviation']):.2f}")
            
            with col2:
                # Range metrics
                if 'Minimum' in stats:
                    st.metric("Minimum", f"{float(stats['Minimum']):.2f}")
                if 'Maximum' in stats:
                    st.metric("Maximum", f"{float(stats['Maximum']):.2f}")
                if 'Range' in stats:
                    st.metric("Range", f"{float(stats['Range']):.2f}")
            
            # Additional info
            if 'Missing Values' in stats:
                st.info(f"Missing Values: {stats['Missing Values']}")
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_categorical_variables(stats_text):
    """Display categorical variables with enhanced visualization"""
    if '## 📝 Categorical Columns' not in stats_text:
        st.info("No categorical variables found in the dataset.")
        return
    
    # Extract categorical section
    categorical_section = stats_text.split('## 📝 Categorical Columns')[1]
    if '## ✅ Boolean Columns' in categorical_section:
        categorical_section = categorical_section.split('## ✅ Boolean Columns')[0]
    
    # Extract individual variables
    variables = re.split(r'### 🏷️ ', categorical_section)[1:]
    
    for var_content in variables:
        if var_content.strip():
            lines = var_content.split('\n')
            var_name = lines[0].strip()
            
            # Extract statistics
            unique_values = re.search(r"- \*\*Unique Values\*\*:?\s*(\d+)", var_content)
            missing_values = re.search(r"- \*\*Missing Values\*\*:?\s*(\d+)", var_content)
            
            # Extract top values
            top_values = []
            top_values_section = var_content.split("- **Top 3 Values**:")[1] if "- **Top 3 Values**:" in var_content else ""
            if top_values_section:
                top_matches = re.findall(r"- `([^`]+)`: (\d+) occurrences", top_values_section)
                top_values = [(val, int(count)) for val, count in top_matches]
            
            st.markdown(f'<div class="categorical-card">', unsafe_allow_html=True)
            
            # Variable header
            st.markdown(f"#### 🏷️ {var_name}")
            
            # Basic info
            col1, col2 = st.columns(2)
            with col1:
                if unique_values:
                    st.metric("Unique Values", unique_values.group(1))
            with col2:
                if missing_values:
                    st.metric("Missing Values", missing_values.group(1))
            
            # Top values visualization
            if top_values:
                st.markdown("**Top Values Distribution:**")
                
                # Create a bar chart for top values
                values, counts = zip(*top_values)
                
                fig = px.bar(
                    x=counts,
                    y=values,
                    orientation='h',
                    title=f"Top Values for {var_name}",
                    color=counts,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    height=200,
                    showlegend=False,
                    xaxis_title="Count",
                    yaxis_title="Values"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_boolean_variables(stats_text):
    """Display True/False variables with enhanced visualization"""
    if '## ✅ Boolean Columns' not in stats_text:
        st.info("No True/False variables found in the dataset.")
        return
    
    # Extract boolean section
    boolean_section = stats_text.split('## ✅ True/False Columns')[1]
    
    # Extract individual variables
    variables = re.split(r'### 🔘 ', boolean_section)[1:]
    
    for var_content in variables:
        if var_content.strip():
            lines = var_content.split('\n')
            var_name = lines[0].strip()
            
            # Extract distribution information
            distribution_matches = re.findall(r"- `(True|False)`: (\d+) \(([\d.]+)%\)", var_content)
            
            st.markdown(f'<div class="boolean-card">', unsafe_allow_html=True)
            
            # Variable header
            st.markdown(f"#### 🔘 {var_name}")
            
            if distribution_matches:
                # Create distribution visualization
                total_count = sum(int(count) for _, count, _ in distribution_matches)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Create a pie chart
                    labels = [val for val, _, _ in distribution_matches]
                    values = [int(count) for _, count, _ in distribution_matches]
                    percentages = [float(pct) for _, _, pct in distribution_matches]
                    
                    fig = px.pie(
                        values=values,
                        names=labels,
                        title=f"Distribution of {var_name}",
                        color_discrete_sequence=['#2ecc71', '#e74c3c']
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Display metrics
                    for i, (val, count, pct) in enumerate(distribution_matches):
                        st.metric(
                            f"{val} Count", 
                            f"{count} ({pct}%)",
                            delta=None
                        )
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_ai_analysis(results):
    """Display AI analysis with enhanced formatting"""
    st.markdown('<div class="section-header">🤖 AI Analysis & Insights</div>', unsafe_allow_html=True)
    
    if 'ai_analysis' not in results or not results['ai_analysis']:
        st.error("No AI analysis available. Please run the analysis first.")
        return
    
    analysis_text = results['ai_analysis']
    
    # Split analysis into sections based on markdown headers
    sections = re.split(r'(?=^#+\s)', analysis_text, flags=re.MULTILINE)
    
    for section in sections:
        if not section.strip():
            continue
            
        # Check section type for special styling
        section_lower = section.lower()
        
        if any(keyword in section_lower for keyword in ['executive summary', 'summary']):
            st.markdown('<div class="ai-insight-card">', unsafe_allow_html=True)
            st.markdown(section)
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif any(keyword in section_lower for keyword in ['recommendation', 'suggestion', 'next steps']):
            st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
            st.markdown(section)
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif any(keyword in section_lower for keyword in ['pattern', 'trend', 'insight', 'finding']):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(section)
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Default styling for other sections
            st.markdown(section)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 AI Data Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analyzer' not in st.session_state:
        try:
            st.session_state.analyzer = ChatBotAnalyzer()
            st.success("✅ Analyzer initialized successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize analyzer: {e}")
            return
    
    # Sidebar for file upload (simplified)
    with st.sidebar:
        st.markdown("## 📁 Upload Dataset")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload your dataset in CSV format"
        )
        
        if uploaded_file is not None:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Analysis button in sidebar
            st.markdown("## 🚀 Start Analysis")
            if st.button("Analyze Dataset", type="primary", use_container_width=True):
                with st.spinner("🤖 Analyzing dataset with AI..."):
                    try:
                        results = st.session_state.analyzer.analyze_csv(tmp_file_path)
                        if results:
                            st.session_state.analysis_results = results
                            st.session_state.uploaded_file_name = uploaded_file.name
                            st.success("✅ Analysis completed successfully!")
                        else:
                            st.error("❌ Analysis failed. Please check the console for details.")
                    except Exception as e:
                        st.error(f"❌ Analysis error: {e}")
            
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass
    
    # Main content area
    if uploaded_file is not None and st.session_state.analysis_results is None:
        # Show data preview before analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        display_data_preview(uploaded_file, tmp_file_path)
        
        # Clean up
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        
        # Analysis prompt
        st.markdown("---")
        st.markdown("""
        <div class="preview-card">
            <h3>🚀 Ready for Deep Analysis?</h3>
            <p>Click the <strong>"Analyze Dataset"</strong> button in the sidebar to generate comprehensive AI-powered insights, 
            statistical analysis, and interactive visualizations for your data.</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.analysis_results:
        # Show analysis results
        # Create tabs for different sections
        tab1, tab2 = st.tabs(["📊 Statistics & Visualizations", "🤖 AI Analysis"])
        
        with tab1:
            display_enhanced_statistics(st.session_state.analysis_results)
        
        with tab2:
            display_ai_analysis(st.session_state.analysis_results)
    
    else:
        # Welcome message and instructions
        st.markdown("""
        <div class="card">
            <h2>🎯 Welcome to AI Data Analyzer!</h2>
            <p>This application uses advanced AI to provide comprehensive analysis of your datasets.</p>
            
            <h3>📋 How to use:</h3>
            <ol>
                <li><strong>Upload a CSV file</strong> using the sidebar</li>
                <li><strong>Preview your data</strong> in the main area</li>
                <li><strong>Click "Analyze Dataset"</strong> in the sidebar to generate insights</li>
                <li><strong>Explore the results</strong> in the Statistics and AI Analysis tabs</li>
            </ol>
            
            <h3>✨ Features:</h3>
            <ul>
                <li>📊 Comprehensive descriptive statistics</li>
                <li>🎨 Interactive visualizations</li>
                <li>🤖 AI-powered insights and recommendations</li>
                <li>📈 Pattern identification and trend analysis</li>
                <li>🔍 Data quality assessment</li>
            </ul>
            
            <div class="recommendation-card">
                <h4>💡 Pro Tip:</h4>
                <p>For best results, ensure your dataset is clean and well-structured. Remove any unnecessary columns and handle missing values before uploading.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()