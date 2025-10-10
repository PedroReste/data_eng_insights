# en_02_interface.py
import streamlit as st
import pandas as pd
import tempfile
import os
import base64
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

# Dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        padding: 1rem;
    }
    .section-header {
        font-size: 2rem;
        color: #ffffff;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
        font-weight: 700;
    }
    .subsection-header {
        font-size: 1.5rem;
        color: #ffffff;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        background: linear-gradient(90deg, #3498db, transparent);
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .card {
        background: #1e2130;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #3498db;
        color: #ffffff;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 0.5rem;
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
    .welcome-card {
        background: linear-gradient(135deg, #1e2130 0%, #2d3256 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        border: 1px solid #3498db;
    }
    .feature-card {
        background: #1e2130;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #2ecc71;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .upload-card {
        background: linear-gradient(135deg, #1e2130 0%, #2d3256 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px dashed #3498db;
        text-align: center;
    }
    .tab-content {
        background: #1e2130;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .download-btn {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        margin: 0.5rem;
    }
    .analysis-card {
        background: #1e2130;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #e74c3c;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .insight-section {
        background: #2d3256;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #f39c12;
    }
</style>
""", unsafe_allow_html=True)

def create_stat_card(value, label, icon="📊", color="#667eea"):
    return f"""
    <div class="stat-card" style="background: linear-gradient(135deg, {color} 0%, #764ba2 100%);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def get_download_link(content, filename, text):
    """Generate a download link for text content"""
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'

def display_welcome_screen(uploaded_file=None):
    """Display welcome screen with app information"""
    st.markdown('<h1 class="main-header">📊 Data Analyzer</h1>', unsafe_allow_html=True)
    
    if uploaded_file:
        st.markdown(f"""
        <div class="welcome-card">
            <h2 style="color: #2ecc71; text-align: center; margin-bottom: 2rem;">✅ File Uploaded Successfully!</h2>
            <p style="font-size: 1.2rem; text-align: center; margin-bottom: 2rem;">
            <strong>File:</strong> {uploaded_file.name}<br>
            Ready for analysis. Click the <strong>"Analyze Dataset"</strong> button in the sidebar to start.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color: #3498db; text-align: center; margin-bottom: 2rem;">🎯 Welcome to Data Analyzer!</h2>
            <p style="font-size: 1.2rem; text-align: center; margin-bottom: 2rem;">
            Advanced AI-powered tool for comprehensive dataset analysis and insights generation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features
    st.markdown("### ✨ Application Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Descriptive Analysis</h4>
            <p>Comprehensive statistical reports and data profiling</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📈 Data Visualization</h4>
            <p>Interactive charts and graphs for all variable types</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Insights</h4>
            <p>LLM-powered analysis to uncover hidden patterns</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How to use
    st.markdown("### 📋 How to Use")
    if uploaded_file:
        st.markdown(f"""
        <div class="card">
            <ol style="font-size: 1.1rem;">
                <li><strong>✅ File uploaded successfully</strong> - {uploaded_file.name}</li>
                <li><strong>Click "Analyze Dataset"</strong> in the sidebar to start the analysis</li>
                <li><strong>Wait for processing</strong> - the system will generate descriptive statistics and AI insights</li>
                <li><strong>Explore results</strong> in the Exploratory Data Analysis and Insights tabs</li>
                <li><strong>Download reports</strong> for offline use</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <ol style="font-size: 1.1rem;">
                <li><strong>Upload your CSV file</strong> using the sidebar uploader</li>
                <li><strong>Click "Analyze Dataset"</strong> to start the analysis process</li>
                <li><strong>Wait for processing</strong> - the system will generate descriptive statistics and AI insights</li>
                <li><strong>Explore results</strong> in the Exploratory Data Analysis and Insights tabs</li>
                <li><strong>Download reports</strong> for offline use</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Tips
    st.markdown("### 💡 Tips for Best Results")
    st.markdown("""
    <div class="card">
        <ul style="font-size: 1.1rem;">
            <li>Ensure your file is properly structured as CSV</li>
            <li>Clean unnecessary columns before uploading</li>
            <li>Handle missing values when possible</li>
            <li>Use descriptive column names</li>
            <li>Files should be under 200MB for optimal performance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def display_exploratory_analysis(results):
    """Display exploratory data analysis with tabs"""
    st.markdown('<div class="section-header">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)
    
    # Download button
    if 'ai_analysis' in results and 'statistics' in results:
        combined_report = f"# Data Analysis Report\n\n## Descriptive Statistics\n\n{results['statistics']}\n\n## AI Analysis\n\n{results['ai_analysis']}"
        st.markdown(get_download_link(combined_report, "complete_analysis_report.txt", "📥 Download Complete Report (TXT)"), unsafe_allow_html=True)
    
    # Overview cards
    df = results['dataframe']
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(create_stat_card(f"{df.shape[0]:,}", "Total Rows", "📈", "#2ecc71"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_stat_card(f"{df.shape[1]}", "Total Columns", "📊", "#3498db"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_stat_card(f"{df.isnull().sum().sum():,}", "Missing Values", "⚠️", "#f39c12"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_stat_card(f"{df.duplicated().sum():,}", "Duplicated Rows", "🔍", "#e74c3c"), unsafe_allow_html=True)
    with col5:
        total_cells = df.shape[0] * df.shape[1]
        st.markdown(create_stat_card(f"{total_cells:,}", "Total Cells", "🔢", "#9b59b6"), unsafe_allow_html=True)
    
    # Donut chart for column types
    analyzer = st.session_state.analyzer
    type_counts = analyzer.get_detailed_column_info()['Type'].value_counts()
    fig_donut = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Column Types Distribution",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(height=400, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_donut, use_container_width=True)
    
    # Create tabs for different data types
    tab_names = ["Overview"]
    simple_types = analyzer.get_simple_column_types()
    
    if simple_types['Numerical']:
        tab_names.append("Numerical Columns")
    if simple_types['Categorical']:
        tab_names.append("Categorical Columns")
    if simple_types['True/False']:
        tab_names.append("True/False Columns")
    if simple_types['Date/Time']:
        tab_names.append("Date/Time Columns")
    
    tabs = st.tabs(tab_names)
    
    # Overview Tab
    with tabs[0]:
        display_overview_tab(results)
    
    # Numerical Columns Tab
    if simple_types['Numerical']:
        tab_index = tab_names.index("Numerical Columns")
        with tabs[tab_index]:
            display_numerical_tab(results)
    
    # Categorical Columns Tab
    if simple_types['Categorical']:
        tab_index = tab_names.index("Categorical Columns")
        with tabs[tab_index]:
            display_categorical_tab(results)
    
    # True/False Columns Tab
    if simple_types['True/False']:
        tab_index = tab_names.index("True/False Columns")
        with tabs[tab_index]:
            display_boolean_tab(results)
    
    # Date/Time Columns Tab
    if simple_types['Date/Time']:
        tab_index = tab_names.index("Date/Time Columns")
        with tabs[tab_index]:
            display_datetime_tab(results)

def display_overview_tab(results):
    """Display overview tab content"""
    df = results['dataframe']
    analyzer = st.session_state.analyzer
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### First 10 Rows")
        st.dataframe(df.head(10), use_container_width=True, height=400)
    
    with col2:
        st.markdown("#### Column Information")
        column_info = analyzer.get_detailed_column_info()
        st.dataframe(column_info, use_container_width=True, height=400)

def display_numerical_tab(results):
    """Display numerical columns analysis"""
    df = results['dataframe']
    numerical_cols = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
    
    for col in numerical_cols:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 📈 {col}")
            
            # Statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mean", f"{df[col].mean():.2f}")
                st.metric("Median", f"{df[col].median():.2f}")
                st.metric("Variance", f"{df[col].var():.2f}")
            with col2:
                st.metric("Standard Deviation", f"{df[col].std():.2f}")
                st.metric("Minimum", f"{df[col].min():.2f}")
                st.metric("Maximum", f"{df[col].max():.2f}")
            
            st.metric("Missing Values", f"{df[col].isnull().sum()}")
            
            # Visualizations
            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                # Histogram
                fig_hist = px.histogram(df, x=col, title=f"Histogram - {col}")
                fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with viz_col2:
                # Box plot
                fig_box = px.box(df, y=col, title=f"Box Plot - {col}")
                fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_categorical_tab(results):
    """Display categorical columns analysis"""
    df = results['dataframe']
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns
    
    for col in categorical_cols:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 🏷️ {col}")
            
            # Statistics
            unique_count = df[col].nunique()
            missing_count = df[col].isnull().sum()
            top_values = df[col].value_counts().head(3)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Unique Categories", unique_count)
                st.metric("Missing Values", missing_count)
            
            with col2:
                st.markdown("**Top 3 Categories:**")
                for value, count in top_values.items():
                    st.write(f"- `{value}`: {count} occurrences")
            
            # Bar chart
            value_counts = df[col].value_counts().head(10)  # Top 10 only
            fig_bar = px.bar(
                x=value_counts.values,
                y=value_counts.index,
                orientation='h',
                title=f"Top Categories - {col}",
                color=value_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(
                xaxis_title="Count",
                yaxis_title="Categories",
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_boolean_tab(results):
    """Display boolean columns analysis"""
    df = results['dataframe']
    boolean_cols = df.select_dtypes(include='bool').columns
    
    for col in boolean_cols:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### ✅ {col}")
            
            value_counts = df[col].value_counts()
            percentages = df[col].value_counts(normalize=True) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Metrics
                for val, count in value_counts.items():
                    percentage = percentages[val]
                    st.metric(
                        f"{val} Count", 
                        f"{count} ({percentage:.1f}%)"
                    )
            
            with col2:
                # Donut chart
                fig_donut = px.pie(
                    values=value_counts.values,
                    names=[str(label) for label in value_counts.index],
                    title=f"Distribution - {col}",
                    hole=0.6
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut.update_layout(height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_donut, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_datetime_tab(results):
    """Display datetime columns analysis"""
    df = results['dataframe']
    datetime_cols = df.select_dtypes(include=['datetime64']).columns
    
    for col in datetime_cols:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 📅 {col}")
            
            # Statistics
            min_date = df[col].min()
            max_date = df[col].max()
            date_range = max_date - min_date
            
            # Most frequent date
            date_counts = df[col].value_counts()
            most_frequent_date = date_counts.index[0] if len(date_counts) > 0 else None
            most_frequent_count = date_counts.iloc[0] if len(date_counts) > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Earliest Date", min_date.strftime('%Y-%m-%d'))
                st.metric("Latest Date", max_date.strftime('%Y-%m-%d'))
                st.metric("Date Range", f"{date_range.days} days")
            
            with col2:
                if most_frequent_date:
                    st.metric("Most Frequent Date", most_frequent_date.strftime('%Y-%m-%d'))
                    st.metric("Frequency", most_frequent_count)
            
            # Timeline chart
            timeline_data = df[col].value_counts().sort_index()
            fig_timeline = px.line(
                x=timeline_data.index,
                y=timeline_data.values,
                title=f"Timeline - {col}",
                labels={'x': 'Date', 'y': 'Record Count'}
            )
            fig_timeline.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_llm_insights(results):
    """Display LLM analysis with structured sections"""
    st.markdown('<div class="section-header">🤖 Insights Generated</div>', unsafe_allow_html=True)
    
    # Download button
    if 'ai_analysis' in results and 'statistics' in results:
        combined_report = f"# Data Analysis Report\n\n## Descriptive Statistics\n\n{results['statistics']}\n\n## AI Analysis\n\n{results['ai_analysis']}"
        st.markdown(get_download_link(combined_report, "complete_analysis_report.txt", "📥 Download Complete Report (TXT)"), unsafe_allow_html=True)
    
    if 'ai_analysis' not in results or not results['ai_analysis']:
        st.error("No AI analysis available. Please run the analysis first.")
        return
    
    analysis_text = results['ai_analysis']
    
    # Extract sections based on the prompt structure
    sections = {
        'Executive Summary': '',
        'Detailed Statistical Analysis': '',
        'Pattern Identification': '',
        'Business/Research Implications': '',
        'Recommendations': ''
    }
    
    current_section = None
    lines = analysis_text.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if this line starts a new section
        if line_stripped.lower().startswith('# executive summary'):
            current_section = 'Executive Summary'
            continue
        elif line_stripped.lower().startswith('## detailed statistical analysis') or line_stripped.lower().startswith('# detailed statistical analysis'):
            current_section = 'Detailed Statistical Analysis'
            continue
        elif line_stripped.lower().startswith('## pattern identification') or line_stripped.lower().startswith('# pattern identification'):
            current_section = 'Pattern Identification'
            continue
        elif line_stripped.lower().startswith('## business/research implications') or line_stripped.lower().startswith('# business/research implications'):
            current_section = 'Business/Research Implications'
            continue
        elif line_stripped.lower().startswith('## recommendations') or line_stripped.lower().startswith('# recommendations'):
            current_section = 'Recommendations'
            continue
        
        # Add content to current section
        if current_section and line_stripped:
            sections[current_section] += line + '\n'
    
    # Display each section
    for section_name, section_content in sections.items():
        if section_content.strip():
            st.markdown(f'<div class="insight-section">', unsafe_allow_html=True)
            st.markdown(f"### {section_name}")
            st.markdown(section_content)
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analyzer' not in st.session_state:
        try:
            st.session_state.analyzer = ChatBotAnalyzer()
        except Exception as e:
            st.error(f"❌ Failed to initialize analyzer: {e}")
            st.info("Please make sure your OpenRouter API key is properly configured.")
            return
    
    # Sidebar for file upload
    with st.sidebar:
        st.markdown("## 📁 Upload Dataset")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload your dataset in CSV format"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Analysis button
            st.markdown("## 🚀 Start Analysis")
            if st.button("Analyze Dataset", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing dataset... This may take a few moments."):
                    try:
                        # Save uploaded file to temporary location
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Run analysis
                        results = st.session_state.analyzer.analyze_csv(tmp_file_path)
                        
                        if results:
                            st.session_state.analysis_results = results
                            st.session_state.uploaded_file_name = uploaded_file.name
                            st.success("✅ Analysis completed successfully!")
                        else:
                            st.error("❌ Analysis failed. Please check your API key and try again.")
                        
                        # Clean up
                        os.unlink(tmp_file_path)
                        
                    except Exception as e:
                        st.error(f"❌ Analysis error: {e}")
    
    # Main content area
    if uploaded_file is not None and st.session_state.analysis_results is None:
        # Show welcome screen with file uploaded message
        display_welcome_screen(uploaded_file)
        
        # Analysis prompt
        st.markdown("---")
        st.markdown("""
        <div class="upload-card">
            <h3>🚀 Ready for Deep Analysis?</h3>
            <p>Click the <strong>"Analyze Dataset"</strong> button in the sidebar to generate comprehensive AI-powered insights.</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.analysis_results:
        # Show analysis results in tabs
        tab1, tab2 = st.tabs(["📊 Exploratory Data Analysis", "🤖 Insights Generated"])
        
        with tab1:
            display_exploratory_analysis(st.session_state.analysis_results)
        
        with tab2:
            display_llm_insights(st.session_state.analysis_results)
    
    else:
        # Welcome screen
        display_welcome_screen()

if __name__ == "__main__":
    main()