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

# NEW: Importações para geração de PDF
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        Image, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import plotly.io as pio
    from PIL import Image as PILImage
    import io
    import tempfile
    import base64
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    print(f"ReportLab não disponível: {e}")
    REPORTLAB_AVAILABLE = False

# Set page configuration
st.set_page_config(
    page_title="Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS with print optimization
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
    .pdf-btn {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        margin: 0.3rem;
        text-decoration: none;
        display: inline-block;
        font-size: 1rem;
    }
    .pdf-btn:hover {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        color: white;
        text-decoration: none;
    }

    /* Print Styles - Essential for PDF generation */
    @media print {
        /* Reset for printing */
        * {
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        
        .stApp {
            background: white !important;
            color: black !important;
        }
        
        /* Hide elements that shouldn't be printed */
        .stButton, 
        .stDownloadButton, 
        .stFileUploader,
        .stSidebar,
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        .element-container:has(button),
        .st-emotion-cache-1r6slb0,
        .st-emotion-cache-1y4p8pa,
        .no-print {
            display: none !important;
        }
        
        /* Main content adjustments */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            -webkit-background-clip: initial !important;
            -webkit-text-fill-color: white !important;
            color: white !important;
            background-clip: initial !important;
            text-fill-color: white !important;
            font-size: 2rem !important;
            padding: 1rem !important;
            margin-bottom: 1rem !important;
        }
        
        .section-header {
            color: #2c3e50 !important;
            border-bottom: 2px solid #3498db !important;
            font-size: 1.3rem !important;
            margin: 1rem 0 0.5rem 0 !important;
        }
        
        .card, .stat-card, .analysis-card, .insight-section {
            background: white !important;
            color: black !important;
            border: 1px solid #ddd !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            page-break-inside: avoid !important;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
        
        /* Ensure proper page breaks */
        .analysis-card, .insight-section {
            page-break-inside: avoid;
            break-inside: avoid;
        }
        
        /* Plotly charts */
        .js-plotly-plot, .plotly-graph-div {
            page-break-inside: avoid !important;
            max-width: 100% !important;
        }
        
        /* Dataframes */
        .dataframe {
            page-break-inside: avoid !important;
            font-size: 10px !important;
        }
        
        /* Layout adjustments for printing */
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
        
        /* Force A4 page size */
        @page {
            size: A4;
            margin: 1cm;
        }
        
        body {
            margin: 0 !important;
            padding: 0 !important;
        }
    }

    /* Print-specific elements (hidden on screen) */
    .print-only {
        display: none;
    }
    
    @media print {
        .print-only {
            display: block !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FUNÇÕES AUXILIARES PARA PDF
# =============================================================================

def export_plotly_figure(fig, width=800, height=400):
    """Export Plotly figure to PNG bytes"""
    try:
        # Converter figura Plotly para imagem PNG
        img_bytes = pio.to_image(fig, format='png', width=width, height=height)
        return img_bytes
    except Exception as e:
        print(f"Erro ao exportar figura Plotly: {e}")
        return None

def create_statistics_table(df):
    """Create a formatted statistics table for the PDF"""
    # Basic statistics
    data = [
        ['Metric', 'Value'],
        ['Total Rows', f"{df.shape[0]:,}"],
        ['Total Columns', f"{df.shape[1]}"],
        ['Total Cells', f"{df.shape[0] * df.shape[1]:,}"],
        ['Missing Values', f"{df.isnull().sum().sum():,}"],
        ['Duplicate Rows', f"{df.duplicated().sum():,}"],
        ['Memory Usage', f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"]
    ]
    
    return data

def create_column_types_table(analyzer):
    """Create column types summary table"""
    simple_types = analyzer.get_simple_column_types()
    
    data = [['Data Type', 'Count']]
    for col_type, columns in simple_types.items():
        if columns:  # Only include types that have columns
            data.append([col_type, str(len(columns))])
    
    return data

def create_numerical_stats_table(df):
    """Create numerical statistics summary"""
    numerical_cols = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
    
    if len(numerical_cols) == 0:
        return None
    
    data = [['Column', 'Mean', 'Std Dev', 'Min', 'Max', 'Missing']]
    
    for col in numerical_cols[:10]:  # Limit to first 10 columns
        data.append([
            col,
            f"{df[col].mean():.2f}",
            f"{df[col].std():.2f}",
            f"{df[col].min():.2f}",
            f"{df[col].max():.2f}",
            f"{df[col].isnull().sum()}"
        ])
    
    return data

def generate_pdf_with_reportlab(results, dataset_name):
    """Generate comprehensive PDF report with charts using ReportLab"""
    if not REPORTLAB_AVAILABLE:
        st.error("ReportLab não está disponível. Instale com: pip install reportlab")
        return None
    
    try:
        # Create buffer for PDF
        buffer = io.BytesIO()
        
        # Setup document with margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=f"Data Analysis Report - {dataset_name}"
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#3498db'),
            alignment=TA_LEFT
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Story elements
        story = []
        
        # Title Page
        story.append(Paragraph("DATA ANALYSIS REPORT", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Dataset: {dataset_name}", heading1_style))
        story.append(Paragraph(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 40))
        story.append(Paragraph("Generated by AI Data Analyzer", normal_style))
        
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", heading1_style))
        story.append(Spacer(1, 10))
        
        toc_items = [
            "1. Executive Summary",
            "2. Dataset Overview", 
            "3. Data Types Summary",
            "4. Numerical Analysis",
            "5. Visualizations",
            "6. AI Insights Summary"
        ]
        
        for item in toc_items:
            story.append(Paragraph(item, normal_style))
        
        story.append(PageBreak())
        
        # 1. Executive Summary
        story.append(Paragraph("1. Executive Summary", heading1_style))
        story.append(Spacer(1, 10))
        
        df = results['dataframe']
        exec_summary = f"""
        This report provides a comprehensive analysis of the dataset '{dataset_name}' 
        containing {df.shape[0]:,} rows and {df.shape[1]} columns. The analysis includes 
        descriptive statistics, data quality assessment, and AI-powered insights to 
        help understand patterns and relationships within the data.
        """
        story.append(Paragraph(exec_summary, normal_style))
        story.append(Spacer(1, 15))
        
        # 2. Dataset Overview
        story.append(Paragraph("2. Dataset Overview", heading1_style))
        story.append(Spacer(1, 10))
        
        # Basic statistics table
        stats_data = create_statistics_table(df)
        stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # 3. Data Types Summary
        story.append(Paragraph("3. Data Types Summary", heading1_style))
        story.append(Spacer(1, 10))
        
        analyzer = st.session_state.analyzer
        type_data = create_column_types_table(analyzer)
        if type_data and len(type_data) > 1:
            type_table = Table(type_data, colWidths=[2.5*inch, 1.5*inch])
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(type_table)
        else:
            story.append(Paragraph("No column type information available.", normal_style))
        
        story.append(Spacer(1, 20))
        
        # 4. Numerical Analysis
        numerical_data = create_numerical_stats_table(df)
        if numerical_data and len(numerical_data) > 1:
            story.append(Paragraph("4. Numerical Columns Summary", heading1_style))
            story.append(Spacer(1, 10))
            
            # Use smaller font for numerical table if many columns
            num_table = Table(numerical_data, colWidths=[1.2*inch] + [0.8*inch]*5)
            num_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ROWBREAKS', (0, 0), (-1, -1), 10),  # Page break every 10 rows
            ]))
            story.append(num_table)
            story.append(Spacer(1, 20))
        
        story.append(PageBreak())
        
        # 5. Visualizations
        story.append(Paragraph("5. Data Visualizations", heading1_style))
        story.append(Spacer(1, 10))
        
        # Export and include Plotly figures as images
        visualizations = results.get('visualizations', {})
        if visualizations:
            for viz_name, fig in visualizations.items():
                try:
                    story.append(Paragraph(f"Chart: {viz_name.replace('_', ' ').title()}", heading2_style))
                    
                    # Export Plotly figure to PNG
                    img_bytes = export_plotly_figure(fig, width=600, height=400)
                    if img_bytes:
                        # Save to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                            tmp_file.write(img_bytes)
                            tmp_path = tmp_file.name
                        
                        # Add image to PDF
                        img = Image(tmp_path, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 10))
                        
                        # Clean up
                        os.unlink(tmp_path)
                    else:
                        story.append(Paragraph("Could not generate chart image.", normal_style))
                    
                    # Add page break after every 2 charts
                    if list(visualizations.keys()).index(viz_name) % 2 == 1:
                        story.append(PageBreak())
                        
                except Exception as e:
                    story.append(Paragraph(f"Error including chart {viz_name}: {str(e)}", normal_style))
                    continue
        else:
            story.append(Paragraph("No visualizations available.", normal_style))
        
        story.append(PageBreak())
        
        # 6. AI Insights Summary
        story.append(Paragraph("6. AI Insights Summary", heading1_style))
        story.append(Spacer(1, 10))
        
        if 'ai_analysis' in results and results['ai_analysis']:
            # Truncate AI analysis if too long, but include key sections
            ai_text = results['ai_analysis']
            
            # Extract first 1500 characters or split by sections
            if len(ai_text) > 1500:
                # Try to find a good breaking point
                sections = ['##', '**', '-']
                break_point = 1500
                for section in sections:
                    idx = ai_text.find(section, 1200)
                    if idx != -1:
                        break_point = idx
                        break
                
                ai_preview = ai_text[:break_point] + "\n\n... (complete analysis available in the full report)"
            else:
                ai_preview = ai_text
            
            story.append(Paragraph(ai_preview, normal_style))
        else:
            story.append(Paragraph("No AI analysis available.", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("---", normal_style))
        story.append(Paragraph("End of Report", heading2_style))
        story.append(Paragraph("Generated by AI Data Analyzer - Advanced Data Analysis Tool", normal_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        st.error(f"Error generating PDF with ReportLab: {str(e)}")
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")
        return None

def generate_simple_pdf_with_charts(results, dataset_name):
    """Generate a simpler PDF with essential charts - more reliable"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        )
        
        story.append(Paragraph(f"Data Analysis Report: {dataset_name}", title_style))
        story.append(Paragraph(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Basic info
        df = results['dataframe']
        info_text = f"""
        This dataset contains <b>{df.shape[0]:,} rows</b> and <b>{df.shape[1]} columns</b>, 
        with <b>{df.isnull().sum().sum():,} missing values</b> and <b>{df.duplicated().sum():,} duplicate rows</b>.
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Include key visualizations
        visualizations = results.get('visualizations', {})
        key_viz = ['data_types', 'correlation_heatmap']  # Prioritize these charts
        
        for viz_key in key_viz:
            if viz_key in visualizations:
                try:
                    story.append(Paragraph(f"Chart: {viz_key.replace('_', ' ').title()}", styles['Heading2']))
                    
                    img_bytes = export_plotly_figure(visualizations[viz_key], width=500, height=300)
                    if img_bytes:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                            tmp_file.write(img_bytes)
                            img = Image(tmp_file.name, width=5*inch, height=3*inch)
                            story.append(img)
                            story.append(Spacer(1, 10))
                        os.unlink(tmp_file.name)
                except Exception as e:
                    continue
        
        story.append(PageBreak())
        
        # AI Analysis preview
        if 'ai_analysis' in results:
            story.append(Paragraph("AI Analysis Insights", styles['Heading2']))
            # Take first 1000 characters
            preview = results['ai_analysis'][:1000] + "..." if len(results['ai_analysis']) > 1000 else results['ai_analysis']
            story.append(Paragraph(preview, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        st.error(f"Error in simple PDF generation: {str(e)}")
        return None

# =============================================================================
# FUNÇÕES ORIGINAIS DA INTERFACE
# =============================================================================

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

def display_print_instructions():
    """Display instructions for generating PDF via browser print"""
    st.markdown("""
    <div class="card no-print">
        <h3>📄 Generate PDF Report</h3>
        <p>To generate a PDF report with the exact same appearance as this page:</p>
        <ol>
            <li><strong>Use your browser's print function:</strong></li>
            <li><strong>Windows/Linux:</strong> Press <kbd>Ctrl</kbd> + <kbd>P</kbd></li>
            <li><strong>Mac:</strong> Press <kbd>Cmd</kbd> + <kbd>P</kbd></li>
            <li>In the print dialog, select <strong>"Save as PDF"</strong> as destination</li>
            <li>Click <strong>"Save"</strong> to download the PDF</li>
        </ol>
        <p><strong>Benefits of this method:</strong></p>
        <ul>
            <li>✅ Exact visual representation of the analysis</li>
            <li>✅ Includes all interactive charts and graphs</li>
            <li>✅ Professional formatting maintained</li>
            <li>✅ Works with complex layouts and visualizations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def add_print_header(dataset_name):
    """Add print-only header with dataset information"""
    st.markdown(f"""
    <div class="print-only" style="
        border-bottom: 2px solid #3498db; 
        padding-bottom: 1rem; 
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h1 style="color: #2c3e50; margin: 0; font-size: 2rem;">Data Analysis Report</h1>
        <p style="color: #7f8c8d; margin: 0.5rem 0; font-size: 1.1rem;">
            Dataset: {dataset_name} | Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        <p style="color: #95a5a6; margin: 0; font-size: 0.9rem;">
            Generated by AI Data Analyzer
        </p>
    </div>
    """, unsafe_allow_html=True)

# JavaScript para abrir o diálogo de impressão
def add_print_javascript():
    """Add JavaScript to trigger print dialog"""
    st.markdown("""
    <script>
    function openPrintDialog() {
        window.print();
    }
    </script>
    """, unsafe_allow_html=True)

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
            <p style="font-size: 0.9rem; margin: 0;">LLM-powered analysis to uncover hidden patterns</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin: 0.5rem 0; font-size: 1rem;">📄 PDF Reports</h4>
            <p style="font-size: 0.9rem; margin: 0;">Professional PDF reports via browser print function</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How to use - More compact
    st.markdown("### 📋 How to Use")
    if uploaded_file:
        st.markdown(f"""
        <div class="card">
            <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem;">
                <li style="margin-bottom: 0.5rem;"><strong>✅ File uploaded successfully</strong> - {uploaded_file.name}</li>
                <li style="margin-bottom: 0.5rem;"><strong>Click "Analyze Dataset"</strong> in the sidebar to start the analysis</li>
                <li style="margin-bottom: 0.5rem;"><strong>Wait for processing</strong> - the system will generate descriptive statistics and AI insights</li>
                <li style="margin-bottom: 0.5rem;"><strong>Explore results</strong> in the Exploratory Data Analysis and Insights tabs</li>
                <li><strong>Download PDF reports</strong> using Ctrl+P (Windows) or Cmd+P (Mac)</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem;">
                <li style="margin-bottom: 0.5rem;"><strong>Upload your CSV file</strong> using the sidebar uploader</li>
                <li style="margin-bottom: 0.5rem;"><strong>Click "Analyze Dataset"</strong> to start the analysis process</li>
                <li style="margin-bottom: 0.5rem;"><strong>Wait for processing</strong> - the system will generate descriptive statistics and AI insights</li>
                <li style="margin-bottom: 0.5rem;"><strong>Explore results</strong> in the Exploratory Data Analysis and Insights tabs</li>
                <li><strong>Download PDF reports</strong> using Ctrl+P (Windows) or Cmd+P (Mac)</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Tips - More compact
    st.markdown("### 💡 Tips for Best Results")
    st.markdown("""
    <div class="card">
        <ul style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem;">
            <li style="margin-bottom: 0.3rem;">Ensure your file is properly structured as CSV</li>
            <li style="margin-bottom: 0.3rem;">Clean unnecessary columns before uploading</li>
            <li style="margin-bottom: 0.3rem;">Handle missing values when possible</li>
            <li style="margin-bottom: 0.3rem;">Use descriptive column names</li>
            <li>Files should be under 200MB for optimal performance</li>
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
    
    # Create heatmap - configuração mais simples
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
    
    # Add print header
    dataset_name = st.session_state.get('uploaded_file_name', 'dataset')
    add_print_header(dataset_name)
    
    # Add JavaScript for print functionality
    add_print_javascript()
    
    # NOVA SEÇÃO: PDF Export com ReportLab
    st.markdown("### 🎯 Advanced PDF Export (ReportLab)")
    
    if not REPORTLAB_AVAILABLE:
        st.warning("""
        **ReportLab não está instalado!** 
        Para usar a geração avançada de PDF, instale: 
        `pip install reportlab pillow`
        """)
    
    pdf_col1, pdf_col2 = st.columns(2)
    
    with pdf_col1:
        if st.button("📊 Generate Professional PDF", use_container_width=True, 
                    disabled=not REPORTLAB_AVAILABLE):
            with st.spinner("🔄 Generating comprehensive PDF report..."):
                dataset_name = st.session_state.get('uploaded_file_name', 'dataset')
                pdf_buffer = generate_pdf_with_reportlab(results, dataset_name)
                
                if pdf_buffer:
                    st.success("✅ PDF generated successfully!")
                    st.download_button(
                        label="📥 Download Professional PDF",
                        data=pdf_buffer,
                        file_name=f"{dataset_name}_professional_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Failed to generate PDF. Trying simple version...")
                    # Fallback to simple version
                    simple_pdf = generate_simple_pdf_with_charts(results, dataset_name)
                    if simple_pdf:
                        st.download_button(
                            label="📥 Download Simple PDF",
                            data=simple_pdf,
                            file_name=f"{dataset_name}_simple_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
    
    with pdf_col2:
        if st.button("🚀 Generate Quick PDF", use_container_width=True,
                    disabled=not REPORTLAB_AVAILABLE):
            with st.spinner("🔄 Generating quick PDF report..."):
                dataset_name = st.session_state.get('uploaded_file_name', 'dataset')
                simple_pdf = generate_simple_pdf_with_charts(results, dataset_name)
                
                if simple_pdf:
                    st.success("✅ Quick PDF generated!")
                    st.download_button(
                        label="📥 Download Quick PDF",
                        data=simple_pdf,
                        file_name=f"{dataset_name}_quick_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Failed to generate quick PDF")
    
    # Informações sobre a geração de PDF
    st.markdown("""
    <div class="card">
        <h4>📋 PDF Features Included:</h4>
        <ul>
            <li>✅ Professional layout with table of contents</li>
            <li>✅ Dataset statistics and overview</li>
            <li>✅ All Plotly charts as high-quality images</li>
            <li>✅ AI analysis summary</li>
            <li>✅ Multi-page format with proper pagination</li>
            <li>✅ Color-coded tables and sections</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Export section original
    st.markdown("### 📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_print_instructions()
        
        # Botão funcional usando st.button com JavaScript
        st.markdown("""
        <div class="no-print" style="text-align: center; margin: 2rem 0;">
            <p style="color: #888; font-size: 0.9rem; margin-bottom: 1rem;">
                Quick print shortcut: <kbd>Ctrl</kbd> + <kbd>P</kbd> (Windows/Linux) or <kbd>Cmd</kbd> + <kbd>P</kbd> (Mac)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão que realmente funciona no Streamlit
        if st.button("🖨️ Open Print Dialog", use_container_width=True, key="print_eda"):
            st.markdown("""
            <script>
            window.print();
            </script>
            """, unsafe_allow_html=True)
            st.info("💰 **Tip**: In the print dialog, select 'Save as PDF' as destination")
    
    with col2:
        # Text report fallback
        if 'ai_analysis' in results and 'statistics' in results:
            combined_report = f"# Data Analysis Report\n\n## Descriptive Statistics\n\n{results['statistics']}\n\n## AI Analysis\n\n{results['ai_analysis']}"
            st.markdown("""
            <div class="card">
                <h4>📝 Text Report (Fallback)</h4>
                <p>Download the analysis in simple text format as a fallback option.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(get_download_link(combined_report, "analysis_report.txt", "📥 Download Text Report"), unsafe_allow_html=True)
    
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
    
    # Correlation heatmap
    st.markdown("### 🔗 Correlation Matrix")
    try:
        corr_fig = create_correlation_heatmap(df)
        st.plotly_chart(corr_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate correlation matrix: {str(e)}")
    
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
        st.dataframe(df.head(10), use_container_width=True, height=350)
    
    with col2:
        st.markdown("#### Column Information")
        column_info = analyzer.get_detailed_column_info()
        st.dataframe(column_info, use_container_width=True, height=350)

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
            
            # Visualizations - Line chart instead of histogram
            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                # Gráfico de área
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
                    color_discrete_sequence=['#3498db']  # Single color
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
                    color_discrete_sequence=['#3498db']  # Single color
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
            
            col1, col2 = st.columns([1, 2])  # More space for the chart
            
            with col1:
                # Metrics
                for val, count in value_counts.items():
                    percentage = percentages[val]
                    st.metric(
                        f"{val} Count", 
                        f"{count} ({percentage:.1f}%)"
                    )
            
            with col2:
                # Larger donut chart with specific colors
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
                    height=400,  # Larger chart
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
    
    # Add print header
    dataset_name = st.session_state.get('uploaded_file_name', 'dataset')
    add_print_header(dataset_name)
    
    # Add JavaScript for print functionality
    add_print_javascript()
    
    # Export section
    st.markdown("### 📥 Export Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_print_instructions()
        
        # Botão funcional usando st.button com JavaScript
        st.markdown("""
        <div class="no-print" style="text-align: center; margin: 2rem 0;">
            <p style="color: #888; font-size: 0.9rem; margin-bottom: 1rem;">
                Quick print shortcut: <kbd>Ctrl</kbd> + <kbd>P</kbd> (Windows/Linux) or <kbd>Cmd</kbd> + <kbd>P</kbd> (Mac)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão que realmente funciona no Streamlit
        if st.button("🖨️ Open Print Dialog", use_container_width=True, key="print_insights"):
            st.markdown("""
            <script>
            window.print();
            </script>
            """, unsafe_allow_html=True)
            st.info("💰 **Tip**: In the print dialog, select 'Save as PDF' as destination")
    
    with col2:
        # Text report fallback
        if 'ai_analysis' in results and 'statistics' in results:
            combined_report = f"# Data Analysis Report\n\n## Descriptive Statistics\n\n{results['statistics']}\n\n## AI Analysis\n\n{results['ai_analysis']}"
            st.markdown("""
            <div class="card">
                <h4>📝 Text Insights (Fallback)</h4>
                <p>Download the insights in text format as a fallback option.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(get_download_link(combined_report, "ai_insights_report.txt", "📥 Download Insights (TXT)"), unsafe_allow_html=True)
    
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
        
        # Check if this line starts a new section (more flexible matching)
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
            <h3 style="font-size: 1.2rem;">🚀 Ready for Deep Analysis?</h3>
            <p style="font-size: 0.9rem;">Click the <strong>"Analyze Dataset"</strong> button in the sidebar to generate comprehensive AI-powered insights.</p>
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