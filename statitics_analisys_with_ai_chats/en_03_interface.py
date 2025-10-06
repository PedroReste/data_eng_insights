# en_03_interface.py
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
from en_02_api_key_reader import read_api_key_from_content

# Set page configuration
st.set_page_config(
    page_title="Data Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with beautiful styling for results
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
</style>
""", unsafe_allow_html=True)

def create_stat_card(value, label, icon="📊", color="#667eea"):
    """Create a beautiful statistic card"""
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

def display_enhanced_statistics(results):
    """Display statistics in a highly visual and organized way"""
    st.markdown('<div class="section-header">📊 Enhanced Statistics Dashboard</div>', unsafe_allow_html=True)
    
    # Parse the statistics text
    stats_text = results['statistics']
    
    # Display dataset overview in a beautiful grid
    display_dataset_overview(stats_text)
    
    # Display data types summary
    display_data_types_summary(stats_text)
    
    # Display variables in organized tabs
    display_variables_analysis(stats_text)

def display_dataset_overview(stats_text):
    """Display dataset overview with beautiful metrics"""
    st.markdown("### 📋 Dataset Overview")
    
    # Extract overview metrics
    overview_lines = stats_text.split('## 📋 Dataset Overview')[1].split('## 🔧 Data Types Summary')[0].strip().split('\n')
    metrics = {}
    
    for line in overview_lines:
        if '**' in line:
            key = line.split('**')[1]
            value = line.split('**')[-2] if '**' in line.split('**')[-2] else line.split('**')[-1]
            metrics[key.lower().replace(' ', '_')] = value
    
    # Create metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_stat_card(
            metrics.get('total_rows', 'N/A'), 
            "Total Rows", 
            "📈", 
            "#e74c3c"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_stat_card(
            metrics.get('total_columns', 'N/A'), 
            "Total Columns", 
            "🔧", 
            "#3498db"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_stat_card(
            metrics.get('missing_values', 'N/A'), 
            "Missing Values", 
            "⚠️", 
            "#f39c12"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_stat_card(
            metrics.get('duplicate_rows', 'N/A'), 
            "Duplicate Rows", 
            "🔍", 
            "#2ecc71"
        ), unsafe_allow_html=True)

def display_data_types_summary(stats_text):
    """Display data types summary with visual tags"""
    st.markdown("### 🔧 Data Types Distribution")
    
    # Extract data types
    dtype_section = stats_text.split('## 🔧 Data Types Summary')[1].split('## 🔢 Numerical Variables')[0].strip()
    dtype_lines = [line for line in dtype_section.split('\n') if '**' in line]
    
    # Create a beautiful data types display
    cols = st.columns(len(dtype_lines))
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    
    for i, line in enumerate(dtype_lines):
        if '**' in line:
            dtype = line.split('**')[1]
            count = line.split('**')[-2] if '**' in line.split('**')[-2] else line.split('**')[-1]
            with cols[i % len(cols)]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: {colors[i % len(colors)]}; 
                         color: white; border-radius: 10px; margin: 0.5rem;">
                    <div style="font-size: 1.2rem; font-weight: bold;">{count}</div>
                    <div style="font-size: 0.9rem;">{dtype}</div>
                </div>
                """, unsafe_allow_html=True)

def display_variables_analysis(stats_text):
    """Display variables analysis in organized tabs"""
    st.markdown("### 📈 Variables Analysis")
    
    tab1, tab2, tab3 = st.tabs(["🔢 Numerical Variables", "📝 Categorical Variables", "✅ Boolean Variables"])
    
    with tab1:
        display_numerical_variables(stats_text)
    
    with tab2:
        display_categorical_variables(stats_text)
    
    with tab3:
        display_boolean_variables(stats_text)

def display_numerical_variables(stats_text):
    """Display numerical variables with enhanced visualization"""
    if '## 🔢 Numerical Variables' not in stats_text:
        st.info("No numerical variables found in the dataset.")
        return
    
    numerical_section = stats_text.split('## 🔢 Numerical Variables')[1]
    if '## 📝 Categorical Variables' in numerical_section:
        numerical_section = numerical_section.split('## 📝 Categorical Variables')[0]
    
    variables = numerical_section.split('### 📈 ')[1:]
    
    for var_content in variables:
        if var_content.strip():
            lines = var_content.split('\n')
            var_name = lines[0].strip()
            
            # Extract statistics
            stats = {}
            for line in lines[1:]:
                if ':**' in line:
                    key = line.split(':**')[0].replace('- **', '').strip()
                    value = line.split(':**')[1].strip()
                    stats[key] = value
            
            st.markdown(f'<div class="variable-card">', unsafe_allow_html=True)
            
            # Variable header
            st.markdown(f"#### 📈 {var_name}")
            
            # Create a grid for statistics
            col1, col2 = st.columns(2)
            
            with col1:
                # Central tendency metrics
                if 'Mean' in stats:
                    st.metric("📊 Mean", stats['Mean'])
                if 'Median' in stats:
                    st.metric("🎯 Median", stats['Median'])
                if 'Standard Deviation' in stats:
                    st.metric("📐 Std Dev", stats['Standard Deviation'])
            
            with col2:
                # Range metrics
                if 'Minimum' in stats:
                    st.metric("📉 Minimum", stats['Minimum'])
                if 'Maximum' in stats:
                    st.metric("📈 Maximum", stats['Maximum'])
                if 'Range' in stats:
                    st.metric("📏 Range", stats['Range'])
            
            # Additional metrics in expander
            with st.expander("View Detailed Metrics"):
                col3, col4 = st.columns(2)
                with col3:
                    if 'Variance' in stats:
                        st.metric("📊 Variance", stats['Variance'])
                with col4:
                    if 'Missing Values' in stats:
                        st.metric("⚠️ Missing", stats['Missing Values'])
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_categorical_variables(stats_text):
    """Display categorical variables with enhanced visualization"""
    if '## 📝 Categorical Variables' not in stats_text:
        st.info("No categorical variables found in the dataset.")
        return
    
    categorical_section = stats_text.split('## 📝 Categorical Variables')[1]
    if '## ✅ Boolean Variables' in categorical_section:
        categorical_section = categorical_section.split('## ✅ Boolean Variables')[0]
    
    variables = categorical_section.split('### 🏷️ ')[1:]
    
    for var_content in variables:
        if var_content.strip():
            lines = var_content.split('\n')
            var_name = lines[0].strip()
            
            # Extract information
            info = {}
            top_values = []
            current_section = None
            
            for line in lines[1:]:
                if '**Unique Values**' in line:
                    info['unique'] = line.split('**')[-2]
                elif '**Missing Values**' in line:
                    info['missing'] = line.split('**')[-2]
                elif 'Top 3 Values' in line:
                    current_section = 'top_values'
                elif current_section == 'top_values' and '`' in line:
                    value_part = line.split('`')[1]
                    value = value_part.split(':')[0]
                    count = value_part.split(':')[1].split(' occurrences')[0].strip()
                    top_values.append((value, count))
            
            st.markdown(f'<div class="categorical-card">', unsafe_allow_html=True)
            
            # Variable header
            st.markdown(f"#### 🏷️ {var_name}")
            
            # Basic info
            col1, col2 = st.columns(2)
            with col1:
                if 'unique' in info:
                    st.metric("🎯 Unique Values", info['unique'])
            with col2:
                if 'missing' in info:
                    st.metric("⚠️ Missing Values", info['missing'])
            
            # Top values visualization
            if top_values:
                st.markdown("##### 🏆 Top Values Distribution")
                total_occurrences = sum(int(count.replace(',', '')) for _, count in top_values)
                
                for value, count in top_values:
                    count_num = int(count.replace(',', ''))
                    percentage = (count_num / total_occurrences) * 100
                    
                    st.markdown(f"""
                    <div style="margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: between; margin-bottom: 0.2rem;">
                            <span style="font-weight: 600;">{value}</span>
                            <span>{count} ({percentage:.1f}%)</span>
                        </div>
                        <div class="distribution-bar" style="width: {percentage}%">
                            <span>{value}</span>
                            <span>{percentage:.1f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_boolean_variables(stats_text):
    """Display boolean variables with enhanced visualization"""
    if '## ✅ Boolean Variables' not in stats_text:
        st.info("No boolean variables found in the dataset.")
        return
    
    boolean_section = stats_text.split('## ✅ Boolean Variables')[1]
    variables = boolean_section.split('### 🔘 ')[1:]
    
    for var_content in variables:
        if var_content.strip():
            lines = var_content.split('\n')
            var_name = lines[0].strip()
            
            # Extract distribution
            distribution = {}
            current_section = None
            
            for line in lines[1:]:
                if '**Distribution**' in line:
                    current_section = 'distribution'
                elif current_section == 'distribution' and '`' in line:
                    value_part = line.split('`')[1]
                    value = value_part.split(':')[0]
                    count_percentage = value_part.split(':')[1].strip()
                    count = count_percentage.split(' (')[0]
                    percentage = count_percentage.split(' (')[1].replace('%)', '')
                    distribution[value] = {'count': count, 'percentage': percentage}
            
            st.markdown(f'<div class="boolean-card">', unsafe_allow_html=True)
            
            # Variable header
            st.markdown(f"#### 🔘 {var_name}")
            
            # Distribution visualization
            if distribution:
                st.markdown("##### 📊 Value Distribution")
                
                for value, data in distribution.items():
                    percentage = float(data['percentage'])
                    color = "#2ecc71" if value == "True" else "#e74c3c"
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="margin: 0.5rem 0;">
                            <div style="display: flex; justify-content: between; margin-bottom: 0.2rem;">
                                <span style="font-weight: 600; color: {color};">{value}</span>
                            </div>
                            <div class="progress-bar" style="width: {percentage}%; background: {color};"></div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.metric("", f"{percentage}%")
            
            # Additional metrics in expander
            with st.expander("View Technical Metrics"):
                col3, col4 = st.columns(2)
                with col3:
                    # Extract variance and std dev
                    for line in lines:
                        if '**Variance**' in line:
                            variance = line.split('**')[-2]
                            st.metric("📊 Variance", variance)
                        elif '**Standard Deviation**' in line:
                            std_dev = line.split('**')[-2]
                            st.metric("📐 Std Dev", std_dev)
                
                with col4:
                    for line in lines:
                        if '**Missing Values**' in line:
                            missing = line.split('**')[-2]
                            st.metric("⚠️ Missing", missing)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_enhanced_ai_analysis(results):
    """Display AI analysis in a highly visual and organized way"""
    st.markdown('<div class="section-header">🤖 AI-Powered Insights</div>', unsafe_allow_html=True)
    
    analysis_text = results['ai_analysis']
    sections = parse_ai_analysis_enhanced(analysis_text)
    
    # Display each section in an organized way
    for section_title, section_content in sections.items():
        if section_content.strip():
            if section_title.lower() in ['executive summary', 'overview']:
                display_executive_summary_section(section_title, section_content)
            elif 'recommendation' in section_title.lower():
                display_recommendation_section(section_title, section_content)
            elif 'pattern' in section_title.lower() or 'insight' in section_title.lower():
                display_insight_section(section_title, section_content)
            else:
                display_general_section(section_title, section_content)

def parse_ai_analysis_enhanced(analysis_text):
    """Enhanced parsing of AI analysis with better section detection"""
    sections = {}
    current_section = "Executive Summary"
    current_content = []
    
    lines = analysis_text.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        
        # Detect section headers
        if line_stripped.startswith('# ') and len(line_stripped) > 3:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line_stripped[2:].strip()
            current_content = []
        elif line_stripped.startswith('## ') and len(line_stripped) > 3:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line_stripped[3:].strip()
            current_content = []
        elif line_stripped and not line_stripped.startswith('---'):
            current_content.append(line_stripped)
    
    # Add the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def display_executive_summary_section(title, content):
    """Display executive summary with highlight cards"""
    st.markdown(f'<div class="ai-insight-card">', unsafe_allow_html=True)
    st.markdown(f"### 📄 {title}")
    
    # Split content into key points
    points = re.split(r'[•\-]\s+', content)
    key_points = [p.strip() for p in points if len(p.strip()) > 20][:4]  # Top 4 key points
    
    for i, point in enumerate(key_points):
        if point:
            # Extract numbers for highlighting
            highlighted_point = re.sub(r'(\d+\.?\d*)', r'<span class="highlight-number">\1</span>', point)
            st.markdown(f"**{i+1}.** {highlighted_point}", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_recommendation_section(title, content):
    """Display recommendations with action cards"""
    st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
    st.markdown(f"### 💡 {title}")
    
    # Split into individual recommendations
    recommendations = re.split(r'\d+\.|\n-|\n•', content)
    recommendations = [r.strip() for r in recommendations if len(r.strip()) > 10]
    
    for i, rec in enumerate(recommendations[:6]):  # Show top 6 recommendations
        if rec:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.7); padding: 1rem; margin: 0.5rem 0; 
                     border-radius: 8px; border-left: 4px solid #3498db;">
                <div style="display: flex; align-items: start;">
                    <div style="background: #3498db; color: white; border-radius: 50%; 
                             width: 25px; height: 25px; display: flex; align-items: center; 
                             justify-content: center; margin-right: 1rem; font-weight: bold;">
                        {i+1}
                    </div>
                    <div style="flex: 1;">
                        {rec}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_insight_section(title, content):
    """Display insights with visual emphasis"""
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### 🔍 {title}")
    
    # Format insights with better readability
    insights = re.split(r'[•\-]\s+', content)
    
    for insight in insights:
        if len(insight.strip()) > 10:
            # Highlight key phrases
            insight_highlighted = re.sub(
                r'(significantly|important|notable|key finding|major|critical)',
                r'**\1**',
                insight,
                flags=re.IGNORECASE
            )
            st.markdown(f"• {insight_highlighted}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_general_section(title, content):
    """Display general sections in a clean format"""
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### 📋 {title}")
    st.markdown(content)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Header with modern design
    st.markdown('<h1 class="main-header">🚀 AI Data Analyzer Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar configuration (keep your existing sidebar code)
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key Section
        st.markdown("#### 🔑 API Setup")
        api_method = st.radio(
            "Authentication Method:",
            ["Upload Key File", "Enter Key Directly"],
            horizontal=True
        )
        
        api_key = None
        
        if api_method == "Upload Key File":
            api_file = st.file_uploader("Upload API Key File", type=['txt'], help="TXT file with 'open_router:your_key' format")
            if api_file:
                content = api_file.read().decode('utf-8')
                api_key = read_api_key_from_content(content)
                if api_key:
                    st.success("✅ API Key Verified")
        
        else:
            api_key = st.text_input("Enter OpenRouter API Key:", type="password", 
                                  help="Your OpenRouter API key starting with 'sk-or-v1-'")
            if api_key:
                st.success("✅ API Key Entered")
        
        st.markdown("---")
        
        # File Upload Section
        st.markdown("#### 📁 Data Source")
        uploaded_file = st.file_uploader("Upload CSV File", type=['csv'], 
                                       help="Upload your dataset for analysis")
    
    # Main content area
    if uploaded_file is not None and api_key:
        try:
            # Perform analysis when button is clicked
            if st.button("🚀 Launch Comprehensive Analysis", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is analyzing your data... This may take a few moments."):
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name
                    
                    try:
                        # Perform full analysis
                        analyzer = ChatBotAnalyzer(api_key)
                        results = analyzer.analyze_csv(temp_path, save_output=False)
                        
                        if results:
                            st.balloons()
                            st.success("🎉 Analysis Complete!")
                            
                            # Display enhanced statistics
                            display_enhanced_statistics(results)
                            
                            # Display enhanced AI analysis
                            display_enhanced_ai_analysis(results)
                            
                            # Download section
                            st.markdown('<div class="section-header">💾 Export Results</div>', unsafe_allow_html=True)
                            
                            col1, col2, col3 = st.columns(3)
                            base_name = os.path.splitext(uploaded_file.name)[0]
                            
                            with col1:
                                st.download_button(
                                    label="📊 Download Statistics",
                                    data=results['statistics'],
                                    file_name=f"{base_name}_statistics.md",
                                    mime="text/markdown",
                                    use_container_width=True
                                )
                            
                            with col2:
                                st.download_button(
                                    label="🤖 Download AI Insights",
                                    data=results['ai_analysis'],
                                    file_name=f"{base_name}_ai_insights.md",
                                    mime="text/markdown",
                                    use_container_width=True
                                )
                            
                            with col3:
                                combined = f"# Comprehensive Analysis Report\n\n## Statistics\n\n{results['statistics']}\n\n## AI Insights\n\n{results['ai_analysis']}"
                                st.download_button(
                                    label="📄 Download Full Report",
                                    data=combined,
                                    file_name=f"{base_name}_full_report.md",
                                    mime="text/markdown",
                                    use_container_width=True
                                )
                        
                        else:
                            st.error("❌ Analysis failed. Please check your API key.")
                    
                    except Exception as e:
                        st.error(f"❌ Analysis error: {str(e)}")
                    
                    finally:
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
            else:
                # Show preview before analysis
                st.info("👆 Click the button above to start the AI analysis and see enhanced visual results!")
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    elif not uploaded_file:
        display_welcome_screen()
    elif not api_key:
        st.warning("⚠️ Please configure your API key to enable AI analysis.")

def display_welcome_screen():
    """Display welcome screen"""
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;">
        <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">🎯 Welcome to AI Data Analyzer Pro</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Upload your CSV file and unlock powerful insights with enhanced visualization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features with enhanced styling
    st.markdown("### ✨ Enhanced Visualization Features")
    
    features = [
        {"icon": "📊", "title": "Beautiful Statistics", "desc": "Color-coded metrics and interactive charts"},
        {"icon": "🔍", "title": "Enhanced Insights", "desc": "AI-powered analysis with visual emphasis"},
        {"icon": "🎨", "title": "Modern UI", "desc": "Clean, organized sections with progress bars"},
        {"icon": "💡", "title": "Actionable Recommendations", "desc": "Priority-based suggestions with visual cues"}
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card">
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">{feature['icon']}</div>
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">{feature['title']}</h4>
                    <p style="color: #7f8c8d; font-size: 0.9rem;">{feature['desc']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()