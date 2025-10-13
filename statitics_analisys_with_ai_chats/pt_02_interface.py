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

# Importar dos nossos módulos
from en_01_analyzer import ChatBotAnalyzer

# Configurar página
st.set_page_config(
    page_title="Analisador de Dados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS do tema escuro
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
    /* Esconder índice do dataframe */
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
    """Gerar link de download para conteúdo de texto"""
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'

def display_welcome_screen(uploaded_file=None):
    """Exibir tela de boas-vindas com informações do aplicativo"""
    # Título sem ícone
    st.markdown('<h1 class="main-header">Analisador de Dados</h1>', unsafe_allow_html=True)
    
    if uploaded_file:
        # Seção unificada na parte superior
        st.markdown(f"""
        <div class="welcome-card">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="flex: 1;">
                    <h2 style="color: #2ecc71; margin: 0; font-size: 1.5rem;">✅ Arquivo Carregado com Sucesso!</h2>
                    <p style="font-size: 1rem; margin: 0.5rem 0 0 0;">
                    <strong>Arquivo:</strong> {uploaded_file.name}<br>
                    Pronto para análise. Clique no botão <strong>"Analisar Conjunto de Dados"</strong> na barra lateral para começar.
                    </p>
                </div>
                <div style="margin-left: 1rem; padding: 1rem; background: rgba(52, 152, 219, 0.1); border-radius: 8px; border-left: 4px solid #3498db;">
                    <h3 style="font-size: 1.1rem; color: #3498db; margin: 0 0 0.5rem 0;">🚀 Pronto para Análise Profunda?</h3>
                    <p style="font-size: 0.9rem; margin: 0;">Clique no botão na barra lateral para gerar insights com IA.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color: #3498db; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">🎯 Bem-vindo ao Analisador de Dados!</h2>
            <p style="font-size: 1rem; text-align: center; margin-bottom: 1rem;">
            Ferramenta avançada com IA para análise abrangente de conjuntos de dados e geração de insights.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Funcionalidades em um único card com layout melhorado
    st.markdown("### ✨ Funcionalidades do Aplicativo")
    st.markdown("""
    <div class="feature-card">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #3498db;">📊 Análise Descritiva</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Relatórios estatísticos abrangentes e perfilamento de dados com métricas detalhadas e distribuições</p>
            </div>
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #2ecc71;">📈 Visualização de Dados</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Gráficos interativos, visualizações e matrizes de correlação para todos os tipos de variáveis e relacionamentos</p>
            </div>
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #e74c3c;">🤖 Insights com IA</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Análise com LLM para descobrir padrões ocultos, tendências e inteligência de negócios</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Como Usar e Dicas lado a lado com layout melhorado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Como Usar")
        if uploaded_file:
            st.markdown(f"""
            <div class="card">
                <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                    <li style="margin-bottom: 0.8rem;"><strong>✅ Arquivo carregado com sucesso</strong> - {uploaded_file.name}</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Clique em "Analisar Conjunto de Dados"</strong> na barra lateral para iniciar a análise</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Aguarde o processamento</strong> - o sistema gerará estatísticas descritivas e insights com IA</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Explore os resultados</strong> nas abas Análise Exploratória e Insights Gerados</li>
                    <li><strong>Baixe os relatórios</strong> para uso offline e documentação</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card">
                <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                    <li style="margin-bottom: 0.8rem;"><strong>Carregue seu arquivo CSV</strong> usando o carregador na barra lateral</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Clique em "Analisar Conjunto de Dados"</strong> para iniciar o processo de análise</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Aguarde o processamento</strong> - o sistema gerará estatísticas descritivas e insights com IA</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Explore os resultados</strong> nas abas Análise Exploratória e Insights Gerados</li>
                    <li><strong>Baixe os relatórios</strong> para uso offline e documentação</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Dicas - Layout melhorado
        st.markdown("### 💡 Dicas para Melhores Resultados")
        st.markdown("""
        <div class="card">
            <ul style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                <li style="margin-bottom: 0.8rem;"><strong>Garanta formato CSV</strong> - Valores separados por vírgula adequadamente estruturados</li>
                <li style="margin-bottom: 0.8rem;"><strong>Limpe os dados primeiro</strong> - Remova colunas desnecessárias antes de carregar</li>
                <li style="margin-bottom: 0.8rem;"><strong>Trate valores faltantes</strong> - Resolva valores nulos quando possível</li>
                <li style="margin-bottom: 0.8rem;"><strong>Cabeçalhos descritivos</strong> - Use nomes de colunas claros e significativos</li>
                <li><strong>Otimização de tamanho</strong> - Arquivos abaixo de 200MB para desempenho ideal</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_column_types_cards(analyzer):
    """Exibir tipos de coluna como cards em vez de gráfico de rosca"""
    simple_types = analyzer.get_simple_column_types()
    
    # Obter contagens para cada tipo, garantindo que contagens zero sejam incluídas
    numerical_count = len(simple_types.get('Numéricas', []))
    categorical_count = len(simple_types.get('Categóricas', []))
    boolean_count = len(simple_types.get('Verdadeiro/Falso', []))
    datetime_count = len(simple_types.get('Data/Hora', []))
    
    # Exibir como cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_type_card(numerical_count, "Colunas Numéricas", "#3498db"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_type_card(categorical_count, "Colunas Categóricas", "#e74c3c"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_type_card(boolean_count, "Colunas Verdadeiro/Falso", "#2ecc71"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_type_card(datetime_count, "Colunas Data/Hora", "#f39c12"), unsafe_allow_html=True)

def create_correlation_heatmap(df):
    """Criar mapa de calor de correlação para todas as variáveis"""
    # Criar uma cópia do dataframe para codificação
    df_encoded = df.copy()
    
    # Codificar variáveis categóricas
    for col in df_encoded.select_dtypes(include=['object', 'category']).columns:
        df_encoded[col] = pd.factorize(df_encoded[col])[0]
    
    # Codificar variáveis booleanas
    for col in df_encoded.select_dtypes(include='bool').columns:
        df_encoded[col] = df_encoded[col].astype(int)
    
    # Calcular matriz de correlação
    corr_matrix = df_encoded.corr()
    
    # Criar mapa de calor
    fig = px.imshow(
        corr_matrix,
        title="Matriz de Correlação (Todas as Variáveis)",
        color_continuous_scale='RdBu_r',
        aspect="auto",
        range_color=[-1, 1],
        labels=dict(color="Correlação")
    )
    
    fig.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        coloraxis_colorbar=dict(
            title="Correlação",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1.0", "-0.5", "0.0", "0.5", "1.0"]
        )
    )
    
    return fig

def display_exploratory_analysis(results):
    """Exibir análise exploratória de dados com abas"""
    st.markdown('<div class="section-header">📊 Análise Exploratória de Dados</div>', unsafe_allow_html=True)
    
    # Botão de download
    if 'ai_analysis' in results and 'statistics' in results:
        combined_report = f"# Relatório de Análise de Dados\n\n## Estatísticas Descritivas\n\n{results['statistics']}\n\n## Análise com IA\n\n{results['ai_analysis']}"
        st.markdown(get_download_link(combined_report, "relatorio_analise_completo.txt", "📥 Baixar Relatório Completo (TXT)"), unsafe_allow_html=True)
    
    # Cards de visão geral
    df = results['dataframe']
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(create_stat_card(f"{df.shape[0]:,}", "Total de Linhas", "📈", "#2ecc71"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_stat_card(f"{df.shape[1]}", "Total de Colunas", "📊", "#3498db"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_stat_card(f"{df.isnull().sum().sum():,}", "Valores Faltantes", "⚠️", "#f39c12"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_stat_card(f"{df.duplicated().sum():,}", "Linhas Duplicadas", "🔍", "#e74c3c"), unsafe_allow_html=True)
    with col5:
        total_cells = df.shape[0] * df.shape[1]
        st.markdown(create_stat_card(f"{total_cells:,}", "Total de Células", "🔢", "#9b59b6"), unsafe_allow_html=True)
    
    # Tipos de coluna como cards
    analyzer = st.session_state.analyzer
    display_column_types_cards(analyzer)
    
    # Criar abas para diferentes tipos de dados
    tab_names = ["Visão Geral"]
    simple_types = analyzer.get_simple_column_types()
    
    if simple_types['Numéricas']:
        tab_names.append("Colunas Numéricas")
    if simple_types['Categóricas']:
        tab_names.append("Colunas Categóricas")
    if simple_types['Verdadeiro/Falso']:
        tab_names.append("Colunas Verdadeiro/Falso")
    if simple_types['Data/Hora']:
        tab_names.append("Colunas Data/Hora")
    
    tabs = st.tabs(tab_names)
    
    # Aba Visão Geral
    with tabs[0]:
        display_overview_tab(results)
    
    # Aba Colunas Numéricas
    if simple_types['Numéricas']:
        tab_index = tab_names.index("Colunas Numéricas")
        with tabs[tab_index]:
            display_numerical_tab(results)
    
    # Aba Colunas Categóricas
    if simple_types['Categóricas']:
        tab_index = tab_names.index("Colunas Categóricas")
        with tabs[tab_index]:
            display_categorical_tab(results)
    
    # Aba Colunas Verdadeiro/Falso
    if simple_types['Verdadeiro/Falso']:
        tab_index = tab_names.index("Colunas Verdadeiro/Falso")
        with tabs[tab_index]:
            display_boolean_tab(results)
    
    # Aba Colunas Data/Hora
    if simple_types['Data/Hora']:
        tab_index = tab_names.index("Colunas Data/Hora")
        with tabs[tab_index]:
            display_datetime_tab(results)

def display_overview_tab(results):
    """Exibir conteúdo da aba de visão geral"""
    df = results['dataframe']
    analyzer = st.session_state.analyzer
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Primeiras 10 Linhas")
        # Índice removido usando hide_index=True
        df_display = df.head(10)
        st.dataframe(df_display, use_container_width=True, height=350, hide_index=True)
    
    with col2:
        st.markdown("#### Informações das Colunas")
        column_info = analyzer.get_detailed_column_info()
        # Índice removido usando hide_index=True
        st.dataframe(column_info, use_container_width=True, height=350, hide_index=True)
    
    # Mapa de calor de correlação movido para dentro da aba Visão Geral
    st.markdown("### 🔗 Matriz de Correlação")
    try:
        corr_fig = create_correlation_heatmap(df)
        st.plotly_chart(corr_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Não foi possível gerar a matriz de correlação: {str(e)}")

def display_numerical_tab(results):
    """Exibir análise de colunas numéricas"""
    df = results['dataframe']
    numerical_cols = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
    
    for col in numerical_cols:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 📈 {col}")
            
            # Estatísticas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Média", f"{df[col].mean():.2f}")
                st.metric("Mediana", f"{df[col].median():.2f}")
                st.metric("Variância", f"{df[col].var():.2f}")
            with col2:
                st.metric("Desvio Padrão", f"{df[col].std():.2f}")
                st.metric("Mínimo", f"{df[col].min():.2f}")
                st.metric("Máximo", f"{df[col].max():.2f}")
            
            st.metric("Valores Faltantes", f"{df[col].isnull().sum()}")
            
            # Visualizações
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
                        title=f"Distribuição - {col}",
                        labels={'x': col, 'y': 'Frequência'}
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
                        yaxis_title="Frequência"
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
    """Exibir análise de colunas categóricas"""
    df = results['dataframe']
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns
    
    for col in categorical_cols:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 🏷️ {col}")
            
            # Estatísticas
            unique_count = df[col].nunique()
            missing_count = df[col].isnull().sum()
            top_values = df[col].value_counts().head(3)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Categorias Únicas", unique_count)
                st.metric("Valores Faltantes", missing_count)
            
            with col2:
                st.markdown("**Top 3 Categorias:**")
                for value, count in top_values.items():
                    st.write(f"- `{value}`: {count} ocorrências")
            
            # Gráfico de barras com orientação condicional
            value_counts = df[col].value_counts().head(10)  # Apenas os 10 principais
            
            if len(value_counts) <= 5:
                # Gráfico de barras horizontal para 5 ou menos categorias
                fig_bar = px.bar(
                    x=value_counts.values,
                    y=value_counts.index,
                    orientation='h',
                    title=f"Principais Categorias - {col}",
                    color_discrete_sequence=['#3498db']
                )
                fig_bar.update_layout(
                    xaxis_title="Contagem",
                    yaxis_title="Categorias",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
            else:
                # Gráfico de barras vertical para mais de 5 categorias
                fig_bar = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Principais Categorias - {col}",
                    color_discrete_sequence=['#3498db']
                )
                fig_bar.update_layout(
                    xaxis_title="Categorias",
                    yaxis_title="Contagem",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
                fig_bar.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_boolean_tab(results):
    """Exibir análise de colunas booleanas"""
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
                # Métricas
                for val, count in value_counts.items():
                    percentage = percentages[val]
                    st.metric(
                        f"Contagem {val}", 
                        f"{count} ({percentage:.1f}%)"
                    )
            
            with col2:
                # Gráfico de rosca
                colors = {'True': 'rgba(46, 204, 113, 0.8)', 'False': 'rgba(231, 76, 60, 0.8)'}
                color_sequence = [colors.get(str(label), '#3498db') for label in value_counts.index]

                fig_donut = px.pie(
                    values=value_counts.values,
                    names=[str(label) for label in value_counts.index],
                    title=f"Distribuição - {col}",
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
    """Exibir análise de colunas de data/hora"""
    df = results['dataframe']
    datetime_cols = df.select_dtypes(include=['datetime64']).columns
    
    for col in datetime_cols:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 📅 {col}")
            
            # Estatísticas
            min_date = df[col].min()
            max_date = df[col].max()
            date_range = max_date - min_date
            
            # Data mais frequente
            date_counts = df[col].value_counts()
            most_frequent_date = date_counts.index[0] if len(date_counts) > 0 else None
            most_frequent_count = date_counts.iloc[0] if len(date_counts) > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Data Mais Antiga", min_date.strftime('%Y-%m-%d'))
                st.metric("Data Mais Recente", max_date.strftime('%Y-%m-%d'))
                st.metric("Intervalo de Datas", f"{date_range.days} dias")
            
            with col2:
                if most_frequent_date:
                    st.metric("Data Mais Frequente", most_frequent_date.strftime('%Y-%m-%d'))
                    st.metric("Frequência", most_frequent_count)
            
            # Gráfico de linha temporal
            timeline_data = df[col].value_counts().sort_index()
            fig_timeline = px.line(
                x=timeline_data.index,
                y=timeline_data.values,
                title=f"Linha do Tempo - {col}",
                labels={'x': 'Data', 'y': 'Contagem de Registros'}
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
    """Exibir análise de LLM com seções estruturadas"""
    st.markdown('<div class="section-header">🤖 Insights Gerados</div>', unsafe_allow_html=True)
    
    # Botão de download
    if 'ai_analysis' in results and 'statistics' in results:
        combined_report = f"# Relatório de Análise de Dados\n\n## Estatísticas Descritivas\n\n{results['statistics']}\n\n## Análise com IA\n\n{results['ai_analysis']}"
        st.markdown(get_download_link(combined_report, "relatorio_analise_completo.txt", "📥 Baixar Relatório Completo (TXT)"), unsafe_allow_html=True)
    
    if 'ai_analysis' not in results or not results['ai_analysis']:
        st.error("Nenhuma análise com IA disponível. Por favor, execute a análise primeiro.")
        return
    
    analysis_text = results['ai_analysis']
    
    # Extração de seções melhorada
    sections = {
        'Resumo Executivo': '',
        'Análise Estatística Detalhada': '',
        'Identificação de Padrões': '',
        'Implicações para Negócios/Pesquisa': '',
        'Recomendações': ''
    }
    
    current_section = None
    lines = analysis_text.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        
        # Verificar se esta linha inicia uma nova seção
        if any(header in line_stripped.lower() for header in ['resumo executivo', 'executive summary', 'summary']):
            current_section = 'Resumo Executivo'
            continue
        elif any(header in line_stripped.lower() for header in ['análise estatística detalhada', 'detailed statistical analysis', 'statistical analysis']):
            current_section = 'Análise Estatística Detalhada'
            continue
        elif any(header in line_stripped.lower() for header in ['identificação de padrões', 'pattern identification', 'pattern analysis', 'patterns']):
            current_section = 'Identificação de Padrões'
            continue
        elif any(header in line_stripped.lower() for header in ['implicações para negócios/pesquisa', 'business/research implications', 'implications', 'business implications', 'research implications']):
            current_section = 'Implicações para Negócios/Pesquisa'
            continue
        elif any(header in line_stripped.lower() for header in ['recomendações', 'recommendations', 'suggestions', 'next steps']):
            current_section = 'Recomendações'
            continue
        
        # Pular linhas vazias no início das seções
        if current_section and not line_stripped and not sections[current_section]:
            continue
            
        # Adicionar conteúdo à seção atual
        if current_section and line_stripped:
            sections[current_section] += line + '\n'
    
    # Exibir cada seção
    section_displayed = False
    for section_name, section_content in sections.items():
        if section_content.strip():
            section_displayed = True
            st.markdown(f'<div class="insight-section">', unsafe_allow_html=True)
            st.markdown(f"### {section_name}")
            st.markdown(section_content)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Se nenhuma seção foi extraída adequadamente, mostrar a análise bruta
    if not section_displayed:
        st.markdown("""
        <div class="insight-section">
            <h3>Análise Completa</h3>
            <p>A análise com IA não pôde ser analisada em seções específicas. Aqui está a análise completa:</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="card">{analysis_text}</div>', unsafe_allow_html=True)

def main():
    """Aplicação principal do Streamlit"""
    
    # Inicializar estado da sessão
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analyzer' not in st.session_state:
        try:
            st.session_state.analyzer = ChatBotAnalyzer()
        except Exception as e:
            st.error(f"❌ Falha ao inicializar o analisador: {e}")
            st.info("Por favor, certifique-se de que sua chave da API OpenRouter está configurada corretamente.")
            return
    
    # Barra lateral para upload de arquivo
    with st.sidebar:
        st.markdown("## 📁 Carregar Conjunto de Dados")
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV",
            type=['csv'],
            help="Carregue seu conjunto de dados em formato CSV"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
            
            # Botão de análise
            st.markdown("## 🚀 Iniciar Análise")
            if st.button("Analisar Conjunto de Dados", type="primary", use_container_width=True):
                with st.spinner("🔄 Processando conjunto de dados... Isso pode levar alguns instantes."):
                    try:
                        # Salvar arquivo carregado em local temporário
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Executar análise
                        results = st.session_state.analyzer.analyze_csv(tmp_file_path)
                        
                        if results:
                            st.session_state.analysis_results = results
                            st.session_state.uploaded_file_name = uploaded_file.name
                            st.success("✅ Análise concluída com sucesso!")
                        else:
                            st.error("❌ A análise falhou. Por favor, verifique seu arquivo e tente novamente.")
                        
                        # Limpar arquivo temporário
                        os.unlink(tmp_file_path)
                        
                    except Exception as e:
                        st.error(f"❌ Erro durante a análise: {str(e)}")
                        st.info("Por favor, verifique se seu arquivo CSV está formatado corretamente.")
            
            # Botão limpar análise
            if st.session_state.analysis_results:
                if st.button("Limpar Análise", type="secondary", use_container_width=True):
                    st.session_state.analysis_results = None
                    st.rerun()
    
    # Área de conteúdo principal
    if uploaded_file is not None and st.session_state.analysis_results is None:
        # Mostrar tela de boas-vindas com mensagem de arquivo carregado
        display_welcome_screen(uploaded_file)
    
    elif st.session_state.analysis_results:
        # Mostrar resultados da análise em abas
        tab1, tab2 = st.tabs(["📊 Análise Exploratória de Dados", "🤖 Insights Gerados"])
        
        with tab1:
            display_exploratory_analysis(st.session_state.analysis_results)
        
        with tab2:
            display_llm_insights(st.session_state.analysis_results)
    
    else:
        # Tela de boas-vindas
        display_welcome_screen()

if __name__ == "__main__":
    main()