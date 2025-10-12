# en_03_pdf_generator.py
import os
import base64
import tempfile
from io import BytesIO
from jinja2 import Template
import plotly.io as pio
import pandas as pd
from datetime import datetime

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("WeasyPrint not available - PDF generation disabled")

class PDFReportGenerator:
    def __init__(self):
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Data Analysis Report</title>
            <style>
                @page {
                    size: A4;
                    margin: 1.5cm;
                    @bottom-center {
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 10px;
                        color: #666;
                    }
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background: white;
                }
                
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }
                
                .section {
                    background: white;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    border-left: 5px solid #3498db;
                    page-break-inside: avoid;
                }
                
                .section-statistics {
                    border-left-color: #2ecc71;
                }
                
                .section-insights {
                    border-left-color: #e74c3c;
                }
                
                .section-visualizations {
                    border-left-color: #f39c12;
                }
                
                h1 {
                    font-size: 28px;
                    margin: 0;
                    font-weight: 300;
                }
                
                h2 {
                    color: #2c3e50;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 8px;
                    margin-top: 25px;
                    font-size: 20px;
                    page-break-after: avoid;
                }
                
                h3 {
                    color: #34495e;
                    margin-top: 15px;
                    font-size: 16px;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 12px;
                    margin: 15px 0;
                }
                
                .stat-card {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    text-align: center;
                    border-top: 4px solid #3498db;
                }
                
                .stat-value {
                    font-size: 20px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 5px 0;
                }
                
                .stat-label {
                    font-size: 12px;
                    color: #7f8c8d;
                }
                
                .table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    font-size: 12px;
                }
                
                .table th, .table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                
                .table th {
                    background-color: #34495e;
                    color: white;
                    font-weight: 600;
                }
                
                .table tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                
                .visualization {
                    text-align: center;
                    margin: 20px 0;
                    page-break-inside: avoid;
                }
                
                .visualization img {
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    margin: 10px 0;
                }
                
                .insight-box {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 12px 0;
                    font-size: 14px;
                }
                
                .recommendation {
                    background: #d1ecf1;
                    border: 1px solid #bee5eb;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 12px 0;
                    font-size: 14px;
                }
                
                .footer {
                    text-align: center;
                    margin-top: 30px;
                    padding: 15px;
                    color: #7f8c8d;
                    font-size: 11px;
                    border-top: 1px solid #ecf0f1;
                }
                
                .page-break {
                    page-break-before: always;
                }
                
                .code-block {
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    padding: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                    margin: 10px 0;
                    overflow-x: auto;
                }
                
                ul, ol {
                    margin: 10px 0;
                    padding-left: 20px;
                }
                
                li {
                    margin: 5px 0;
                }
                
                strong {
                    color: #2c3e50;
                }
                
                .metadata {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 15px 0;
                    font-size: 13px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Data Analysis Report</h1>
                <p>Generated by AI Data Analyzer</p>
                <div class="metadata">
                    <strong>Dataset:</strong> {{ dataset_name }}<br>
                    <strong>Generated on:</strong> {{ timestamp }}<br>
                    <strong>Total Rows:</strong> {{ total_rows }} | <strong>Total Columns:</strong> {{ total_columns }}
                </div>
            </div>

            {% if overview_stats %}
            <div class="section">
                <h2>📋 Dataset Overview</h2>
                <div class="stats-grid">
                    {% for stat in overview_stats %}
                    <div class="stat-card">
                        <div class="stat-value">{{ stat.value }}</div>
                        <div class="stat-label">{{ stat.label }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if column_types %}
            <div class="section">
                <h2>🔧 Data Types Summary</h2>
                <div class="stats-grid">
                    {% for type in column_types %}
                    <div class="stat-card" style="border-top-color: {{ type.color }};">
                        <div class="stat-value">{{ type.count }}</div>
                        <div class="stat-label">{{ type.name }} Columns</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if statistics_html %}
            <div class="section section-statistics">
                <h2>📈 Descriptive Statistics</h2>
                {{ statistics_html }}
            </div>
            {% endif %}

            {% if insights_html %}
            <div class="page-break"></div>
            <div class="section section-insights">
                <h2>🤖 AI Insights & Analysis</h2>
                {{ insights_html }}
            </div>
            {% endif %}

            {% if visualizations and visualizations|length > 0 %}
            <div class="page-break"></div>
            <div class="section section-visualizations">
                <h2>📊 Key Visualizations</h2>
                {% for viz in visualizations %}
                <div class="visualization">
                    <h3>{{ viz.title }}</h3>
                    <img src="data:image/png;base64,{{ viz.image }}" alt="{{ viz.title }}">
                </div>
                {% if not loop.last %}<hr style="margin: 20px 0;">{% endif %}
                {% endfor %}
            </div>
            {% endif %}

            <div class="footer">
                <p>Report generated automatically by Data Analyzer AI</p>
                <p>https://data-analyzer-pr.streamlit.app</p>
            </div>
        </body>
        </html>
        """
    
    def convert_plotly_to_base64(self, fig):
        """Convert Plotly figure to base64 encoded image"""
        try:
            # Increase DPI for better print quality
            img_bytes = pio.to_image(fig, format='png', width=800, height=500, scale=2)
            return base64.b64encode(img_bytes).decode('utf-8')
        except Exception as e:
            print(f"Error converting plotly figure: {e}")
            return None
    
    def format_statistics_for_html(self, stats_text):
        """Convert markdown statistics to HTML"""
        if not stats_text:
            return "<p>No statistics available.</p>"
        
        html = ""
        lines = stats_text.split('\n')
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    html += "</ul>"
                    in_list = False
                continue
            
            # Handle headers
            if line.startswith('# '):
                html += f"<h2>{line[2:]}</h2>"
            elif line.startswith('## '):
                html += f"<h3>{line[3:]}</h3>"
            elif line.startswith('### '):
                html += f"<h4>{line[4:]}</h4>"
            # Handle bullet points
            elif line.startswith('- **'):
                if not in_list:
                    html += "<ul>"
                    in_list = True
                # Extract content between ** **
                content = line[2:]  # Remove '- '
                content = content.replace('**', '')  # Remove bold markers
                html += f"<li><strong>{content}</strong></li>"
            elif line.startswith('- '):
                if not in_list:
                    html += "<ul>"
                    in_list = True
                html += f"<li>{line[2:]}</li>"
            else:
                if in_list:
                    html += "</ul>"
                    in_list = False
                html += f"<p>{line}</p>"
        
        if in_list:
            html += "</ul>"
        
        return html
    
    def format_insights_for_html(self, insights_text):
        """Convert markdown insights to HTML with section formatting"""
        if not insights_text:
            return "<p>No insights available.</p>"
        
        html = ""
        lines = insights_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle main sections
            if line.lower().startswith('executive summary'):
                current_section = 'summary'
                html += f'<div class="insight-box"><h3>{line}</h3>'
            elif any(header in line.lower() for header in ['recommendations', 'suggestions']):
                if current_section:
                    html += '</div>'
                current_section = 'recommendation'
                html += f'<div class="recommendation"><h3>{line}</h3>'
            elif line.startswith('# '):
                if current_section:
                    html += '</div>'
                current_section = None
                html += f"<h2>{line[2:]}</h2>"
            elif line.startswith('## '):
                if current_section:
                    html += '</div>'
                current_section = None
                html += f"<h3>{line[3:]}</h3>"
            else:
                html += f"<p>{line}</p>"
        
        # Close any open section
        if current_section:
            html += '</div>'
        
        return html
    
    def generate_pdf_report(self, results, dataset_name, include_visualizations=True):
        """Generate a complete PDF report from analysis results"""
        if not WEASYPRINT_AVAILABLE:
            raise Exception("WeasyPrint not available. Please install weasyprint and cairocffi.")
        
        try:
            df = results['dataframe']
            
            # Prepare overview statistics
            overview_stats = [
                {'value': f"{df.shape[0]:,}", 'label': 'Total Rows'},
                {'value': f"{df.shape[1]}", 'label': 'Total Columns'},
                {'value': f"{df.isnull().sum().sum():,}", 'label': 'Missing Values'},
                {'value': f"{df.duplicated().sum():,}", 'label': 'Duplicated Rows'}
            ]
            
            # Prepare column types
            column_types = [
                {'name': 'Numerical', 'count': len(df.select_dtypes(include=['number']).columns), 'color': '#3498db'},
                {'name': 'Categorical', 'count': len(df.select_dtypes(include=['object', 'category']).columns), 'color': '#e74c3c'},
                {'name': 'Boolean', 'count': len(df.select_dtypes(include=['bool']).columns), 'color': '#2ecc71'},
                {'name': 'Date/Time', 'count': len(df.select_dtypes(include=['datetime']).columns), 'color': '#f39c12'}
            ]
            
            # Format statistics and insights
            formatted_stats = self.format_statistics_for_html(results.get('statistics', ''))
            formatted_insights = self.format_insights_for_html(results.get('ai_analysis', ''))
            
            # Prepare visualizations (limit to key ones)
            visualizations = []
            if include_visualizations and 'visualizations' in results:
                key_viz = ['data_types', 'correlation_heatmap', 'missing_data']
                for viz_name in key_viz:
                    if viz_name in results['visualizations']:
                        fig = results['visualizations'][viz_name]
                        base64_img = self.convert_plotly_to_base64(fig)
                        if base64_img:
                            visualizations.append({
                                'title': viz_name.replace('_', ' ').title(),
                                'image': base64_img
                            })
            
            # Prepare template data
            template_data = {
                'dataset_name': dataset_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_rows': f"{df.shape[0]:,}",
                'total_columns': df.shape[1],
                'overview_stats': overview_stats,
                'column_types': column_types,
                'statistics_html': formatted_stats,
                'insights_html': formatted_insights,
                'visualizations': visualizations
            }
            
            # Render HTML
            template = Template(self.html_template)
            html_content = template.render(**template_data)
            
            # Generate PDF
            pdf_bytes = HTML(string=html_content, base_url='.').write_pdf()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise Exception(f"PDF generation failed: {str(e)}")