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
from scipy.stats import chi2_contingency, spearmanr, kendalltau, pearsonr
import scipy.stats as stats

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
        # Tela de boas-vindas com arquivo carregado
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
    
    # Recursos em um único cartão com layout melhorado
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
    
    # Como Usar e Dicas lado a lado com layout melhorado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Como Usar")
        if arquivo_carregado:
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
        # Dicas - Layout melhorado
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

def calcular_cramers_v(x, y):
    """Calcular Cramér's V para duas variáveis categóricas"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))

def calcular_correlation_ratio(categorical_var, numerical_var):
    """Calcular Correlation Ratio (Eta) para variável categórica vs numérica"""
    categories = categorical_var.unique()
    y_mean = numerical_var.mean()
    category_means = numerical_var.groupby(categorical_var).mean()
    category_counts = numerical_var.groupby(categorical_var).count()
    
    ss_between = ((category_means - y_mean) ** 2 * category_counts).sum()
    ss_total = ((numerical_var - y_mean) ** 2).sum()
    
    return np.sqrt(ss_between / ss_total) if ss_total != 0 else 0

def calcular_phi(x, y):
    """Calcular coeficiente Phi para duas variáveis binárias"""
    confusion_matrix = pd.crosstab(x, y)
    if confusion_matrix.shape != (2, 2):
        return np.nan
    
    a, b = confusion_matrix.iloc[0, 0], confusion_matrix.iloc[0, 1]
    c, d = confusion_matrix.iloc[1, 0], confusion_matrix.iloc[1, 1]
    
    phi = (a*d - b*c) / np.sqrt((a+b)*(c+d)*(a+c)*(b+d))
    return phi

def calcular_theils_u(x, y):
    """Calcular Theil's U (incerteza) para duas variáveis categóricas"""
    def conditional_entropy(x, y):
        y_counts = y.value_counts(normalize=True)
        x_unique = x.unique()
        cond_entropy = 0
        for x_val in x_unique:
            y_given_x = y[x == x_val]
            if len(y_given_x) > 0:
                y_probs = y_given_x.value_counts(normalize=True)
                entropy = -np.sum(y_probs * np.log2(y_probs))
                cond_entropy += (len(y_given_x) / len(x)) * entropy
        return cond_entropy
    
    def entropy(series):
        probs = series.value_counts(normalize=True)
        return -np.sum(probs * np.log2(probs))
    
    h_y_given_x = conditional_entropy(x, y)
    h_y = entropy(y)
    
    return 1 - (h_y_given_x / h_y) if h_y != 0 else 0

def criar_matriz_correlacao_avancada(df, metodo):
    """Criar matriz de correlação usando diferentes métodos"""
    if df is None or df.empty:
        return None
    
    colunas_numericas = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
    colunas_categoricas = df.select_dtypes(include=['object', 'category', 'bool']).columns
    todas_colunas = df.columns
    
    n = len(todas_colunas)
    matriz_corr = pd.DataFrame(np.zeros((n, n)), index=todas_colunas, columns=todas_colunas)
    
    for i, col1 in enumerate(todas_colunas):
        for j, col2 in enumerate(todas_colunas):
            if i == j:
                matriz_corr.iloc[i, j] = 1.0
                continue
                
            if metodo == "Pearson":
                if col1 in colunas_numericas and col2 in colunas_numericas:
                    try:
                        corr, _ = pearsonr(df[col1].dropna(), df[col2].dropna())
                        matriz_corr.iloc[i, j] = corr
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                else:
                    matriz_corr.iloc[i, j] = np.nan
                    
            elif metodo == "Spearman":
                if col1 in colunas_numericas and col2 in colunas_numericas:
                    try:
                        corr, _ = spearmanr(df[col1].dropna(), df[col2].dropna())
                        matriz_corr.iloc[i, j] = corr
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                else:
                    matriz_corr.iloc[i, j] = np.nan
                    
            elif metodo == "Kendall Tau":
                if col1 in colunas_numericas and col2 in colunas_numericas:
                    try:
                        corr, _ = kendalltau(df[col1].dropna(), df[col2].dropna())
                        matriz_corr.iloc[i, j] = corr
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                else:
                    matriz_corr.iloc[i, j] = np.nan
                    
            elif metodo == "Cramers V":
                if col1 in colunas_categoricas and col2 in colunas_categoricas:
                    try:
                        corr = calcular_cramers_v(df[col1].dropna(), df[col2].dropna())
                        matriz_corr.iloc[i, j] = corr
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                else:
                    matriz_corr.iloc[i, j] = np.nan
                    
            elif metodo == "Theils U":
                if col1 in colunas_categoricas and col2 in colunas_categoricas:
                    try:
                        corr = calcular_theils_u(df[col1].dropna(), df[col2].dropna())
                        matriz_corr.iloc[i, j] = corr
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                else:
                    matriz_corr.iloc[i, j] = np.nan
                    
            elif metodo == "Phi":
                if col1 in colunas_categoricas and col2 in colunas_categoricas:
                    try:
                        corr = calcular_phi(df[col1].dropna(), df[col2].dropna())
                        matriz_corr.iloc[i, j] = corr if not np.isnan(corr) else 0
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                else:
                    matriz_corr.iloc[i, j] = np.nan
                    
            elif metodo == "Correlation Ratio":
                if col1 in colunas_categoricas and col2 in colunas_numericas:
                    try:
                        corr = calcular_correlation_ratio(df[col1].dropna(), df[col2].dropna())
                        matriz_corr.iloc[i, j] = corr
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                elif col1 in colunas_numericas and col2 in colunas_categoricas:
                    try:
                        corr = calcular_correlation_ratio(df[col2].dropna(), df[col1].dropna())
                        matriz_corr.iloc[i, j] = corr
                    except:
                        matriz_corr.iloc[i, j] = np.nan
                else:
                    matriz_corr.iloc[i, j] = np.nan
                    
            elif metodo == "Automático (Atual)":
                # Método atual - codificação automática
                df_codificado = df.copy()
                for col_temp in df_codificado.select_dtypes(include=['object', 'category']).columns:
                    df_codificado[col_temp] = pd.factorize(df_codificado[col_temp])[0]
                for col_temp in df_codificado.select_dtypes(include='bool').columns:
                    df_codificado[col_temp] = df_codificado[col_temp].astype(int)
                
                try:
                    matriz_temp = df_codificado.corr()
                    if col1 in matriz_temp.columns and col2 in matriz_temp.index:
                        matriz_corr.iloc[i, j] = matriz_temp.loc[col2, col1]
                    else:
                        matriz_corr.iloc[i, j] = np.nan
                except:
                    matriz_corr.iloc[i, j] = np.nan
    
    return matriz_corr

def criar_heatmap_interativo(df):
    """Criar interface interativa para múltiplos métodos de correlação"""
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para análise de correlação")
        return
    
    metodos_correlacao = [
        "Automático (Atual)",
        "Pearson", 
        "Spearman", 
        "Kendall Tau",
        "Cramers V",
        "Theils U", 
        "Phi",
        "Correlation Ratio"
    ]
    
    descricoes_metodos = {
        "Automático (Atual)": "Método atual - codificação automática de todas as variáveis",
        "Pearson": "Correlação linear entre variáveis numéricas",
        "Spearman": "Correlação de postos (monotônica) entre variáveis numéricas", 
        "Kendall Tau": "Correlação de postos baseada em concordâncias",
        "Cramers V": "Associação entre variáveis categóricas (baseado em Chi-quadrado)",
        "Theils U": "Medida de associação assimétrica entre categóricas",
        "Phi": "Correlação para variáveis binárias (2x2)",
        "Correlation Ratio": "Relação entre variável categórica e numérica"
    }
    
    # Seleção do método
    col1, col2 = st.columns([2, 1])
    
    with col1:
        metodo_selecionado = st.selectbox(
            "Selecionar Método de Correlação:",
            options=metodos_correlacao,
            index=0,
            key="metodo_correlacao"
        )
    
    with col2:
        visualizacao = st.radio(
            "Visualização:",
            options=["Gráfico Heatmap", "Tabela de Valores"],
            horizontal=True
        )
    
    # Descrição do método selecionado
    st.info(f"**{metodo_selecionado}**: {descricoes_metodos[metodo_selecionado]}")
    
    # Calcular matriz de correlação
    with st.spinner(f"Calculando matriz de correlação usando {metodo_selecionado}..."):
        matriz_corr = criar_matriz_correlacao_avancada(df, metodo_selecionado)
    
    if matriz_corr is None or matriz_corr.isna().all().all():
        st.error("Não foi possível calcular a matriz de correlação com o método selecionado.")
        return
    
    # Filtrar colunas com todos os valores NaN
    colunas_validas = matriz_corr.columns[~matriz_corr.isna().all()]
    matriz_corr_filtrada = matriz_corr.loc[colunas_validas, colunas_validas]
    
    if matriz_corr_filtrada.empty:
        st.warning("Nenhuma correlação válida encontrada com o método selecionado.")
        return
    
    if visualizacao == "Gráfico Heatmap":
        # Criar heatmap
        try:
            fig = px.imshow(
                matriz_corr_filtrada,
                title=f"Matriz de Correlação - {metodo_selecionado}",
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
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao criar heatmap: {str(e)}")
    
    else:  # Tabela de Valores
        st.markdown("#### Tabela de Correlação")
        
        # Formatar valores para exibição
        matriz_exibicao = matriz_corr_filtrada.copy()
        for col in matriz_exibicao.columns:
            matriz_exibicao[col] = matriz_exibicao[col].apply(
                lambda x: f"{x:.3f}" if not pd.isna(x) else "N/A"
            )
        
        st.dataframe(matriz_exibicao, use_container_width=True, height=400)
        
        # Estatísticas resumidas
        st.markdown("#### Estatísticas da Matriz")
        valores_correlacao = matriz_corr_filtrada.values.flatten()
        valores_correlacao = valores_correlacao[~np.isnan(valores_correlacao)]
        
        if len(valores_correlacao) > 0:
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                st.metric("Média", f"{np.mean(valores_correlacao):.3f}")
            with col_stat2:
                st.metric("Desvio Padrão", f"{np.std(valores_correlacao):.3f}")
            with col_stat3:
                st.metric("Mínimo", f"{np.min(valores_correlacao):.3f}")
            with col_stat4:
                st.metric("Máximo", f"{np.max(valores_correlacao):.3f}")

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
        # Preparar dados para visualização
        df_plot = df[[nova_selecao_x, nova_selecao_y]].copy()
        
        # Verificar tipos de dados
        tipo_x = str(df_plot[nova_selecao_x].dtype)
        tipo_y = str(df_plot[nova_selecao_y].dtype)
        
        # Criar scatter plot baseado nos tipos de dados
        if tipo_x in ['object', 'category', 'bool'] and tipo_y in ['object', 'category', 'bool']:
            # Ambas categóricas: usar gráfico de contagem
            contagem = df_plot.groupby([nova_selecao_x, nova_selecao_y]).size().reset_index(name='contagem')
            fig = px.scatter(
                contagem, 
                x=nova_selecao_x, 
                y=nova_selecao_y, 
                size='contagem',
                title=f"Relação entre {nova_selecao_x} e {nova_selecao_y}",
                size_max=30
            )
            
        elif tipo_x in ['object', 'category', 'bool'] and tipo_y not in ['object', 'category', 'bool']:
            # X categórico, Y numérico: box plot
            fig = px.box(
                df_plot, 
                x=nova_selecao_x, 
                y=nova_selecao_y,
                title=f"Distribuição de {nova_selecao_y} por {nova_selecao_x}"
            )
            
        elif tipo_x not in ['object', 'category', 'bool'] and tipo_y in ['object', 'category', 'bool']:
            # X numérico, Y categórico: box plot horizontal
            fig = px.box(
                df_plot, 
                y=nova_selecao_x, 
                x=nova_selecao_y,
                title=f"Distribuição de {nova_selecao_x} por {nova_selecao_y}"
            )
            
        else:
            # Ambas numéricas: scatter plot tradicional
            fig = px.scatter(
                df_plot, 
                x=nova_selecao_x, 
                y=nova_selecao_y,
                title=f"Relação entre {nova_selecao_x} e {nova_selecao_y}",
                trendline="lowess" if len(df_plot) > 10 else None
            )
        
        # Configurar layout
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")
        return None

def exibir_analise_exploratoria(analisador):
    """Exibir análise exploratória completa"""
    if analisador is None or analisador.df is None:
        st.warning("⚠️ Nenhum conjunto de dados carregado para análise.")
        return
    
    df = analisador.df
    
    # Criar abas para diferentes tipos de análise
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "📈 Correlações", 
        "📉 Distribuições",
        "🔍 Detalhes das Colunas",
        "📋 Dados Brutos"
    ])
    
    with tab1:
        st.markdown('<div class="section-header">📊 Visão Geral do Conjunto de Dados</div>', unsafe_allow_html=True)
        
        # Cartões de estatísticas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(criar_cartao_estatistica(
                len(df), 
                "Total de Linhas", 
                "📈", 
                "#3498db"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(criar_cartao_estatistica(
                len(df.columns), 
                "Total de Colunas", 
                "📋", 
                "#e74c3c"
            ), unsafe_allow_html=True)
        
        with col3:
            valores_ausentes = df.isnull().sum().sum()
            st.markdown(criar_cartao_estatistica(
                valores_ausentes, 
                "Valores Ausentes", 
                "⚠️", 
                "#f39c12"
            ), unsafe_allow_html=True)
        
        with col4:
            memoria_mb = df.memory_usage(deep=True).sum() / 1024**2
            st.markdown(criar_cartao_estatistica(
                f"{memoria_mb:.1f}MB", 
                "Uso de Memória", 
                "💾", 
                "#2ecc71"
            ), unsafe_allow_html=True)
        
        # Tipos de coluna
        st.markdown('<div class="subsection-header">📋 Tipos de Colunas</div>', unsafe_allow_html=True)
        exibir_cartoes_tipos_coluna(analisador)
        
        # Informações básicas
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown('<div class="subsection-header">📝 Informações do DataFrame</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="card">
                <p><strong>Forma do DataFrame:</strong> {} linhas × {} colunas</p>
                <p><strong>Intervalo de Índices:</strong> {} a {}</p>
                <p><strong>Colunas:</strong> {}</p>
            </div>
            """.format(
                len(df), len(df.columns),
                df.index[0], df.index[-1],
                ", ".join([f"<span class='format-badge'>{col}</span>" for col in df.columns[:8]]) + 
                ("..." if len(df.columns) > 8 else "")
            ), unsafe_allow_html=True)
        
        with col_info2:
            st.markdown('<div class="subsection-header">📊 Estatísticas de Dados</div>', unsafe_allow_html=True)
            colunas_numericas = df.select_dtypes(include=['int64', 'float64']).columns
            if len(colunas_numericas) > 0:
                estatisticas = df[colunas_numericas].describe()
                st.dataframe(estatisticas, use_container_width=True)
            else:
                st.info("ℹ️ Nenhuma coluna numérica encontrada para estatísticas descritivas.")
    
    with tab2:
        st.markdown('<div class="section-header">📈 Análise de Correlações</div>', unsafe_allow_html=True)
        
        # Scatter plot interativo
        st.markdown('<div class="subsection-header">🔍 Gráfico de Dispersão Interativo</div>', unsafe_allow_html=True)
        fig_scatter = criar_scatterplot_interativo(df)
        if fig_scatter:
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("⚠️ Não foi possível gerar o gráfico de dispersão com os dados atuais.")
        
        # Matriz de correlação
        st.markdown('<div class="subsection-header">📊 Matriz de Correlação Avançada</div>', unsafe_allow_html=True)
        criar_heatmap_interativo(df)
    
    with tab3:
        st.markdown('<div class="section-header">📉 Análise de Distribuições</div>', unsafe_allow_html=True)
        
        # Histogramas para colunas numéricas
        colunas_numericas = df.select_dtypes(include=['int64', 'float64']).columns
        if len(colunas_numericas) > 0:
            st.markdown('<div class="subsection-header">📊 Distribuições Numéricas</div>', unsafe_allow_html=True)
            
            # Selecionar coluna para histograma
            coluna_selecionada = st.selectbox(
                "Selecionar coluna para histograma:",
                options=colunas_numericas,
                key="histogram_col"
            )
            
            if coluna_selecionada:
                fig = px.histogram(
                    df, 
                    x=coluna_selecionada,
                    title=f"Distribuição de {coluna_selecionada}",
                    nbins=30,
                    opacity=0.8
                )
                fig.update_layout(
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Gráficos para colunas categóricas
        colunas_categoricas = df.select_dtypes(include=['object', 'category']).columns
        if len(colunas_categoricas) > 0:
            st.markdown('<div class="subsection-header">📋 Distribuições Categóricas</div>', unsafe_allow_html=True)
            
            coluna_cat_selecionada = st.selectbox(
                "Selecionar coluna categórica:",
                options=colunas_categoricas,
                key="bar_col"
            )
            
            if coluna_cat_selecionada:
                contagem = df[coluna_cat_selecionada].value_counts().head(15)
                fig = px.bar(
                    x=contagem.index,
                    y=contagem.values,
                    title=f"Distribuição de {coluna_cat_selecionada} (Top 15)",
                    labels={'x': coluna_cat_selecionada, 'y': 'Contagem'}
                )
                fig.update_layout(
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown('<div class="section-header">🔍 Detalhes das Colunas</div>', unsafe_allow_html=True)
        
        coluna_detalhes = st.selectbox(
            "Selecionar coluna para detalhes:",
            options=df.columns,
            key="col_details"
        )
        
        if coluna_detalhes:
            col_data = df[coluna_detalhes]
            tipo_dado = col_data.dtype
            valores_unicos = col_data.nunique()
            valores_ausentes = col_data.isnull().sum()
            percentual_ausentes = (valores_ausentes / len(col_data)) * 100
            
            col_det1, col_det2, col_det3, col_det4 = st.columns(4)
            
            with col_det1:
                st.metric("Tipo de Dado", str(tipo_dado))
            with col_det2:
                st.metric("Valores Únicos", valores_unicos)
            with col_det3:
                st.metric("Valores Ausentes", valores_ausentes)
            with col_det4:
                st.metric("Percentual Ausentes", f"{percentual_ausentes:.1f}%")
            
            # Estatísticas específicas por tipo
            if col_data.dtype in ['int64', 'float64']:
                st.markdown("#### Estatísticas Numéricas")
                stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                with stats_col1:
                    st.metric("Média", f"{col_data.mean():.2f}")
                with stats_col2:
                    st.metric("Mediana", f"{col_data.median():.2f}")
                with stats_col3:
                    st.metric("Desvio Padrão", f"{col_data.std():.2f}")
                with stats_col4:
                    st.metric("Intervalo", f"{col_data.min():.2f} - {col_data.max():.2f}")
            
            # Amostra de valores
            st.markdown("#### Amostra de Valores")
            st.write(col_data.head(10))
    
    with tab5:
        st.markdown('<div class="section-header">📋 Dados Brutos</div>', unsafe_allow_html=True)
        
        # Controles para visualização
        col_cont1, col_cont2, col_cont3 = st.columns(3)
        
        with col_cont1:
            linhas_mostrar = st.slider(
                "Número de linhas para mostrar:",
                min_value=10,
                max_value=1000,
                value=100,
                step=10
            )
        
        with col_cont2:
            colunas_mostrar = st.multiselect(
                "Colunas para mostrar:",
                options=df.columns.tolist(),
                default=df.columns.tolist()[:8] if len(df.columns) > 8 else df.columns.tolist()
            )
        
        with col_cont3:
            st.metric("Total de Linhas", len(df))
            st.metric("Total de Colunas", len(df.columns))
        
        # Exibir dados
        if colunas_mostrar:
            st.dataframe(df[colunas_mostrar].head(linhas_mostrar), use_container_width=True)
        else:
            st.dataframe(df.head(linhas_mostrar), use_container_width=True)

def exibir_analise_insights(analisador):
    """Exibir insights e análises avançadas"""
    if analisador is None or analisador.df is None:
        st.warning("⚠️ Nenhum conjunto de dados carregado para análise de insights.")
        return
    
    st.markdown('<div class="section-header">🤖 Análise de Insights com IA</div>', unsafe_allow_html=True)
    
    # Verificar se já temos insights
    if hasattr(analisador, 'insights') and analisador.insights:
        st.markdown('<div class="insight-section">', unsafe_allow_html=True)
        st.markdown(analisador.insights)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botão para gerar novos insights
        if st.button("🔄 Gerar Novos Insights", type="secondary"):
            with st.spinner("Gerando novos insights com IA..."):
                try:
                    analisador.gerar_insights_ia()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao gerar insights: {str(e)}")
    else:
        # Gerar insights pela primeira vez
        if st.button("🚀 Gerar Insights com IA", type="primary"):
            with st.spinner("Analisando dados e gerando insights com IA..."):
                try:
                    analisador.gerar_insights_ia()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao gerar insights: {str(e)}")
                    st.info("Verifique sua conexão com a internet e a configuração da chave API.")

def main():
    """Função principal da interface Streamlit"""
    
    # Inicializar analisador
    if not inicializar_analisador():
        return
    
    # Sidebar para upload e configurações
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #3498db; margin-bottom: 0.5rem;">⚙️ Configurações</h2>
            <p style="font-size: 0.9rem; opacity: 0.8;">Carregue e analise seus dados</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload de arquivo
        st.markdown("### 📁 Upload de Dados")
        arquivo_carregado = st.file_uploader(
            "Carregar arquivo de dados",
            type=['csv', 'xlsx', 'json'],
            key="file_uploader"
        )
        
        # Processar arquivo carregado
        if arquivo_carregado is not None:
            try:
                # Detectar tipo de arquivo
                extensao = arquivo_carregado.name.split('.')[-1].lower()
                
                # Limpar estado anterior se for um novo arquivo
                if 'current_file' not in st.session_state or st.session_state.current_file != arquivo_carregado.name:
                    st.session_state.analisador.limpar_analise()
                    st.session_state.current_file = arquivo_carregado.name
                
                # Ler arquivo baseado na extensão
                if extensao == 'csv':
                    df = pd.read_csv(arquivo_carregado)
                    st.session_state.analisador.df = df
                    st.success(f"✅ CSV carregado: {arquivo_carregado.name}")
                    
                elif extensao == 'xlsx':
                    # Para Excel, mostrar seletor de planilhas
                    xls = pd.ExcelFile(arquivo_carregado)
                    planilhas = xls.sheet_names
                    
                    if len(planilhas) > 1:
                        planilha_selecionada = st.selectbox(
                            "Selecionar planilha:",
                            options=planilhas,
                            key="sheet_selector"
                        )
                    else:
                        planilha_selecionada = planilhas[0]
                    
                    df = pd.read_excel(arquivo_carregado, sheet_name=planilha_selecionada)
                    st.session_state.analisador.df = df
                    st.success(f"✅ Excel carregado: {arquivo_carregado.name} ({planilha_selecionada})")
                    
                elif extensao == 'json':
                    df = pd.read_json(arquivo_carregado)
                    st.session_state.analisador.df = df
                    st.success(f"✅ JSON carregado: {arquivo_carregado.name}")
                
                # Exibir informações básicas do arquivo
                if st.session_state.analisador.df is not None:
                    df_info = st.session_state.analisador.df
                    st.markdown(f"""
                    <div class="card">
                        <p><strong>Arquivo:</strong> {arquivo_carregado.name}</p>
                        <p><strong>Formato:</strong> {extensao.upper()}</p>
                        <p><strong>Dimensões:</strong> {len(df_info)} linhas × {len(df_info.columns)} colunas</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
        
        # Botão de análise
        st.markdown("---")
        st.markdown("### 🔍 Análise")
        
        if st.session_state.analisador.df is not None:
            if st.button("📊 Analisar Conjunto de Dados", type="primary", use_container_width=True):
                with st.spinner("Analisando dados..."):
                    try:
                        # A análise exploratória já está sendo feita na exibição
                        st.success("✅ Análise concluída!")
                    except Exception as e:
                        st.error(f"❌ Erro na análise: {str(e)}")
        else:
            st.button("📊 Analisar Conjunto de Dados", disabled=True, use_container_width=True)
        
        # Informações da sessão
        st.markdown("---")
        st.markdown("### ℹ️ Informações")
        st.markdown("""
        <div class="card">
            <p><strong>Desenvolvido com:</strong></p>
            <p>• Streamlit</p>
            <p>• Pandas</p>
            <p>• Plotly</p>
            <p>• OpenRouter AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Conteúdo principal
    if st.session_state.analisador.df is not None:
        # Tabs principais
        tab_principal1, tab_principal2 = st.tabs(["📊 Análise Exploratória", "🤖 Insights com IA"])
        
        with tab_principal1:
            exibir_analise_exploratoria(st.session_state.analisador)
        
        with tab_principal2:
            exibir_analise_insights(st.session_state.analisador)
    else:
        # Tela de boas-vindas quando nenhum arquivo está carregado
        exibir_tela_boas_vindas()

if __name__ == "__main__":
    main()