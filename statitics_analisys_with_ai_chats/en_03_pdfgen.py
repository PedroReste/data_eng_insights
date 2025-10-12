# en_03_pdf_generator.py
import os
import base64
import tempfile
from io import BytesIO
import pdfkit
from jinja2 import Template
import plotly.io as pio
import pandas as pd

class PDFReportGenerator:
    def __init__(self):
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Data Analysis Report</title>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f8f9fa;
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
                    padding: 25px;
                    margin: 20px 0;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    border-left: 5px solid #3498db;
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
                    font-size: 2.5em;
                    margin: 0;
                    font-weight: 300;
                }
                h2 {
                    color: #2c3e50;
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 10px;
                    margin-top: 30px;
                }
                h3 {
                    color: #34495e;
                    margin-top: 20px;
                }
                .card {
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }
                .stat-card {
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-top: 4px solid #3498db;
                }
                .stat-value {
                    font-size: 1.8em;
                    font-weight: bold;
                    color: #2c3e50;
                }
                .stat-label {
                    font-size: 0.9em;
                    color: #7f8c8d;
                    margin-top: 5px;
                }
                .table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                .table th, .table td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }
                .table th {
                    background-color: #34495e;
                    color: white;
                }
                .table tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                .visualization {
                    text-align: center;
                    margin: 25px 0;
                    page-break-inside: avoid;
                }
                .visualization img {
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }
                .insight-box {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                }
                .recommendation {
                    background: #d1ecf1;
                    border: 1px solid #bee5eb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                }
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    border-top: 1px solid #ecf0f1;
                }
                @media print {
                    body {
                        background: white !important;
                    }
                    .section {
                        box-shadow: none;
                        border: 1px solid #ddd;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Data Analysis Report</h1>
                <p>Generated by AI Data Analyzer</p>
                <p><strong>Dataset:</strong> {{ dataset_name }}</p>
                <p><strong>Generated on:</strong> {{ timestamp }}</p>
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
                        <div class="stat-label">{{ type.name }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if statistics %}
            <div class="section section-statistics">
                <h2>📈 Descriptive Statistics</h2>
                {{ statistics|safe }}
            </div>
            {% endif %}

            {% if insights %}
            <div class="section section-insights">
                <h2>🤖 AI Insights & Analysis</h2>
                {{ insights|safe }}
            </div>
            {% endif %}

            {% if visualizations %}
            <div class="section section-visualizations">
                <h2>📊 Key Visualizations</h2>
                {% for viz in visualizations %}
                <div class="visualization">
                    <h3>{{ viz.title }}</h3>
                    <img src="data:image/png;base64,{{ viz.image }}" alt="{{ viz.title }}">
                </div>
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
            img_bytes = pio.to_image(fig, format='png', width=1000, height=600)
            return base64.b64encode(img_bytes).decode('utf-8')
        except Exception as e:
            print(f"Error converting plotly figure: {e}")
            return None
    
    def format_statistics_for_html(self, stats_text):
        """Convert markdown statistics to HTML"""
        if not stats_text:
            return ""
        
        # Simple markdown to HTML conversion
        html = stats_text
        
        # Convert headers
        html = html.replace('# ', '<h2>').replace('\n# ', '</h2>\n<h2>')
        html = html.replace('## ', '<h3>').replace('\n## ', '</h3>\n<h3>')
        html = html.replace('### ', '<h4>').replace('\n### ', '</h4>\n<h4>')
        
        # Convert bullet points
        html = html.replace('- **', '<li><strong>').replace('**', '</strong>')
        html = html.replace('\n- ', '</li>\n<li>')
        
        # Wrap lists
        html = html.replace('<li>', '<ul><li>').replace('</li>', '</li></ul>')
        
        # Handle line breaks
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        
        return f'<div class="statistics-content">{html}</div>'
    
    def format_insights_for_html(self, insights_text):
        """Convert markdown insights to HTML"""
        if not insights_text:
            return ""
        
        html = insights_text
        
        # Convert sections with special formatting
        sections = {
            'Executive Summary': 'insight-box',
            'Recommendations': 'recommendation',
            'Business/Research Implications': 'insight-box'
        }
        
        for section, css_class in sections.items():
            if section in html:
                # Simple section wrapping
                html = html.replace(section, f'<div class="{css_class}"><h3>{section}</h3>')
                # This is a simplified version - you might want more sophisticated parsing
        
        # Convert markdown headers
        html = html.replace('# ', '<h2>').replace('\n# ', '</h2>\n<h2>')
        html = html.replace('## ', '<h3>').replace('\n## ', '</h3>\n<h3>')
        
        return f'<div class="insights-content">{html}</div>'
    
    def generate_pdf_report(self, results, dataset_name, include_visualizations=True):
        """Generate a complete PDF report from analysis results"""
        
        # Prepare overview statistics
        df = results['dataframe']
        overview_stats = [
            {'value': f"{df.shape[0]:,}", 'label': 'Total Rows'},
            {'value': f"{df.shape[1]}", 'label': 'Total Columns'},
            {'value': f"{df.isnull().sum().sum():,}", 'label': 'Missing Values'},
            {'value': f"{df.duplicated().sum():,}", 'label': 'Duplicated Rows'},
            {'value': f"{(df.shape[0] * df.shape[1]):,}", 'label': 'Total Cells'}
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
        
        # Prepare visualizations
        visualizations = []
        if include_visualizations and 'visualizations' in results:
            for viz_name, fig in results['visualizations'].items():
                if fig and hasattr(fig, 'to_image'):
                    base64_img = self.convert_plotly_to_base64(fig)
                    if base64_img:
                        visualizations.append({
                            'title': viz_name.replace('_', ' ').title(),
                            'image': base64_img
                        })
        
        # Prepare template data
        template_data = {
            'dataset_name': dataset_name,
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overview_stats': overview_stats,
            'column_types': column_types,
            'statistics': formatted_stats,
            'insights': formatted_insights,
            'visualizations': visualizations[:4]  # Limit to 4 visualizations
        }
        
        # Render HTML
        template = Template(self.html_template)
        html_content = template.render(**template_data)
        
        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        try:
            # Generate PDF
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # Fallback: return HTML content for debugging
            return html_content.encode('utf-8')