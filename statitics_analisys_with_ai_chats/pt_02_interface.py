# pt_02_interface.py
import streamlit as st
import pandas as pd
import tempfile
import os
import base64
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Importar de nossos módulos
from pt_01_analyzer import AnalisadorChatBot

# Configurar página
st.set_page_config(
    page_title="Analisador de Dados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para tema escuro
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
    /* Ocultar índice do dataframe */
    .dataframe thead th:first-child {
        display: none;
    }
    .dataframe tbody th {
        display: none;
    }
    .format-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    .upload-success-section {
        background: linear-gradient(135deg, #1e2130 0%, #2d3256 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid #2ecc71;
    }
    .upload-success-left {
        background: rgba(46, 204, 113, 0.1);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #2ecc71;
        height: 100%;
    }
    .upload-success-right {
        background: rgba(52, 152, 219, 0.1);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

def inicializar_analisador():
    """Inicializar o analisador com tratamento adequado de erros"""
    try:
        if 'analisador' not in st.session_state or st.session_state.analisador is None:
            st.session_state.analisador = AnalisadorChatBot()
            return True
        return True
    except Exception as e:
        st.error(f"❌ Falha ao inicializar analisador: {e}")
        st.info("Por favor, certifique-se de que sua chave API do OpenRouter está configurada corretamente.")
        return False

def criar_cartao_estatistica(valor, rotulo, icone="📊", cor="#667eea"):
    return f"""
    <div class="stat-card" style="background: linear-gradient(135deg, {cor} 0%, #764ba2 100%);">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">{icone}</div>
        <div class="metric-value">{valor}</div>
        <div class="metric-label">{rotulo}</div>
    </div>
    """

def criar_cartao_tipo(valor, rotulo, cor="#3498db"):
    return f"""
    <div class="type-card" style="border-color: {cor};">
        <div class="metric-value">{valor}</div>
        <div class="metric-label">{rotulo}</div>
    </div>
    """

def obter_link_download(conteudo, nome_arquivo, texto):
    """Gerar um link de download para conteúdo de texto"""
    b64 = base64.b64encode(conteudo.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{nome_arquivo}" class="download-btn">{texto}</a>'

def exibir_tela_boas_vindas(arquivo_carregado=None):
    """Exibir tela de boas-vindas com informações do aplicativo"""
    # Título sem ícone
    st.markdown('<h1 class="main-header">Analisador de Dados</h1>', unsafe_allow_html=True)
    
    if arquivo_carregado:
        # Tela de boas-vindas com arquivo carregado (sem seção "Arquivo Pronto para Análise")
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color: #3498db; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">🎯 Bem-vindo ao Analisador de Dados!</h2>
            <p style="font-size: 1rem; text-align: center; margin-bottom: 1rem;">
            Ferramenta avançada com IA para análise abrangente de conjuntos de dados e geração de insights.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Tela de boas-vindas padrão (sem arquivo carregado)
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color: #3498db; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">🎯 Bem-vindo ao Analisador de Dados!</h2>
            <p style="font-size: 1rem; text-align: center; margin-bottom: 1rem;">
            Ferramenta avançada com IA para análise abrangente de conjuntos de dados e geração de insights.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # CORREÇÃO: Recursos em um único cartão com layout melhorado
    st.markdown("### ✨ Recursos do Aplicativo")
    st.markdown("""
    <div class="feature-card">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #3498db;">📊 Suporte a Múltiplos Formatos</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Analise arquivos CSV, Excel (XLSX) e JSON com detecção automática de formato</p>
            </div>
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #2ecc71;">📈 Análise Inteligente de Dados</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Relatórios estatísticos abrangentes e perfilamento de dados com métricas detalhadas</p>
            </div>
            <div style="padding: 0.5rem;">
                <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #e74c3c;">🤖 Insights com IA</h4>
                <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Análise com LLM para descobrir padrões ocultos e inteligência de negócios</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CORREÇÃO: Como Usar e Dicas lado a lado com layout melhorado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Como Usar")
        if arquivo_carregado:
            # CORREÇÃO: Remover o cartão que mostra que o arquivo foi carregado com sucesso
            st.markdown("""
            <div class="card">
                <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                    <li style="margin-bottom: 0.8rem;"><strong>Selecione a planilha</strong> (se arquivo Excel) na barra lateral</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Clique em "Analisar Conjunto de Dados"</strong> na barra lateral para iniciar a análise</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Aguarde o processamento</strong> - detecção automática de formato e análise</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Explore os resultados</strong> nas abas de Análise Exploratória e Insights</li>
                    <li><strong>Baixe os relatórios</strong> para uso offline e documentação</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card">
                <ol style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                    <li style="margin-bottom: 0.8rem;"><strong>Carregue seu arquivo de dados</strong> - formato CSV, Excel (XLSX) ou JSON</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Selecione a planilha</strong> (se arquivo Excel) na barra lateral</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Clique em "Analisar Conjunto de Dados"</strong> para iniciar o processo de análise</li>
                    <li style="margin-bottom: 0.8rem;"><strong>Aguarde o processamento</strong> - detecção automática de formato e análise</li>
                    <li><strong>Explore os resultados</strong> nas abas de análise e baixe os relatórios</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Dicas - Layout melhorado (removido "Formatos Suportados")
        st.markdown("### 💡 Dicas para Melhores Resultados")
        st.markdown("""
        <div class="card">
            <ul style="font-size: 0.9rem; margin: 0.5rem 0; padding-left: 1.2rem; line-height: 1.6;">
                <li style="margin-bottom: 0.8rem;"><strong>Limpe os dados primeiro</strong> - Remova colunas desnecessárias antes de carregar</li>
                <li style="margin-bottom: 0.8rem;"><strong>Trate valores ausentes</strong> - Resolva valores nulos quando possível</li>
                <li style="margin-bottom: 0.8rem;"><strong>Cabeçalhos descritivos</strong> - Use nomes de colunas claros e significativos</li>
                <li><strong>Otimização de tamanho</strong> - Arquivos abaixo de 200MB para desempenho ideal</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def exibir_cartoes_tipos_coluna(analisador):
    """Exibir tipos de coluna como cartões em vez de gráfico de rosca"""
    if analisador is None or analisador.df is None:
        # Retornar cartões vazios se não houver dados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(criar_cartao_tipo(0, "Colunas Numéricas", "#3498db"), unsafe_allow_html=True)
        with col2:
            st.markdown(criar_cartao_tipo(0, "Colunas Categóricas", "#e74c3c"), unsafe_allow_html=True)
        with col3:
            st.markdown(criar_cartao_tipo(0, "Colunas Verdadeiro/Falso", "#2ecc71"), unsafe_allow_html=True)
        with col4:
            st.markdown(criar_cartao_tipo(0, "Colunas Data/Hora", "#f39c12"), unsafe_allow_html=True)
        return
    
    tipos_simples = analisador.obter_tipos_coluna_simples()
    
    # Obter contagens para cada tipo, garantindo que contagens zero sejam incluídas
    contagem_numericas = len(tipos_simples.get('Numéricas', []))
    contagem_categoricas = len(tipos_simples.get('Categóricas', []))
    contagem_booleanas = len(tipos_simples.get('Verdadeiro/Falso', []))
    contagem_data_hora = len(tipos_simples.get('Data/Hora', []))
    
    # Exibir como cartões
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(criar_cartao_tipo(contagem_numericas, "Colunas Numéricas", "#3498db"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(criar_cartao_tipo(contagem_categoricas, "Colunas Categóricas", "#e74c3c"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(criar_cartao_tipo(contagem_booleanas, "Colunas Verdadeiro/Falso", "#2ecc71"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(criar_cartao_tipo(contagem_data_hora, "Colunas Data/Hora", "#f39c12"), unsafe_allow_html=True)

def criar_mapa_calor_correlacao(df):
    """Criar mapa de calor de correlação para todas as variáveis"""
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para análise de correlação")
        return None
        
    # Criar uma cópia do dataframe para codificação
    df_codificado = df.copy()
    
    # Codificar variáveis categóricas
    for col in df_codificado.select_dtypes(include=['object', 'category']).columns:
        df_codificado[col] = pd.factorize(df_codificado[col])[0]
    
    # Codificar variáveis booleanas
    for col in df_codificado.select_dtypes(include='bool').columns:
        df_codificado[col] = df_codificado[col].astype(int)
    
    # Calcular matriz de correlação
    try:
        matriz_corr = df_codificado.corr()
        
        # Criar mapa de calor
        fig = px.imshow(
            matriz_corr,
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
    except Exception as e:
        st.error(f"Não foi possível gerar a matriz de correlação: {str(e)}")
        return None

def criar_scatterplot_interativo(df):
    """Criar gráfico de dispersão interativo otimizado para todos os tipos de variáveis"""
    if df is None or df.empty:
        return None
    
    # Obter todas as colunas disponíveis
    todas_colunas = df.columns.tolist()
    
    if len(todas_colunas) < 2:
        st.info("⚠️ É necessário pelo menos 2 colunas para gerar gráficos de dispersão.")
        return None
    
    # Inicializar estado da sessão para seleções
    if 'scatter_x' not in st.session_state:
        st.session_state.scatter_x = todas_colunas[0]
    if 'scatter_y' not in st.session_state:
        st.session_state.scatter_y = todas_colunas[1] if len(todas_colunas) > 1 else todas_colunas[0]
    
    # Criar interface de seleção
    col1, col2 = st.columns(2)
    
    with col1:
        nova_selecao_x = st.selectbox(
            "Selecionar Variável X:",
            options=todas_colunas,
            index=todas_colunas.index(st.session_state.scatter_x),
            key="select_x"
        )
    
    with col2:
        opcoes_y = [col for col in todas_colunas if col != nova_selecao_x]
        indice_y = opcoes_y.index(st.session_state.scatter_y) if st.session_state.scatter_y in opcoes_y else 0
        
        nova_selecao_y = st.selectbox(
            "Selecionar Variável Y:",
            options=opcoes_y,
            index=indice_y,
            key="select_y"
        )
    
    # Atualizar estado da sessão
    st.session_state.scatter_x = nova_selecao_x
    st.session_state.scatter_y = nova_selecao_y
    
    try:
        # Preparar dados
        df_plot = df[[st.session_state.scatter_x, st.session_state.scatter_y]].copy()
        
        # Determinar tipos de forma otimizada
        def classificar_tipo(serie):
            if pd.api.types.is_numeric_dtype(serie):
                return 'numerico'
            elif pd.api.types.is_datetime64_any_dtype(serie):
                return 'datetime'
            else:
                return 'categorico'
        
        tipo_x = classificar_tipo(df_plot[st.session_state.scatter_x])
        tipo_y = classificar_tipo(df_plot[st.session_state.scatter_y])
        
        # Criar gráfico baseado na combinação de tipos
        combinacao = f"{tipo_x}_{tipo_y}"
        
        if combinacao == 'numerico_numerico':
            # Scatter plot com linha de tendência
            fig = px.scatter(
                df_plot, 
                x=st.session_state.scatter_x, 
                y=st.session_state.scatter_y,
                title=f"Dispersão: {st.session_state.scatter_x} vs {st.session_state.scatter_y}",
                color_discrete_sequence=['#3498db']
            )
            
            # Adicionar linha de tendência
            dados_sem_na = df_plot.dropna()
            if len(dados_sem_na) > 1:
                try:
                    z = np.polyfit(dados_sem_na[st.session_state.scatter_x], dados_sem_na[st.session_state.scatter_y], 1)
                    p = np.poly1d(z)
                    fig.add_trace(go.Scatter(
                        x=dados_sem_na[st.session_state.scatter_x],
                        y=p(dados_sem_na[st.session_state.scatter_x]),
                        mode='lines', line=dict(color='#e74c3c', width=2, dash='dash'),
                        name='Linha de Tendência'
                    ))
                except:
                    pass
        
        elif combinacao in ['categorico_numerico', 'numerico_categorico']:
            # Box plot para categórico vs numérico
            if tipo_x == 'categorico':
                fig = px.box(df_plot, x=st.session_state.scatter_x, y=st.session_state.scatter_y,
                           title=f"Distribuição por Categoria: {st.session_state.scatter_y} vs {st.session_state.scatter_x}",
                           color=st.session_state.scatter_x)
            else:
                fig = px.box(df_plot, x=st.session_state.scatter_y, y=st.session_state.scatter_x,
                           title=f"Distribuição por Categoria: {st.session_state.scatter_x} vs {st.session_state.scatter_y}",
                           color=st.session_state.scatter_y)
        
        elif combinacao == 'categorico_categorico':
            # Gráfico de contagem para duas categóricas
            contagem = df_plot.groupby([st.session_state.scatter_x, st.session_state.scatter_y]).size().reset_index(name='count')
            fig = px.scatter(contagem, x=st.session_state.scatter_x, y=st.session_state.scatter_y, size='count',
                           title=f"Relação entre Categorias: {st.session_state.scatter_x} vs {st.session_state.scatter_y}",
                           color='count', color_continuous_scale='Viridis')
        
        elif 'datetime' in combinacao:
            # Gráfico temporal
            if tipo_x == 'datetime':
                df_temporal = df_plot.groupby(st.session_state.scatter_x)[st.session_state.scatter_y].mean().reset_index()
                fig = px.line(df_temporal, x=st.session_state.scatter_x, y=st.session_state.scatter_y,
                            title=f"Evolução Temporal: {st.session_state.scatter_y}", markers=True)
            else:
                df_temporal = df_plot.groupby(st.session_state.scatter_y)[st.session_state.scatter_x].mean().reset_index()
                fig = px.line(df_temporal, x=st.session_state.scatter_y, y=st.session_state.scatter_x,
                            title=f"Evolução Temporal: {st.session_state.scatter_x}", markers=True)
        
        else:
            # Gráfico genérico como fallback
            fig = px.scatter(df_plot, x=st.session_state.scatter_x, y=st.session_state.scatter_y,
                           title=f"Relação: {st.session_state.scatter_x} vs {st.session_state.scatter_y}")
        
        # Configuração comum do layout
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        # Ajustar ângulo dos ticks para categorias
        if tipo_x == 'categorico':
            fig.update_xaxes(tickangle=45)
        if tipo_y == 'categorico':
            fig.update_yaxes(tickangle=45)
            
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")
        return None

def exibir_analise_exploratoria(resultados):
    """Exibir análise exploratória de dados com abas"""
    st.markdown('<div class="section-header">📊 Análise Exploratória de Dados</div>', unsafe_allow_html=True)
    
    # Botão de download
    if 'analise_ia' in resultados and 'estatisticas' in resultados:
        relatorio_combinado = f"# Relatório de Análise de Dados\n\n## Estatísticas Descritivas\n\n{resultados['estatisticas']}\n\n## Análise IA\n\n{resultados['analise_ia']}"
        st.markdown(obter_link_download(relatorio_combinado, "relatorio_analise_completo.txt", "📥 Baixar Relatório Completo (TXT)"), unsafe_allow_html=True)
    
    # Cartões de visão geral
    df = resultados['dataframe']
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(criar_cartao_estatistica(f"{df.shape[0]:,}", "Total de Linhas", "📈", "#2ecc71"), unsafe_allow_html=True)
    with col2:
        st.markdown(criar_cartao_estatistica(f"{df.shape[1]}", "Total de Colunas", "📊", "#3498db"), unsafe_allow_html=True)
    with col3:
        st.markdown(criar_cartao_estatistica(f"{df.isnull().sum().sum():,}", "Valores Ausentes", "⚠️", "#f39c12"), unsafe_allow_html=True)
    with col4:
        st.markdown(criar_cartao_estatistica(f"{df.duplicated().sum():,}", "Linhas Duplicadas", "🔍", "#e74c3c"), unsafe_allow_html=True)
    with col5:
        total_celulas = df.shape[0] * df.shape[1]
        st.markdown(criar_cartao_estatistica(f"{total_celulas:,}", "Total de Células", "🔢", "#9b59b6"), unsafe_allow_html=True)
    
    # Tipos de coluna como cartões
    analisador = st.session_state.analisador
    exibir_cartoes_tipos_coluna(analisador)
    
    # Criar abas para diferentes tipos de dados
    nomes_abas = ["Visão Geral"]
    tipos_simples = analisador.obter_tipos_coluna_simples()
    
    if tipos_simples['Numéricas']:
        nomes_abas.append("Colunas Numéricas")
    if tipos_simples['Categóricas']:
        nomes_abas.append("Colunas Categóricas")
    if tipos_simples['Verdadeiro/Falso']:
        nomes_abas.append("Colunas Verdadeiro/Falso")
    if tipos_simples['Data/Hora']:
        nomes_abas.append("Colunas Data/Hora")
    
    abas = st.tabs(nomes_abas)
    
    # Aba Visão Geral
    with abas[0]:
        exibir_aba_visao_geral(resultados)
    
    # Aba Colunas Numéricas
    if tipos_simples['Numéricas']:
        indice_aba = nomes_abas.index("Colunas Numéricas")
        with abas[indice_aba]:
            exibir_aba_numericas(resultados)
    
    # Aba Colunas Categóricas
    if tipos_simples['Categóricas']:
        indice_aba = nomes_abas.index("Colunas Categóricas")
        with abas[indice_aba]:
            exibir_aba_categoricas(resultados)
    
    # Aba Colunas Verdadeiro/Falso
    if tipos_simples['Verdadeiro/Falso']:
        indice_aba = nomes_abas.index("Colunas Verdadeiro/Falso")
        with abas[indice_aba]:
            exibir_aba_booleanas(resultados)
    
    # Aba Colunas Data/Hora
    if tipos_simples['Data/Hora']:
        indice_aba = nomes_abas.index("Colunas Data/Hora")
        with abas[indice_aba]:
            exibir_aba_data_hora(resultados)

def exibir_aba_visao_geral(resultados):
    """Exibir conteúdo da aba de visão geral"""
    df = resultados['dataframe']
    analisador = st.session_state.analisador
    
    # Primeiras 10 linhas vs Últimas 10 linhas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Primeiras 10 Linhas")
        df_primeiras = df.head(10)
        st.dataframe(df_primeiras, use_container_width=True, height=350, hide_index=True)
    
    with col2:
        st.markdown("#### Últimas 10 Linhas")
        df_ultimas = df.tail(10)
        st.dataframe(df_ultimas, use_container_width=True, height=350, hide_index=True)
    
    # Informações das Colunas vs Linhas Duplicadas
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Informações das Colunas")
        info_coluna = analisador.obter_info_coluna_detalhada()
        st.dataframe(info_coluna, use_container_width=True, height=350, hide_index=True)
    
    with col4:
        st.markdown("#### Linhas Duplicadas")
        linhas_duplicadas = df[df.duplicated(keep=False)]
        
        if len(linhas_duplicadas) > 0:
            st.dataframe(linhas_duplicadas, use_container_width=True, height=350, hide_index=True)
        else:
            st.success("✅ Não existem linhas duplicadas no arquivo")
            st.info("O conjunto de dados não contém linhas duplicadas.")
    
    # Gráfico de dados vazios por variável
    st.markdown("### 📊 Volume de Dados Vazios por Variável")
    
    # Calcular dados vazios por coluna
    dados_vazios = df.isnull().sum()
    dados_vazios = dados_vazios[dados_vazios > 0]  # Apenas colunas com dados vazios
    
    if len(dados_vazios) > 0:
        fig_vazios = px.bar(
            x=dados_vazios.values,
            y=dados_vazios.index,
            orientation='h',
            title="Volume de Dados Vazios por Variável",
            color_discrete_sequence=['#3498db'],
            labels={'x': 'Quantidade de Valores Vazios', 'y': 'Variáveis'}
        )
        
        fig_vazios.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        
        # Adicionar anotações com porcentagens
        total_linhas = len(df)
        for i, (col, valor) in enumerate(zip(dados_vazios.index, dados_vazios.values)):
            percentual = (valor / total_linhas) * 100
            fig_vazios.add_annotation(
                x=valor,
                y=col,
                text=f"{percentual:.1f}%",
                showarrow=False,
                xshift=30,
                font=dict(color='white', size=10)
            )
        
        st.plotly_chart(fig_vazios, use_container_width=True)
    else:
        st.success("✅ Não existem dados vazios no arquivo")
        st.info("Todas as colunas estão completamente preenchidas sem valores ausentes.")
    
    # Gráfico de dispersão interativo
    st.markdown("### 📈 Gráfico de Dispersão Interativo")
    fig_scatter = criar_scatterplot_interativo(df)
    if fig_scatter:
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Mapa de calor de correlação
    st.markdown("### 🔗 Matriz de Correlação")
    try:
        fig_corr = criar_mapa_calor_correlacao(df)
        if fig_corr:
            st.plotly_chart(fig_corr, use_container_width=True)
    except Exception as e:
        st.error(f"Não foi possível gerar a matriz de correlação: {str(e)}")

def exibir_aba_numericas(resultados):
    """Exibir análise de colunas numéricas"""
    df = resultados['dataframe']
    colunas_numericas = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
    
    for col in colunas_numericas:
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
            
            st.metric("Valores Ausentes", f"{df[col].isnull().sum()}")
            
            # Visualizações
            col_viz1, col_viz2 = st.columns(2)
            with col_viz1:
                # Gráfico de área
                dados_grafico = df[col].dropna()
                if len(dados_grafico) > 0:
                    valores_hist, bordas_bin = np.histogram(dados_grafico, bins=50)
                    centros_bin = (bordas_bin[:-1] + bordas_bin[1:]) / 2
                    
                    fig_area = px.area(
                        x=centros_bin, 
                        y=valores_hist, 
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
            
            with col_viz2:
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

def exibir_aba_categoricas(resultados):
    """Exibir análise de colunas categóricas"""
    df = resultados['dataframe']
    colunas_categoricas = df.select_dtypes(include=['object', 'category', 'string']).columns
    
    for col in colunas_categoricas:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 🏷️ {col}")
            
            # Estatísticas
            contagem_unicos = df[col].nunique()
            contagem_ausentes = df[col].isnull().sum()
            valores_principais = df[col].value_counts().head(3)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Categorias Únicas", contagem_unicos)
                st.metric("Valores Ausentes", contagem_ausentes)
            
            with col2:
                st.markdown("**3 Categorias Principais:**")
                for valor, contagem in valores_principais.items():
                    st.write(f"- `{valor}`: {contagem} ocorrências")
            
            # Gráfico de barras com orientação condicional
            contagem_valores = df[col].value_counts().head(10)  # Apenas 10 principais
            
            if len(contagem_valores) <= 5:
                # Gráfico de barras horizontal para 5 ou menos categorias
                fig_barra = px.bar(
                    x=contagem_valores.values,
                    y=contagem_valores.index,
                    orientation='h',
                    title=f"Categorias Principais - {col}",
                    color_discrete_sequence=['#3498db']
                )
                fig_barra.update_layout(
                    xaxis_title="Contagem",
                    yaxis_title="Categorias",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
            else:
                # Gráfico de barras vertical para mais de 5 categorias
                fig_barra = px.bar(
                    x=contagem_valores.index,
                    y=contagem_valores.values,
                    title=f"Categorias Principais - {col}",
                    color_discrete_sequence=['#3498db']
                )
                fig_barra.update_layout(
                    xaxis_title="Categorias",
                    yaxis_title="Contagem",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
                fig_barra.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig_barra, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def exibir_aba_booleanas(resultados):
    """Exibir análise de colunas booleanas"""
    df = resultados['dataframe']
    colunas_booleanas = df.select_dtypes(include='bool').columns
    
    for col in colunas_booleanas:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### ✅ {col}")
            
            contagem_valores = df[col].value_counts()
            percentuais = df[col].value_counts(normalize=True) * 100
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Métricas
                for val, contagem in contagem_valores.items():
                    percentual = percentuais[val]
                    st.metric(
                        f"Contagem {val}", 
                        f"{contagem} ({percentual:.1f}%)"
                    )
            
            with col2:
                # Gráfico de rosca
                cores = {'True': 'rgba(46, 204, 113, 0.8)', 'False': 'rgba(231, 76, 60, 0.8)'}
                sequencia_cores = [cores.get(str(rotulo), '#3498db') for rotulo in contagem_valores.index]

                fig_rosca = px.pie(
                    values=contagem_valores.values,
                    names=[str(rotulo) for rotulo in contagem_valores.index],
                    title=f"Distribuição - {col}",
                    hole=0.5,
                    color_discrete_sequence=sequencia_cores
                )
                fig_rosca.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    marker=dict(line=dict(color="#000000", width=2)),
                    textfont=dict(color='white', size=14)
                )
                fig_rosca.update_layout(
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
                st.plotly_chart(fig_rosca, use_container_width=True)

def exibir_aba_data_hora(resultados):
    """Exibir análise de colunas data/hora"""
    df = resultados['dataframe']
    colunas_data_hora = df.select_dtypes(include=['datetime64']).columns
    
    for col in colunas_data_hora:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 📅 {col}")
            
            # Estatísticas
            data_min = df[col].min()
            data_max = df[col].max()
            intervalo_data = data_max - data_min
            
            # Data mais frequente
            contagem_datas = df[col].value_counts()
            data_mais_frequente = contagem_datas.index[0] if len(contagem_datas) > 0 else None
            contagem_mais_frequente = contagem_datas.iloc[0] if len(contagem_datas) > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Data Mais Antiga", data_min.strftime('%Y-%m-%d'))
                st.metric("Data Mais Recente", data_max.strftime('%Y-%m-%d'))
                st.metric("Intervalo de Datas", f"{intervalo_data.days} dias")
            
            with col2:
                if data_mais_frequente:
                    st.metric("Data Mais Frequente", data_mais_frequente.strftime('%Y-%m-%d'))
                    st.metric("Frequência", contagem_mais_frequente)
            
            # Gráfico de linha temporal
            dados_timeline = df[col].value_counts().sort_index()
            fig_timeline = px.line(
                x=dados_timeline.index,
                y=dados_timeline.values,
                title=f"Linha Temporal - {col}",
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

def exibir_insights_ia(resultados):
    """Exibir análise da IA com seções estruturadas"""
    st.markdown('<div class="section-header">🤖 Insights Gerados</div>', unsafe_allow_html=True)
    
    # Botão de download
    if 'analise_ia' in resultados and 'estatisticas' in resultados:
        relatorio_combinado = f"# Relatório de Análise de Dados\n\n## Estatísticas Descritivas\n\n{resultados['estatisticas']}\n\n## Análise IA\n\n{resultados['analise_ia']}"
        st.markdown(obter_link_download(relatorio_combinado, "relatorio_analise_completo.txt", "📥 Baixar Relatório Completo (TXT)"), unsafe_allow_html=True)
    
    if 'analise_ia' not in resultados or not resultados['analise_ia']:
        st.error("Nenhuma análise IA disponível. Por favor, execute a análise primeiro.")
        return
    
    texto_analise = resultados['analise_ia']
    
    # Extração de seções melhorada
    secoes = {
        'Resumo Executivo': '',
        'Análise Estatística Detalhada': '',
        'Identificação de Padrões': '',
        'Implicações para Negócios/Pesquisa': '',
        'Recomendações': ''
    }
    
    secao_atual = None
    linhas = texto_analise.split('\n')
    
    for linha in linhas:
        linha_limpa = linha.strip()
        
        # Verificar se esta linha inicia uma nova seção
        if any(cabecalho in linha_limpa.lower() for cabecalho in ['resumo executivo', 'resumo']):
            secao_atual = 'Resumo Executivo'
            continue
        elif any(cabecalho in linha_limpa.lower() for cabecalho in ['análise estatística detalhada', 'análise estatística']):
            secao_atual = 'Análise Estatística Detalhada'
            continue
        elif any(cabecalho in linha_limpa.lower() for cabecalho in ['identificação de padrões', 'análise de padrões', 'padrões']):
            secao_atual = 'Identificação de Padrões'
            continue
        elif any(cabecalho in linha_limpa.lower() for cabecalho in ['implicações para negócios/pesquisa', 'implicações', 'implicações de negócios', 'implicações de pesquisa']):
            secao_atual = 'Implicações para Negócios/Pesquisa'
            continue
        elif any(cabecalho in linha_limpa.lower() for cabecalho in ['recomendações', 'sugestões', 'próximos passos']):
            secao_atual = 'Recomendações'
            continue
        
        # Pular linhas vazias no início das seções
        if secao_atual and not linha_limpa and not secoes[secao_atual]:
            continue
            
        # Adicionar conteúdo à seção atual
        if secao_atual and linha_limpa:
            secoes[secao_atual] += linha + '\n'
    
    # Exibir cada seção
    secao_exibida = False
    for nome_secao, conteudo_secao in secoes.items():
        if conteudo_secao.strip():
            secao_exibida = True
            st.markdown(f'<div class="insight-section">', unsafe_allow_html=True)
            st.markdown(f"### {nome_secao}")
            st.markdown(conteudo_secao)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Se nenhuma seção foi extraída adequadamente, mostrar a análise bruta
    if not secao_exibida:
        st.markdown("""
        <div class="insight-section">
            <h3>Análise Completa</h3>
            <p>A análise IA não pôde ser analisada em seções específicas. Aqui está a análise completa:</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="card">{texto_analise}</div>', unsafe_allow_html=True)

def main():
    """Função principal do aplicativo"""
    # Inicializar estado da sessão
    if 'analisador' not in st.session_state:
        st.session_state.analisador = None
    if 'resultados_analise' not in st.session_state:
        st.session_state.resultados_analise = None
    if 'arquivo_carregado' not in st.session_state:
        st.session_state.arquivo_carregado = False
    if 'arquivo_atual' not in st.session_state:
        st.session_state.arquivo_atual = None
    if 'planilha_selecionada' not in st.session_state:
        st.session_state.planilha_selecionada = None
    if 'planilhas_excel' not in st.session_state:
        st.session_state.planilhas_excel = []
    
    # Inicializar analisador
    if not inicializar_analisador():
        return
    
    # Barra lateral
    with st.sidebar:
        st.markdown("## ⚙️ Configuração")
        
        # Upload de arquivo
        arquivo_carregado = st.file_uploader(
            "📁 Carregar Arquivo de Dados",
            type=['csv', 'xlsx', 'json'],
            help="Carregue arquivos CSV, Excel (XLSX) ou JSON"
        )
        
        # Lidar com upload de arquivo
        if arquivo_carregado is not None:
            # Verificar se o arquivo é diferente do atual
            if (st.session_state.arquivo_atual is None or 
                st.session_state.arquivo_atual.name != arquivo_carregado.name):
                
                st.session_state.arquivo_carregado = True
                st.session_state.arquivo_atual = arquivo_carregado
                st.session_state.resultados_analise = None
                st.session_state.planilha_selecionada = None
                st.session_state.planilhas_excel = []
                
                # Processar o arquivo carregado
                with st.spinner("🔄 Processando arquivo carregado..."):
                    try:
                        extensao_arquivo = arquivo_carregado.name.split('.')[-1].lower()
                        
                        if extensao_arquivo == 'csv':
                            df = pd.read_csv(arquivo_carregado)
                            st.session_state.analisador.carregar_dados(df)
                            st.success("✅ Arquivo CSV carregado com sucesso!")
                            
                        elif extensao_arquivo == 'xlsx':
                            arquivo_excel = pd.ExcelFile(arquivo_carregado)
                            nomes_planilhas = arquivo_excel.sheet_names
                            st.session_state.planilhas_excel = nomes_planilhas
                            
                            if len(nomes_planilhas) == 1:
                                df = pd.read_excel(arquivo_carregado, sheet_name=nomes_planilhas[0])
                                st.session_state.analisador.carregar_dados(df)
                                st.success(f"✅ Arquivo Excel carregado com sucesso! (Planilha: {nomes_planilhas[0]})")
                            else:
                                st.session_state.planilha_selecionada = None
                                st.info(f"📑 Arquivo Excel tem {len(nomes_planilhas)} planilhas. Por favor, selecione uma abaixo.")
                            
                        elif extensao_arquivo == 'json':
                            df = pd.read_json(arquivo_carregado)
                            st.session_state.analisador.carregar_dados(df)
                            st.success("✅ Arquivo JSON carregado com sucesso!")
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
                        st.session_state.arquivo_carregado = False
                        st.session_state.arquivo_atual = None
            
            # Seleção de planilha para arquivos Excel - CORREÇÃO: Condicional simplificada
            if (arquivo_carregado.name.endswith('.xlsx') and 
                st.session_state.planilha_selecionada is None and
                len(st.session_state.planilhas_excel) > 1):
                
                try:
                    planilha_selecionada = st.selectbox(
                        "📑 Selecionar Planilha",
                        st.session_state.planilhas_excel,
                        help="Escolha qual planilha analisar"
                    )
                    
                    if st.button("Carregar Planilha Selecionada", type="secondary"):
                        with st.spinner(f"🔄 Carregando planilha: {planilha_selecionada}..."):
                            df = pd.read_excel(arquivo_carregado, sheet_name=planilha_selecionada)
                            st.session_state.analisador.carregar_dados(df)
                            st.session_state.planilha_selecionada = planilha_selecionada
                            st.success(f"✅ Planilha '{planilha_selecionada}' carregada com sucesso!")
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao ler arquivo Excel: {str(e)}")
        
        # Botão de análise
        st.markdown("---")
        analise_clicada = st.button(
            "🚀 Analisar Conjunto de Dados",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.arquivo_carregado or st.session_state.analisador.df is None
        )
        
        if analise_clicada:
            if st.session_state.analisador.df is not None:
                with st.spinner("🤖 Analisando conjunto de dados com IA..."):
                    try:
                        resultados = st.session_state.analisador.analisar_conjunto_dados()
                        if resultados:
                            st.session_state.resultados_analise = resultados
                            st.success("✅ Análise concluída com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Análise falhou. Por favor, verifique seus dados e tente novamente.")
                    except Exception as e:
                        st.error(f"❌ Erro durante a análise: {str(e)}")
            else:
                st.error("❌ Por favor, carregue e carregue um arquivo de dados primeiro.")
        
        # Botão limpar análise
        if st.session_state.resultados_analise:
            if st.button("🗑️ Limpar Análise", type="secondary", use_container_width=True):
                st.session_state.resultados_analise = None
                st.session_state.arquivo_carregado = False
                st.session_state.arquivo_atual = None
                st.session_state.planilha_selecionada = None
                st.session_state.planilhas_excel = []
                st.session_state.analisador.df = None
                st.rerun()
    
    # Área de conteúdo principal - CORREÇÃO: Lógica de exibição corrigida
    if st.session_state.resultados_analise is not None:
        # Mostrar resultados da análise
        aba1, aba2 = st.tabs(["📊 Análise Exploratória de Dados", "🤖 Insights IA"])
        
        with aba1:
            exibir_analise_exploratoria(st.session_state.resultados_analise)
        
        with aba2:
            exibir_insights_ia(st.session_state.resultados_analise)
    
    elif st.session_state.arquivo_carregado and st.session_state.arquivo_atual is not None:
        # Mostrar tela de boas-vindas com arquivo carregado (mas sem análise ainda)
        exibir_tela_boas_vindas(arquivo_carregado=st.session_state.arquivo_atual)
    
    else:
        # Exibir tela de boas-vindas padrão
        exibir_tela_boas_vindas()

if __name__ == "__main__":
    main()