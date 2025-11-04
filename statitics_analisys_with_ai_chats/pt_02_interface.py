import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import io

# Importar o analisador
try:
    from pt_01_analyzer import AnalisadorChatBot
except ImportError:
    st.error("❌ Módulo pt_01_analyzer não encontrado. Verifique se o arquivo está no diretório correto.")
    st.stop()

def inicializar_analisador():
    """Inicializar ou recuperar analisador da sessão"""
    if 'analisador' not in st.session_state:
        try:
            st.session_state.analisador = AnalisadorChatBot()
            st.session_state.dados_carregados = False
            st.session_state.df = None
        except Exception as e:
            st.error(f"❌ Erro ao inicializar analisador: {e}")
            return False
    return True

def carregar_dados_interface():
    """Interface para carregamento de dados"""
    st.header("📁 Carregar Dados")
    
    opcoes_carregamento = st.radio(
        "Selecione o método de carregamento:",
        ["📤 Upload de Arquivo", "📋 Colar Dados", "🎲 Dados de Exemplo"],
        horizontal=True
    )
    
    df = None
    
    if opcoes_carregamento == "📤 Upload de Arquivo":
        arquivo = st.file_uploader(
            "Faça upload do seu arquivo",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="Formatos suportados: CSV, Excel (XLSX, XLS), JSON"
        )
        
        if arquivo is not None:
            try:
                # Salvar arquivo temporariamente
                with open("temp_uploaded_file", "wb") as f:
                    f.write(arquivo.getbuffer())
                
                # Detectar formato
                if arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo)
                    st.success(f"✅ CSV carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
                
                elif arquivo.name.endswith(('.xlsx', '.xls')):
                    # Obter planilhas disponíveis
                    analisador_temp = AnalisadorChatBot()
                    planilhas = analisador_temp.obter_planilhas_excel("temp_uploaded_file")
                    
                    if planilhas:
                        planilha_selecionada = st.selectbox(
                            "Selecione a planilha:",
                            planilhas,
                            help="Escolha qual planilha do arquivo Excel carregar"
                        )
                        
                        if st.button("Carregar Planilha Selecionada"):
                            df = pd.read_excel(arquivo, sheet_name=planilha_selecionada)
                            st.success(f"✅ Excel carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
                    else:
                        st.error("❌ Não foi possível ler as planilhas do arquivo Excel")
                
                elif arquivo.name.endswith('.json'):
                    df = pd.read_json(arquivo)
                    st.success(f"✅ JSON carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
                
            except Exception as e:
                st.error(f"❌ Erro ao carregar arquivo: {e}")
    
    elif opcoes_carregamento == "📋 Colar Dados":
        dados_colados = st.text_area(
            "Cole seus dados (formato CSV):",
            height=200,
            help="Cole dados no formato CSV. A primeira linha deve conter os cabeçalhos das colunas."
        )
        
        if st.button("Carregar Dados Colados") and dados_colados:
            try:
                from io import StringIO
                df = pd.read_csv(StringIO(dados_colados))
                st.success(f"✅ Dados colados carregados: {df.shape[0]} linhas, {df.shape[1]} colunas")
            except Exception as e:
                st.error(f"❌ Erro ao processar dados colados: {e}")
    
    elif opcoes_carregamento == "🎲 Dados de Exemplo":
        exemplos = {
            "Vendas de Supermercado": "https://raw.githubusercontent.com/datasets/superstore/master/data/superstore.csv",
            "Iris Dataset": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
            "Titanic Dataset": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
        }
        
        exemplo_selecionado = st.selectbox("Selecione o dataset de exemplo:", list(exemplos.keys()))
        
        if st.button("Carregar Exemplo"):
            try:
                url = exemplos[exemplo_selecionado]
                df = pd.read_csv(url)
                st.success(f"✅ {exemplo_selecionado} carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
            except Exception as e:
                st.error(f"❌ Erro ao carregar exemplo: {e}")
    
    return df

def mostrar_visao_geral():
    """Mostrar visão geral do conjunto de dados"""
    st.header("📊 Visão Geral do Conjunto de Dados")
    
    if st.session_state.df is None:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um conjunto de dados primeiro.")
        return
    
    df = st.session_state.df
    analisador = st.session_state.analisador
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Linhas", f"{df.shape[0]:,}")
    with col2:
        st.metric("Total de Colunas", df.shape[1])
    with col3:
        st.metric("Valores Ausentes", f"{df.isnull().sum().sum():,}")
    with col4:
        st.metric("Linhas Duplicadas", f"{df.duplicated().sum():,}")
    
    # Abas para diferentes visualizações
    aba1, aba2, aba3, aba4 = st.tabs(["📋 Informações das Colunas", "📈 Estatísticas Descritivas", "🎯 Visualizações", "🔍 Heatmaps de Correlação"])
    
    with aba1:
        mostrar_informacoes_colunas(df, analisador)
    
    with aba2:
        mostrar_estatisticas_descritivas(analisador)
    
    with aba3:
        mostrar_visualizacoes(analisador)
    
    with aba4:
        mostrar_heatmaps_correlacao(analisador)

def mostrar_informacoes_colunas(df, analisador):
    """Mostrar informações detalhadas sobre as colunas"""
    st.subheader("📋 Informações das Colunas")
    
    # Tipos de dados por categoria
    tipos_coluna = analisador.obter_tipos_coluna_simples()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Numéricas", len(tipos_coluna['Numéricas']))
    with col2:
        st.metric("Categóricas", len(tipos_coluna['Categóricas']))
    with col3:
        st.metric("Verdadeiro/Falso", len(tipos_coluna['Verdadeiro/Falso']))
    with col4:
        st.metric("Data/Hora", len(tipos_coluna['Data/Hora']))
    
    # Tabela detalhada de informações das colunas
    st.subheader("📊 Detalhes das Colunas")
    info_detalhada = analisador.obter_info_coluna_detalhada()
    st.dataframe(info_detalhada, use_container_width=True)
    
    # Mostrar tipos de dados específicos
    for categoria, colunas in tipos_coluna.items():
        if colunas:
            with st.expander(f"🔍 {categoria} ({len(colunas)} colunas)"):
                for col in colunas:
                    st.write(f"**{col}** - {df[col].dtype}")
                    if categoria == "Numéricas":
                        col_stats = df[col].describe()
                        st.write(f"  Média: {col_stats['mean']:.2f}, Std: {col_stats['std']:.2f}")
                    elif categoria == "Categóricas":
                        st.write(f"  Valores únicos: {df[col].nunique()}")
                        top_valores = df[col].value_counts().head(3)
                        st.write(f"  Top 3: {', '.join([f'{k} ({v})' for k, v in top_valores.items()])}")

def mostrar_estatisticas_descritivas(analisador):
    """Mostrar estatísticas descritivas"""
    st.subheader("📈 Estatísticas Descritivas")
    
    if st.button("🔄 Gerar/Atualizar Estatísticas"):
        with st.spinner("Gerando estatísticas descritivas..."):
            estatisticas = analisador.gerar_estatisticas_descritivas()
            st.session_state.estatisticas_descritivas = estatisticas
    
    if 'estatisticas_descritivas' in st.session_state:
        st.markdown(st.session_state.estatisticas_descritivas)
    else:
        st.info("👆 Clique no botão acima para gerar estatísticas descritivas detalhadas.")

def mostrar_visualizacoes(analisador):
    """Mostrar visualizações do conjunto de dados"""
    st.subheader("🎯 Visualizações do Conjunto de Dados")
    
    if st.button("🔄 Gerar Visualizações"):
        with st.spinner("Gerando visualizações..."):
            visualizacoes = analisador.gerar_visualizacoes()
            st.session_state.visualizacoes = visualizacoes
    
    if 'visualizacoes' in st.session_state:
        visualizacoes = st.session_state.visualizacoes
        
        # Mostrar cada visualização
        for nome, fig in visualizacoes.items():
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Clique no botão acima para gerar visualizações do conjunto de dados.")

def mostrar_heatmaps_correlacao(analisador):
    """Mostrar heatmaps de correlação com diferentes métodos"""
    st.subheader("🔍 Heatmaps de Correlação")
    
    # Métodos de correlação disponíveis
    metodos_correlacao = {
        "pearson": "Pearson (Numérico-Numérico)",
        "spearman": "Spearman (Numérico-Numérico)",
        "kendall": "Kendall Tau (Numérico-Numérico)",
        "cramers_v": "Cramér's V (Categórico-Categórico)",
        "theils_u": "Theil's U (Categórico-Categórico)",
        "phi": "Phi (Binário-Binário)",
        "correlation_ratio": "Correlation Ratio (Categórico-Numérico)"
    }
    
    # Método atual (mantido para compatibilidade)
    metodo_atual = "Matriz de Correlação Atual"
    
    # Seleção do método
    col1, col2 = st.columns([2, 1])
    
    with col1:
        metodo_selecionado = st.selectbox(
            "Selecione o método de correlação:",
            [metodo_atual] + list(metodos_correlacao.keys()),
            format_func=lambda x: metodo_atual if x == metodo_atual else metodos_correlacao[x]
        )
    
    with col2:
        tipo_visualizacao = st.radio(
            "Visualização:",
            ["📊 Gráfico", "📋 Tabela"],
            horizontal=True
        )
    
    # Gerar heatmap baseado na seleção
    if st.button("🔄 Gerar Análise de Correlação"):
        with st.spinner(f"Gerando análise de correlação ({metodo_selecionado})..."):
            if metodo_selecionado == metodo_atual:
                # Usar método atual existente
                fig = analisador.gerar_matriz_correlacao()
                st.session_state.heatmap_figura = fig
                st.session_state.heatmap_tabela = None
            else:
                # Usar método avançado
                fig, tabela = analisador.gerar_matriz_correlacao_avancada(metodo_selecionado)
                st.session_state.heatmap_figura = fig
                st.session_state.heatmap_tabela = tabela
    
    # Mostrar resultados
    if 'heatmap_figura' in st.session_state:
        if tipo_visualizacao == "📊 Gráfico":
            st.plotly_chart(st.session_state.heatmap_figura, use_container_width=True)
            
            # Adicionar informações sobre o método
            with st.expander("ℹ️ Sobre este método de correlação"):
                if metodo_selecionado == metodo_atual:
                    st.markdown("""
                    **Matriz de Correlação Atual (Pearson)**
                    - Mede correlação linear entre variáveis numéricas
                    - Valores entre -1 (correlação negativa perfeita) e 1 (correlação positiva perfeita)
                    - 0 indica nenhuma correlação linear
                    """)
                elif metodo_selecionado == "pearson":
                    st.markdown("""
                    **Correlação de Pearson**
                    - Mede correlação linear entre variáveis numéricas contínuas
                    - Sensível a outliers
                    - Assume normalidade dos dados
                    - Ideal para relações lineares
                    """)
                elif metodo_selecionado == "spearman":
                    st.markdown("""
                    **Correlação de Spearman**
                    - Mede correlação monotônica (não necessariamente linear)
                    - Baseada em ranks (ordens)
                    - Menos sensível a outliers que Pearson
                    - Funciona bem com dados não-normais
                    """)
                elif metodo_selecionado == "kendall":
                    st.markdown("""
                    **Correlação de Kendall Tau**
                    - Mede correlação de ordens (rank correlation)
                    - Mais robusta que Spearman para amostras pequenas
                    - Menos sensível a outliers
                    - Interpretação baseada em probabilidades
                    """)
                elif metodo_selecionado == "cramers_v":
                    st.markdown("""
                    **Cramér's V**
                    - Mede associação entre variáveis categóricas
                    - Baseado no teste qui-quadrado
                    - Valores entre 0 (nenhuma associação) e 1 (associação perfeita)
                    - Ajustado para o número de categorias
                    """)
                elif metodo_selecionado == "theils_u":
                    st.markdown("""
                    **Theil's U (Coeficiente de Incerteza)**
                    - Mede associação assimétrica entre variáveis categóricas
                    - Indica redução na incerteza ao conhecer uma variável
                    - Valores entre 0 e 1
                    - Útil para relações de dependência direcional
                    """)
                elif metodo_selecionado == "phi":
                    st.markdown("""
                    **Coeficiente Phi**
                    - Mede associação entre variáveis binárias (2 categorias)
                    - Similar ao coeficiente de correlação para dados binários
                    - Valores entre -1 e 1
                    - Ideal para tabelas 2x2
                    """)
                elif metodo_selecionado == "correlation_ratio":
                    st.markdown("""
                    **Correlation Ratio (Eta)**
                    - Mede relação entre variável categórica e numérica
                    - Indica quanto da variância da numérica é explicada pela categórica
                    - Valores entre 0 e 1
                    - Análogo ao R² em ANOVA
                    """)
        
        else:  # Tabela
            if st.session_state.heatmap_tabela is not None:
                st.subheader("📋 Tabela de Correlação")
                st.dataframe(st.session_state.heatmap_tabela.style.background_gradient(cmap='RdBu_r', vmin=-1, vmax=1), use_container_width=True)
                
                # Opção para download
                csv = st.session_state.heatmap_tabela.to_csv().encode('utf-8')
                st.download_button(
                    label="📥 Download da Tabela de Correlação (CSV)",
                    data=csv,
                    file_name=f"correlacao_{metodo_selecionado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Tabela de correlação não disponível para o método selecionado.")
    
    else:
        st.info("👆 Clique no botão acima para gerar a análise de correlação.")

def main():
    """Função principal da aplicação"""
    st.set_page_config(
        page_title="Analisador de Dados - Visão Geral",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">📊 Analisador de Dados - Visão Geral</h1>', unsafe_allow_html=True)
    
    # Inicializar analisador
    if not inicializar_analisador():
        return
    
    # Sidebar para carregamento de dados
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Verificar se há dados carregados
        if st.session_state.dados_carregados and st.session_state.df is not None:
            st.success(f"✅ Dados carregados: {st.session_state.df.shape[0]} linhas × {st.session_state.df.shape[1]} colunas")
            
            if st.button("🔄 Recarregar Dados"):
                st.session_state.dados_carregados = False
                st.session_state.df = None
                st.rerun()
        else:
            # Carregar novos dados
            df = carregar_dados_interface()
            
            if df is not None:
                # Aplicar correção de tipos
                try:
                    df_corrigido = st.session_state.analisador.corrigir_tipos_incorretos(df)
                    st.session_state.df = df_corrigido
                    st.session_state.analisador.carregar_dados(df_corrigido)
                    st.session_state.dados_carregados = True
                    st.success("✅ Dados carregados e tipos corrigidos com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao processar dados: {e}")
    
    # Conteúdo principal
    if st.session_state.dados_carregados and st.session_state.df is not None:
        mostrar_visao_geral()
    else:
        # Tela de boas-vindas
        st.markdown("""
        ## 👋 Bem-vindo ao Analisador de Dados!
        
        Esta ferramenta permite que você:
        
        - 📤 **Carregue** seus dados de múltiplas fontes (CSV, Excel, JSON)
        - 🔍 **Explore** estatísticas descritivas e informações das colunas
        - 📈 **Visualize** distribuições e relações entre variáveis
        - 🔗 **Analise** correlações com diferentes métodos estatísticos
        - 🤖 **Obtenha insights** com IA sobre seus dados
        
        ### 🚀 Como começar:
        1. Use a sidebar à esquerda para carregar seus dados
        2. Escolha entre upload de arquivo, colagem de dados ou exemplos
        3. Explore as diferentes abas para analisar seus dados
        
        ### 📚 Métodos de Correlação Disponíveis:
        - **Pearson**: Correlação linear entre variáveis numéricas
        - **Spearman**: Correlação monotônica baseada em ranks
        - **Kendall Tau**: Correlação de ordens robusta
        - **Cramér's V**: Associação entre variáveis categóricas
        - **Theil's U**: Incerteza assimétrica entre categóricas
        - **Phi**: Associação entre variáveis binárias
        - **Correlation Ratio**: Relação categórico-numérica
        """)
        
        # Exemplo rápido de dados
        if st.button("🎲 Carregar Dataset de Exemplo (Iris)"):
            try:
                url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
                df = pd.read_csv(url)
                st.session_state.df = df
                st.session_state.analisador.carregar_dados(df)
                st.session_state.dados_carregados = True
                st.success("✅ Dataset Iris carregado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao carregar exemplo: {e}")

if __name__ == "__main__":
    main()