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
    /* Hide dataframe index */
    .dataframe thead th:first-child {
        display: none;
    }
    .dataframe tbody th {
        display: none;
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
    # Título sem ícone - CORREÇÃO: removido completamente o ícone
    st.markdown('<h1 class="main-header">Data Analyzer</h1>', unsafe_allow_html=True)
    
    if uploaded_file:
        # CORREÇÃO: Seção unificada na parte superior
        st.markdown(f"""
        <div class="welcome-card">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="flex: 1;">
                    <h2 style="color: #2ecc71; margin: 0; font-size: 1.5rem;">✅ File Uploaded Successfully!</h2>
                    <p style="font-size: 1rem; margin: 0.5rem 0 0 0;">
                    <strong>File:</strong> {uploaded_file.name}<br>
                    Ready for analysis. Click the <strong>"Analyze Dataset"</strong> button in the sidebar to start.
                    </p>
                </div>
                <div style="margin-left: 1rem; padding: 1rem; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 4px solid #3498db;">
                    <h3 style="font-size: 1.1rem; color: #3498db; margin: 0 0 0.5rem 0;">🚀 Ready for Deep Analysis?</h3>
                    <p style="font-size: 0.9rem; margin: 0;">Click the button in the sidebar to generate AI-powered insights.</p>
                </div>
            </div>
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
    
    # CORREÇÃO: Features em um único card com layout melhorado
    st.markdown("### ✨ Application Features")
    st.markdown("""
    <div class="feature-card">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #3498db;">📊 Descriptive Analysis</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Comprehensive statistical reports and data profiling with detailed metrics and distributions</p>
            </div>
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #2ecc71;">📈 Data Visualization</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Interactive charts, graphs and correlation matrices for all variable types and relationships</p>
            </div>
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #e74c3c;">🤖 AI Insights</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">LLM-powered analysis to uncover hidden patterns, trends and business intelligence</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CORREÇÃO: How to Use e Tips lado a lado com layout melhorado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 How to Use")
        if uploaded_file:
            st.markdown(f"""
            <div class="card">
                <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                    <li style="margin-bottom: 0.8rem;"><strong>✅ File uploaded successfully</strong> - {uploaded_file.name}</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Click "Analyze Dataset"</strong> in the sidebar to start the analysis</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Wait for processing</strong> - the system will generate descriptive statistics and AI insights</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Explore results</strong> in the Exploratory Data Analysis and Insights tabs</li>
                    <li><strong>Download reports</strong> for offline use and documentation</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card">
                <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                    <li style="margin-bottom: 0.8rem;"><strong>Upload your CSV file</strong> using the sidebar uploader</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Click "Analyze Dataset"</strong> to start the analysis process</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Wait for processing</strong> - the system will generate descriptive statistics and AI insights</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Explore results</strong> in the Exploratory Data Analysis and Insights tabs</li>
                    <li><strong>Download reports</strong> for offline use and documentation</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Tips - Layout melhorado
        st.markdown("### 💡 Tips for Best Results")
        st.markdown("""
        <div class="card">
            <ul style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                <li style="margin-bottom: 0.8rem;"><strong>Ensure CSV format</strong> - Properly structured comma-separated values</li>
                <li style="margin-bottom: 0.8rem;"><strong>Clean data first</strong> - Remove unnecessary columns before uploading</li>
                <li style="margin-bottom: 0.8rem;"><strong>Handle missing values</strong> - Address null values when possible</li>
                <li style="margin-bottom: 0.8rem;"><strong>Descriptive headers</strong> - Use clear, meaningful column names</li>
                <li><strong>Size optimization</strong> - Files under 200MB for optimal performance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_column_types_cards(analyzer):
    """Display column types as cards instead of donut chart"""
    simple_types = analyzer.get_simple_column_types()
    
    # Get counts for each type, ensuring zero counts are included
    numerical_count = len(simple_types.get('Numerical', []))
    categorical_count = len(simple_types.get('Categorical', []))
    boolean_count = len(simple_types.get('True/False', []))
    datetime_count = len(simple_types.get('Date/Time', []))
    
    # Display as cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_type_card(numerical_count, "Numerical Columns", "#3498db"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_type_card(categorical_count, "Categorical Columns", "#e74c3c"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_type_card(boolean_count, "True/False Columns", "#2ecc71"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_type_card(datetime_count, "Date/Time Columns", "#f39c12"), unsafe_allow_html=True)

def create_correlation_heatmap(df):
    """Create correlation heatmap for all variables"""
    # Create a copy of the dataframe for encoding
    df_encoded = df.copy()
    
    # Encode categorical variables
    for col in df_encoded.select_dtypes(include=['object', 'category']).columns:
        df_encoded[col] = pd.factorize(df_encoded[col])[0]
    
    # Encode boolean variables
    for col in df_encoded.select_dtypes(include='bool').columns:
        df_encoded[col] = df_encoded[col].astype(int)
    
    # Calculate correlation matrix
    corr_matrix = df_encoded.corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        title="Correlation Matrix (All Variables)",
        color_continuous_scale='RdBu_r',
        aspect="auto",
        range_color=[-1, 1],
        labels=dict(color="Correlation")
    )
    
    fig.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        coloraxis_colorbar=dict(
            title="Correlation",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1.0", "-0.5", "0.0", "0.5", "1.0"]
        )
    )
    
    return fig

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
    
    # Column types as cards
    analyzer = st.session_state.analyzer
    display_column_types_cards(analyzer)
    
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
        # CORREÇÃO: Índice removido usando hide_index=True
        df_display = df.head(10)
        st.dataframe(df_display, use_container_width=True, height=350, hide_index=True)
    
    with col2:
        st.markdown("#### Column Information")
        column_info = analyzer.get_detailed_column_info()
        # CORREÇÃO: Índice removido usando hide_index=True
        st.dataframe(column_info, use_container_width=True, height=350, hide_index=True)
    
    # CORREÇÃO: Correlation heatmap movido para dentro da aba Overview
    st.markdown("### 🔗 Correlation Matrix")
    try:
        corr_fig = create_correlation_heatmap(df)
        st.plotly_chart(corr_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate correlation matrix: {str(e)}")

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
                # Area chart
                chart_data = df[col].dropna()
                if len(chart_data) > 0:
                    hist_values, bin_edges = np.histogram(chart_data, bins=50)
                    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                    
                    fig_area = px.area(
                        x=bin_centers, 
                        y=hist_values, 
                        title=f"Distribution - {col}",
                        labels={'x': col, 'y': 'Frequency'}
                    )
                    
                    fig_area.update_traces(
                        line=dict(color='#3498db', width=2),
                        fillcolor='rgba(52, 152, 219, 0.5)'
                    )
                    
                    fig_area.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        showlegend=False,
                        xaxis_title=col,
                        yaxis_title="Frequency"
                    )
                    
                    st.plotly_chart(fig_area, use_container_width=True)
            
            with viz_col2:
                # Box plot
                fig_box = px.box(df, y=col, title=f"Box Plot - {col}")
                fig_box.update_traces(marker_color='#e74c3c')
                fig_box.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
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
            
            # Bar chart with conditional orientation
            value_counts = df[col].value_counts().head(10)  # Top 10 only
            
            if len(value_counts) <= 5:
                # Horizontal bar chart for 5 or fewer categories
                fig_bar = px.bar(
                    x=value_counts.values,
                    y=value_counts.index,
                    orientation='h',
                    title=f"Top Categories - {col}",
                    color_discrete_sequence=['#3498db']
                )
                fig_bar.update_layout(
                    xaxis_title="Count",
                    yaxis_title="Categories",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
            else:
                # Vertical bar chart for more than 5 categories
                fig_bar = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Top Categories - {col}",
                    color_discrete_sequence=['#3498db']
                )
                fig_bar.update_layout(
                    xaxis_title="Categories",
                    yaxis_title="Count",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
                fig_bar.update_xaxes(tickangle=45)
            
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
            
            col1, col2 = st.columns([1, 2])
            
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
                colors = {'True': 'rgba(46, 204, 113, 0.8)', 'False': 'rgba(231, 76, 60, 0.8)'}
                color_sequence = [colors.get(str(label), '#3498db') for label in value_counts.index]

                fig_donut = px.pie(
                    values=value_counts.values,
                    names=[str(label) for label in value_counts.index],
                    title=f"Distribution - {col}",
                    hole=0.5,
                    color_discrete_sequence=color_sequence
                )
                fig_donut.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    marker=dict(line=dict(color="#000000", width=2)),
                    textfont=dict(color='white', size=14)
                )
                fig_donut.update_layout(
                    height=400,
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig_donut, use_container_width=True)

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
            fig_timeline.update_traces(line=dict(color='#3498db', width=3))
            fig_timeline.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
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
    
    # Improved section extraction
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
        if any(header in line_stripped.lower() for header in ['executive summary', 'summary']):
            current_section = 'Executive Summary'
            continue
        elif any(header in line_stripped.lower() for header in ['detailed statistical analysis', 'statistical analysis']):
            current_section = 'Detailed Statistical Analysis'
            continue
        elif any(header in line_stripped.lower() for header in ['pattern identification', 'pattern analysis', 'patterns']):
            current_section = 'Pattern Identification'
            continue
        elif any(header in line_stripped.lower() for header in ['business/research implications', 'implications', 'business implications', 'research implications']):
            current_section = 'Business/Research Implications'
            continue
        elif any(header in line_stripped.lower() for header in ['recommendations', 'suggestions', 'next steps']):
            current_section = 'Recommendations'
            continue
        
        # Skip empty lines at the beginning of sections
        if current_section and not line_stripped and not sections[current_section]:
            continue
            
        # Add content to current section
        if current_section and line_stripped:
            sections[current_section] += line + '\n'
    
    # Display each section
    section_displayed = False
    for section_name, section_content in sections.items():
        if section_content.strip():
            section_displayed = True
            st.markdown(f'<div class="insight-section">', unsafe_allow_html=True)
            st.markdown(f"### {section_name}")
            st.markdown(section_content)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # If no sections were properly extracted, show the raw analysis
    if not section_displayed:
        st.markdown("""
        <div class="insight-section">
            <h3>Complete Analysis</h3>
            <p>The AI analysis couldn't be parsed into specific sections. Here's the complete analysis:</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="card">{analysis_text}</div>', unsafe_allow_html=True)

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
                            st.error("❌ Analysis failed. Please check your file and try again.")
                        
                        # Clean up temporary file
                        os.unlink(tmp_file_path)
                        
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        st.info("Please check that your CSV file is properly formatted.")
            
            # Clear analysis button
            if st.session_state.analysis_results:
                if st.button("Clear Analysis", type="secondary", use_container_width=True):
                    st.session_state.analysis_results = None
                    st.rerun()
    
    # Main content area
    if uploaded_file is not None and st.session_state.analysis_results is None:
        # Show welcome screen with file uploaded message
        display_welcome_screen(uploaded_file)
    
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