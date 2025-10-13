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
        font-size: 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        padding: 0.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ffffff;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.3rem;
        margin: 1.5rem 0 0.8rem 0;
        font-weight: 700;
    }
    .subsection-header {
        font-size: 1.2rem;
        color: #ffffff;
        margin: 1rem 0 0.8rem 0;
        font-weight: 600;
        background: linear-gradient(90deg, #3498db, transparent);
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
    }
    .card {
        background: #1e2130;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 4px solid #3498db;
        color: #ffffff;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 0.3rem;
    }
    .type-card {
        background: linear-gradient(135deg, #2d3256 0%, #1e2130 100%);
        border-radius: 10px;
        padding: 1.2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 0.3rem;
        border: 1px solid #3498db;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    .welcome-card {
        background: linear-gradient(135deg, #1e2130 0%, #2d3256 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid #3498db;
    }
    .feature-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        border-left: 3px solid #2ecc71;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .upload-card {
        background: linear-gradient(135deg, #1e2130 0%, #2d3256 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 2px dashed #3498db;
        text-align: center;
    }
    .tab-content {
        background: #1e2130;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.8rem 0;
    }
    .download-btn {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        margin: 0.3rem;
        text-decoration: none;
        display: inline-block;
    }
    .download-btn:hover {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        text-decoration: none;
    }
    .analysis-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #e74c3c;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .insight-section {
        background: #2d3256;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #f39c12;
    }
</style>
""", unsafe_allow_html=True)

def create_stat_card(value, label, icon="📊", color="#667eea"):
    return f"""
    <div class="stat-card" style="background: linear-gradient(135deg, {color} 0%, #764ba2 100%);">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def create_type_card(value, label, color="#3498db"):
    return f"""
    <div class="type-card" style="border-color: {color};">
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
            <h2 style="color: #2ecc71; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">✅ File Uploaded Successfully!</h2>
            <p style="font-size: 1rem; text-align: center; margin-bottom: 1rem;">
            <strong>File:</strong> {uploaded_file.name}<br>
            Ready for analysis. Click the <strong>"Analyze Dataset"</strong> button in the sidebar to start.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color: #3498db; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">🎯 Welcome to Data Analyzer!</h2>
            <p style="font-size: 1rem; text-align: center; margin-bottom: 1rem;">
            Advanced AI-powered tool for comprehensive dataset analysis and insights generation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features - More compact layout
    st.markdown("### ✨ Application Features")
    features_col1, features_col2 = st.columns(2)
    
    with features_col1:
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin: 0.5rem 0; font-size: 1rem;">📊 Descriptive Analysis</h4>
            <p style="font-size: 0.9rem; margin: 0;">Comprehensive statistical reports and data profiling</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin: 0.5rem 0; font-size: 1rem;">📈 Data Visualization</h4>
            <p style="font-size: 0.9rem; margin: 0;">Interactive charts and graphs for all variable types</p>
        </div>
        """, unsafe_allow_html=True)
    
    with features_col2:
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin: 0.5rem 0; font-size: 1rem;">🤖 AI Insights</h4>
            <p style="font-size: 0.9rem; margin: 0;">Advanced AI analysis with practical interpretations</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin: 0.5rem 0; font-size: 1rem;">📥 Export Results</h4>
            <p style="font-size: 0.9rem; margin: 0;">Download comprehensive reports in multiple formats</p>
        </div>
        """, unsafe_allow_html=True)

def display_data_overview(analyzer, df):
    """Display comprehensive data overview"""
    st.markdown('<div class="section-header">📋 Dataset Overview</div>', unsafe_allow_html=True)
    
    # Key metrics in a grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_stat_card(f"{df.shape[0]:,}", "Total Rows", "📈", "#3498db"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_stat_card(f"{df.shape[1]}", "Total Columns", "🔧", "#2ecc71"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_stat_card(f"{df.isnull().sum().sum():,}", "Missing Values", "⚠️", "#e74c3c"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_stat_card(f"{df.duplicated().sum():,}", "Duplicate Rows", "🔍", "#f39c12"), unsafe_allow_html=True)
    
    # Data types overview
    st.markdown('<div class="subsection-header">🔧 Data Types Distribution</div>', unsafe_allow_html=True)
    
    column_types = analyzer.get_simple_column_types()
    type_col1, type_col2, type_col3, type_col4 = st.columns(4)
    
    with type_col1:
        st.markdown(create_type_card(len(column_types.get('Numerical', [])), "Numerical", "#3498db"), unsafe_allow_html=True)
    with type_col2:
        st.markdown(create_type_card(len(column_types.get('Categorical', [])), "Categorical", "#2ecc71"), unsafe_allow_html=True)
    with type_col3:
        st.markdown(create_type_card(len(column_types.get('True/False', [])), "True/False", "#e74c3c"), unsafe_allow_html=True)
    with type_col4:
        st.markdown(create_type_card(len(column_types.get('Date/Time', [])), "Date/Time", "#f39c12"), unsafe_allow_html=True)
    
    # Sample data
    st.markdown('<div class="subsection-header">👀 Data Sample</div>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True)

def display_detailed_column_info(analyzer):
    """Display detailed column information"""
    st.markdown('<div class="section-header">🔍 Detailed Column Information</div>', unsafe_allow_html=True)
    
    column_info = analyzer.get_detailed_column_info()
    if not column_info.empty:
        st.dataframe(column_info, use_container_width=True)
    else:
        st.info("No column information available.")

def display_visualizations(analyzer, results):
    """Display interactive visualizations with tabs"""
    st.markdown('<div class="section-header">📊 Data Visualizations</div>', unsafe_allow_html=True)
    
    # Create tabs for different visualization types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "🔢 Numerical", 
        "📝 Categorical", 
        "✅ True/False", 
        "📊 Correlation"
    ])
    
    with tab1:
        display_overview_visualizations(results)
    
    with tab2:
        display_numerical_visualizations(results)
    
    with tab3:
        display_categorical_visualizations(results)
    
    with tab4:
        display_boolean_visualizations(results)
    
    with tab5:
        display_correlation_visualizations(results)

def display_overview_visualizations(results):
    """Display overview visualizations"""
    st.markdown('<div class="subsection-header">📊 Dataset Overview</div>', unsafe_allow_html=True)
    
    viz = results.get('visualizations', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'data_types' in viz:
            st.plotly_chart(viz['data_types'], use_container_width=True)
        else:
            st.info("Data types visualization not available")
    
    with col2:
        if 'missing_data' in viz:
            st.plotly_chart(viz['missing_data'], use_container_width=True)
        else:
            st.info("No missing data found")

def display_numerical_visualizations(results):
    """Display numerical data visualizations"""
    st.markdown('<div class="subsection-header">🔢 Numerical Variables Analysis</div>', unsafe_allow_html=True)
    
    viz = results.get('visualizations', {})
    
    if 'numerical_distributions' in viz:
        st.plotly_chart(viz['numerical_distributions'], use_container_width=True)
    else:
        st.info("No numerical variables found for visualization")
    
    # Additional numerical analysis - Area charts instead of histograms
    df = results.get('dataframe')
    if df is not None:
        numerical_cols = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        
        if len(numerical_cols) > 0:
            st.markdown('<div class="subsection-header">📊 Area Charts - Numerical Distributions</div>', unsafe_allow_html=True)
            
            # Create area charts for numerical variables
            n_cols = min(3, len(numerical_cols))
            n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
            
            for row in range(n_rows):
                cols = st.columns(n_cols)
                for col_idx in range(n_cols):
                    var_idx = row * n_cols + col_idx
                    if var_idx < len(numerical_cols):
                        col_name = numerical_cols[var_idx]
                        with cols[col_idx]:
                            # Create area chart instead of histogram
                            fig = px.area(
                                df, 
                                x=col_name,
                                title=f"Area Chart - {col_name}",
                                color_discrete_sequence=['#3498db']
                            )
                            fig.update_layout(
                                height=300,
                                showlegend=False,
                                xaxis_title=col_name,
                                yaxis_title="Frequency"
                            )
                            st.plotly_chart(fig, use_container_width=True)

def display_categorical_visualizations(results):
    """Display categorical data visualizations"""
    st.markdown('<div class="subsection-header">📝 Categorical Variables Analysis</div>', unsafe_allow_html=True)
    
    viz = results.get('visualizations', {})
    
    if 'categorical_distributions' in viz:
        st.plotly_chart(viz['categorical_distributions'], use_container_width=True)
    else:
        st.info("No categorical variables found for visualization")

def display_boolean_visualizations(results):
    """Display boolean data visualizations"""
    st.markdown('<div class="subsection-header">✅ True/False Variables Analysis</div>', unsafe_allow_html=True)
    
    viz = results.get('visualizations', {})
    
    if 'boolean_distributions' in viz:
        st.plotly_chart(viz['boolean_distributions'], use_container_width=True)
    else:
        st.info("No boolean variables found for visualization")
    
    # Enhanced boolean visualization with custom colors
    df = results.get('dataframe')
    if df is not None:
        boolean_cols = df.select_dtypes(include='bool').columns
        
        if len(boolean_cols) > 0:
            st.markdown('<div class="subsection-header">🎯 Enhanced Boolean Analysis</div>', unsafe_allow_html=True)
            
            n_cols = min(3, len(boolean_cols))
            n_rows = (len(boolean_cols) + n_cols - 1) // n_cols
            
            for row in range(n_rows):
                cols = st.columns(n_cols)
                for col_idx in range(n_cols):
                    var_idx = row * n_cols + col_idx
                    if var_idx < len(boolean_cols):
                        col_name = boolean_cols[var_idx]
                        with cols[col_idx]:
                            # Create donut chart with custom colors
                            value_counts = df[col_name].value_counts()
                            
                            fig = go.Figure(data=[go.Pie(
                                labels=[str(label) for label in value_counts.index],
                                values=value_counts.values,
                                hole=0.6,
                                marker_colors=['#2ecc71', '#e74c3c'],  # Green for True, Red for False
                                textinfo='percent+label',
                                textposition='inside',  # Changed from 'inside' to fix positioning
                                insidetextfont=dict(color='white', size=12, family="Arial Black")  # Fixed: Changed label color to white for better visibility
                            )])
                            
                            fig.update_layout(
                                title=f"Donut Chart - {col_name}",
                                height=300,
                                showlegend=False,
                                annotations=[dict(
                                    text=f"Total: {len(df)}",
                                    x=0.5, y=0.5,
                                    font_size=14,
                                    showarrow=False,
                                    font_color="white"
                                )]
                            )
                            st.plotly_chart(fig, use_container_width=True)

def display_correlation_visualizations(results):
    """Display correlation visualizations"""
    st.markdown('<div class="subsection-header">📊 Correlation Analysis</div>', unsafe_allow_html=True)
    
    viz = results.get('visualizations', {})
    
    if 'correlation_heatmap' in viz:
        # Get the correlation figure
        fig = viz['correlation_heatmap']
        
        # Fix the colorbar title property
        if hasattr(fig.layout, 'coloraxis') and fig.layout.coloraxis:
            # Remove invalid titleside property and use valid title property
            if hasattr(fig.layout.coloraxis.colorbar, '_props'):
                if 'titleside' in fig.layout.coloraxis.colorbar._props:
                    del fig.layout.coloraxis.colorbar._props['titleside']
            
            # Ensure colorbar has a proper title configuration
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title="Correlation",
                    title_font=dict(size=12),
                    tickfont=dict(size=10)
                )
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add correlation interpretation
        st.markdown("""
        <div class="insight-section">
            <h4>🎯 Correlation Interpretation Guide:</h4>
            <ul>
                <li><strong>+1.0</strong>: Perfect positive correlation</li>
                <li><strong>+0.7 to +0.9</strong>: Strong positive correlation</li>
                <li><strong>+0.4 to +0.6</strong>: Moderate positive correlation</li>
                <li><strong>+0.1 to +0.3</strong>: Weak positive correlation</li>
                <li><strong>0</strong>: No correlation</li>
                <li><strong>-0.1 to -0.3</strong>: Weak negative correlation</li>
                <li><strong>-0.4 to -0.6</strong>: Moderate negative correlation</li>
                <li><strong>-0.7 to -0.9</strong>: Strong negative correlation</li>
                <li><strong>-1.0</strong>: Perfect negative correlation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Correlation heatmap requires at least 2 numerical variables")

def display_ai_analysis(results):
    """Display AI analysis results"""
    st.markdown('<div class="section-header">🤖 AI Analysis & Insights</div>', unsafe_allow_html=True)
    
    ai_analysis = results.get('ai_analysis', '')
    
    if ai_analysis:
        # Display in a nice card with markdown
        st.markdown(f"""
        <div class="analysis-card">
            <div style="font-size: 1rem; line-height: 1.6; color: #f8f9fa;">
            {ai_analysis}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("No AI analysis available. Please check the API connection.")

def display_download_section(results, filename):
    """Display download options for analysis results"""
    st.markdown('<div class="section-header">📥 Download Results</div>', unsafe_allow_html=True)
    
    base_name = filename.split('.')[0] if '.' in filename else filename
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stats_content = results.get('statistics', '')
        if stats_content:
            st.markdown(get_download_link(stats_content, f"{base_name}_statistics.md", "📊 Download Statistics"), unsafe_allow_html=True)
    
    with col2:
        ai_content = results.get('ai_analysis', '')
        if ai_content:
            st.markdown(get_download_link(ai_content, f"{base_name}_ai_analysis.md", "🤖 Download AI Analysis"), unsafe_allow_html=True)
    
    with col3:
        combined_content = f"""# Data Analysis Report - {base_name}

## Descriptive Statistics

{results.get('statistics', '')}

## AI Analysis

{results.get('ai_analysis', '')}
"""
        st.markdown(get_download_link(combined_content, f"{base_name}_complete_report.md", "📑 Download Full Report"), unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: #3498db; margin-bottom: 0.5rem;">🔧 Controls</h2>
            <p style="font-size: 0.9rem; color: #bdc3c7;">Upload and analyze your dataset</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload CSV File",
            type=['csv'],
            help="Upload a CSV file for analysis"
        )
        
        if uploaded_file:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Initialize analyzer
            if st.session_state.analyzer is None:
                try:
                    st.session_state.analyzer = ChatBotAnalyzer()
                    st.session_state.df = st.session_state.analyzer.load_and_preview_data(tmp_path)
                    st.success("✅ Dataset loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error initializing analyzer: {e}")
            
            # Analysis button
            if st.button("🚀 Analyze Dataset", type="primary", use_container_width=True):
                if st.session_state.analyzer and st.session_state.df is not None:
                    with st.spinner("🤖 Analyzing dataset... This may take a few moments."):
                        try:
                            st.session_state.results = st.session_state.analyzer.analyze_csv(tmp_path)
                            if st.session_state.results:
                                st.success("✅ Analysis completed successfully!")
                            else:
                                st.error("❌ Analysis failed. Please check your API key and try again.")
                        except Exception as e:
                            st.error(f"❌ Analysis error: {e}")
                else:
                    st.error("❌ Please upload a valid CSV file first.")
            
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <p style="font-size: 0.8rem; color: #7f8c8d;">
            Powered by OpenRouter AI • Built with Streamlit
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    if uploaded_file is None:
        display_welcome_screen()
    else:
        if st.session_state.df is not None:
            display_welcome_screen(uploaded_file)
            
            if st.session_state.results:
                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📋 Overview", 
                    "📊 Visualizations", 
                    "🤖 AI Analysis", 
                    "📥 Export"
                ])
                
                with tab1:
                    display_data_overview(st.session_state.analyzer, st.session_state.df)
                    display_detailed_column_info(st.session_state.analyzer)
                
                with tab2:
                    display_visualizations(st.session_state.analyzer, st.session_state.results)
                
                with tab3:
                    display_ai_analysis(st.session_state.results)
                
                with tab4:
                    display_download_section(st.session_state.results, uploaded_file.name)
            else:
                st.info("👆 Click the 'Analyze Dataset' button in the sidebar to start the analysis.")
        else:
            st.error("❌ Failed to load the dataset. Please check the file format and try again.")

if __name__ == "__main__":
    main()