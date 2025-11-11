# pt_02_interface.py
import streamlit as st
import pandas as pd
import tempfile
import os
import time
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

# CSS para tema escuro (mantido igual)
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
    /* ... (todo o resto do CSS mantido igual) */
</style>
""", unsafe_allow_html=True)

# === FUNÇÕES DE INTERFACE ===
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
    st.markdown('<h1 class="main-header">Analisador de Dados</h1>', unsafe_allow_html=True)
    
    if arquivo_carregado:
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color: #3498db; text-align: center; margin-bottom: 1rem; font-size: 1.5rem;">🎯 Contexto para Análise</h2>
            <p style="font-size: 1rem; text-align: center; margin-bottom: 1rem;">
            Forneça informações adicionais sobre seus dados para melhorar a análise (opcional).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💬 Contexto dos Dados (Opcional)")
        st.markdown("""
        <div class="card">
            <p style="font-size: 0.9rem; margin: 0.5rem 0; line-height: 1.4;">
            Forneça informações adicionais sobre seus dados para melhorar a análise. 
            Por exemplo: de onde são os dados, qual o objetivo da análise, quais são as colunas mais importantes, etc.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        contexto_usuario = st.text_area(
            "Descreva o contexto dos seus dados:",
            placeholder="Exemplo: Estes dados são de vendas de uma loja de varejo no ano de 2023. Gostaria de entender os fatores que impactam as vendas e identificar oportunidades de crescimento.",
            help="Fornecer contexto ajuda a IA a gerar insights mais relevantes.",
            key="contexto_usuario_input"
        )
        
        st.session_state.contexto_usuario = contexto_usuario
        
        st.markdown("### ✨ Próximos Passos")
        st.markdown("""
        <div class="feature-card">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <div style="padding: 0.5rem;">
                    <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #3498db;">📊 Verifique os Dados</h4>
                    <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Confirme se os dados foram carregados corretamente na visualização acima</p>
                </div>
                <div style="padding: 0.5rem;">
                    <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #2ecc71;">🔎 Adicione Contexto</h4>
                    <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Use o campo acima para descrever o contexto dos seus dados (opcional)</p>
                </div>
                <div style="padding: 0.5rem;">
                    <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #e74c3c;">🚀 Inicie a Análise</h4>
                    <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Clique em 'Analisar Conjunto de Dados' na barra lateral para iniciar</p>
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
                    <h4 style="margin: 0.5rem 0; font-size: 1rem; color: #e74c3c;">🔎 Insights Gerados</h4>
                    <p style="font-size: 0.9rem; margin: 0; line-height: 1.4;">Análise com LLM para descobrir padrões ocultos e inteligência de negócios</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Como Usar")
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
    """Exibir tipos de coluna como cartões"""
    if analisador is None or analisador.df is None:
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
    
    contagem_numericas = len(tipos_simples.get('Numéricas', []))
    contagem_categoricas = len(tipos_simples.get('Categóricas', []))
    contagem_booleanas = len(tipos_simples.get('Verdadeiro/Falso', []))
    contagem_data_hora = len(tipos_simples.get('Data/Hora', []))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(criar_cartao_tipo(contagem_numericas, "Colunas Numéricas", "#3498db"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(criar_cartao_tipo(contagem_categoricas, "Colunas Categóricas", "#e74c3c"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(criar_cartao_tipo(contagem_booleanas, "Colunas Verdadeiro/Falso", "#2ecc71"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(criar_cartao_tipo(contagem_data_hora, "Colunas Data/Hora", "#f39c12"), unsafe_allow_html=True)

def criar_scatterplot_interativo(df):
    """Criar gráfico de dispersão interativo otimizado para todos os tipos de variáveis"""
    if df is None or df.empty:
        return None
    
    todas_colunas = df.columns.tolist()
    
    if len(todas_colunas) < 2:
        st.info("⚠️ É necessário pelo menos 2 colunas para gerar gráficos de dispersão.")
        return None
    
    if (st.session_state.scatter_x is None or 
        st.session_state.scatter_x not in todas_colunas):
        st.session_state.scatter_x = todas_colunas[0]
    
    if (st.session_state.scatter_y is None or 
        st.session_state.scatter_y not in todas_colunas or
        st.session_state.scatter_y == st.session_state.scatter_x):
        outras_colunas = [col for col in todas_colunas if col != st.session_state.scatter_x]
        if outras_colunas:
            st.session_state.scatter_y = outras_colunas[0]
        else:
            st.session_state.scatter_y = st.session_state.scatter_x
    
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
        indice_y = 0
        if st.session_state.scatter_y in opcoes_y:
            indice_y = opcoes_y.index(st.session_state.scatter_y)
        
        nova_selecao_y = st.selectbox(
            "Selecionar Variável Y:",
            options=opcoes_y,
            index=indice_y,
            key="select_y"
        )
    
    st.session_state.scatter_x = nova_selecao_x
    st.session_state.scatter_y = nova_selecao_y
    
    try:
        df_plot = df[[st.session_state.scatter_x, st.session_state.scatter_y]].copy()
        
        def classificar_tipo(serie):
            if pd.api.types.is_numeric_dtype(serie):
                return 'numerico'
            elif pd.api.types.is_datetime64_any_dtype(serie):
                return 'datetime'
            else:
                return 'categorico'
        
        tipo_x = classificar_tipo(df_plot[st.session_state.scatter_x])
        tipo_y = classificar_tipo(df_plot[st.session_state.scatter_y])
        
        combinacao = f"{tipo_x}_{tipo_y}"
        
        if combinacao == 'numerico_numerico':
            fig = px.scatter(
                df_plot, 
                x=st.session_state.scatter_x, 
                y=st.session_state.scatter_y,
                title=f"Dispersão: {st.session_state.scatter_x} vs {st.session_state.scatter_y}",
                color_discrete_sequence=['#3498db']
            )
            
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
            if tipo_x == 'categorico':
                fig = px.box(df_plot, x=st.session_state.scatter_x, y=st.session_state.scatter_y,
                           title=f"Distribuição por Categoria: {st.session_state.scatter_y} vs {st.session_state.scatter_x}",
                           color=st.session_state.scatter_x)
            else:
                fig = px.box(df_plot, x=st.session_state.scatter_y, y=st.session_state.scatter_x,
                           title=f"Distribuição por Categoria: {st.session_state.scatter_x} vs {st.session_state.scatter_y}",
                           color=st.session_state.scatter_y)
        
        elif combinacao == 'categorico_categorico':
            contagem = df_plot.groupby([st.session_state.scatter_x, st.session_state.scatter_y]).size().reset_index(name='count')
            fig = px.scatter(contagem, x=st.session_state.scatter_x, y=st.session_state.scatter_y, size='count',
                           title=f"Relação entre Categorias: {st.session_state.scatter_x} vs {st.session_state.scatter_y}",
                           color='count', color_continuous_scale='Viridis')
        
        elif 'datetime' in combinacao:
            if tipo_x == 'datetime':
                df_temporal = df_plot.groupby(st.session_state.scatter_x)[st.session_state.scatter_y].mean().reset_index()
                fig = px.line(df_temporal, x=st.session_state.scatter_x, y=st.session_state.scatter_y,
                            title=f"Evolução Temporal: {st.session_state.scatter_y}", markers=True)
            else:
                df_temporal = df_plot.groupby(st.session_state.scatter_y)[st.session_state.scatter_x].mean().reset_index()
                fig = px.line(df_temporal, x=st.session_state.scatter_y, y=st.session_state.scatter_x,
                            title=f"Evolução Temporal: {st.session_state.scatter_x}", markers=True)
        
        else:
            fig = px.scatter(df_plot, x=st.session_state.scatter_x, y=st.session_state.scatter_y,
                           title=f"Relação: {st.session_state.scatter_x} vs {st.session_state.scatter_y}")
        
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        if tipo_x == 'categorico':
            fig.update_xaxes(tickangle=45)
        if tipo_y == 'categorico':
            fig.update_yaxes(tickangle=45)
            
        return fig
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")
        return None

# === FUNÇÕES DE EXIBIÇÃO DE ANÁLISE ===
def exibir_analise_exploratoria(resultados):
    """Exibir análise exploratória de dados com abas"""
    st.markdown('<div class="section-header">📊 Análise Exploratória de Dados</div>', unsafe_allow_html=True)
    
    if 'analise_ia' in resultados and 'estatisticas' in resultados:
        relatorio_combinado = f"# Relatório de Análise de Dados\n\n## Estatísticas Descritivas\n\n{resultados['estatisticas']}\n\n## Análise IA\n\n{resultados['analise_ia']}"
        st.markdown(obter_link_download(relatorio_combinado, "relatorio_analise_completo.txt", "📥 Baixar Relatório Completo (TXT)"), unsafe_allow_html=True)
    
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
    
    analisador = st.session_state.analisador
    exibir_cartoes_tipos_coluna(analisador)
    
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
    
    with abas[0]:
        exibir_aba_visao_geral(resultados)
    
    if tipos_simples['Numéricas']:
        indice_aba = nomes_abas.index("Colunas Numéricas")
        with abas[indice_aba]:
            exibir_aba_numericas(resultados)
    
    if tipos_simples['Categóricas']:
        indice_aba = nomes_abas.index("Colunas Categóricas")
        with abas[indice_aba]:
            exibir_aba_categoricas(resultados)
    
    if tipos_simples['Verdadeiro/Falso']:
        indice_aba = nomes_abas.index("Colunas Verdadeiro/Falso")
        with abas[indice_aba]:
            exibir_aba_booleanas(resultados)
    
    if tipos_simples['Data/Hora']:
        indice_aba = nomes_abas.index("Colunas Data/Hora")
        with abas[indice_aba]:
            exibir_aba_data_hora(resultados)

def exibir_aba_visao_geral(resultados):
    """Exibir conteúdo da aba de visão geral"""
    df = resultados['dataframe']
    analisador = st.session_state.analisador
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Primeiras 10 Linhas")
        df_primeiras = df.head(10)
        st.dataframe(df_primeiras, use_container_width=True, height=350, hide_index=True)
    
    with col2:
        st.markdown("#### Últimas 10 Linhas")
        df_ultimas = df.tail(10)
        st.dataframe(df_ultimas, use_container_width=True, height=350, hide_index=True)
    
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
    
    st.markdown("### 📊 Volume de Dados Vazios por Variável")
    
    dados_vazios = df.isnull().sum()
    dados_vazios = dados_vazios[dados_vazios > 0]
    
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
    
    st.markdown("### 📈 Gráfico de Dispersão Interativo")
    fig_scatter = criar_scatterplot_interativo(df)
    if fig_scatter:
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("### 🔗 Análise de Correlação - Múltiplos Métodos")
    
    metodos_correlacao = [
        "Automático", "Pearson", "Spearman", "Kendall Tau",
        "Cramers V", "Theils U", "Phi", "Correlation Ratio"
    ]
    
    col_metodo, col_viz = st.columns([1, 2])
    
    with col_metodo:
        metodo_selecionado = st.selectbox(
            "Selecione o Método de Correlação:",
            options=metodos_correlacao,
            index=0,
            help="Escolha o método de correlação apropriado para seus dados"
        )
        
        info_metodos = {
            "Automático": "Correlação de Pearson com codificação automática para todas as variáveis",
            "Pearson": "Correlação linear entre variáveis numéricas",
            "Spearman": "Correlação de postos para relações monotônicas",
            "Kendall Tau": "Correlação de postos mais robusta a outliers",
            "Cramers V": "Associação entre variáveis categóricas (0-1)",
            "Theils U": "Associação assimétrica entre categóricas (0-1)",
            "Phi": "Associação entre variáveis binárias (-1 a +1)",
            "Correlation Ratio": "Relação entre categórica e numérica (0-1)"
        }
        
        st.info(f"**{metodo_selecionado}**: {info_metodos[metodo_selecionado]}")
        
        tipo_visualizacao = st.radio(
            "Tipo de Visualização:",
            ["Gráfico Heatmap", "Tabela de Valores"],
            horizontal=True
        )
    
    with col_viz:
        analisador = st.session_state.analisador
        fig, matriz_corr = analisador.criar_mapa_calor_correlacao_completo(metodo_selecionado)
        
        if matriz_corr is not None:
            if tipo_visualizacao == "Gráfico Heatmap":
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Não foi possível gerar o gráfico de correlação")
            else:
                matriz_exibicao = matriz_corr.copy()
                matriz_exibicao = matriz_exibicao.clip(-1, 1)
                st.dataframe(matriz_exibicao.round(3), use_container_width=True, height=400)
                
                csv = matriz_exibicao.round(4).to_csv()
                st.download_button(
                    label="📥 Baixar Matriz de Correlação (CSV)",
                    data=csv,
                    file_name=f"matriz_correlacao_{metodo_selecionado.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning(f"❌ Não foi possível calcular a correlação usando {metodo_selecionado}")

def exibir_aba_numericas(resultados):
    """Exibir análise de colunas numéricas"""
    df = resultados['dataframe']
    colunas_numericas = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
    
    for col in colunas_numericas:
        with st.container():
            st.markdown(f'<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown(f"#### 📈 {col}")
            
            st.markdown("##### 📊 Estatísticas Gerais")
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
            
            with st.expander("📈 Estatísticas Avançadas", expanded=False):
                col3, col4 = st.columns(2)
                
                with col3:
                    st.metric("Percentil 5", f"{df[col].quantile(0.05):.2f}")
                    st.metric("Percentil 25 (Q1)", f"{df[col].quantile(0.25):.2f}")
                    st.metric("Percentil 75 (Q3)", f"{df[col].quantile(0.75):.2f}")
                    st.metric("Percentil 95", f"{df[col].quantile(0.95):.2f}")
                
                with col4:
                    iqr = df[col].quantile(0.75) - df[col].quantile(0.25)
                    st.metric("IQR (Q3 - Q1)", f"{iqr:.2f}")
                    
                    media = df[col].mean()
                    desvio_padrao = df[col].std()
                    if media != 0:
                        cv = (desvio_padrao / media) * 100
                        st.metric("Coeficiente de Variação (CV)", f"{cv:.2f}%")
                    else:
                        st.metric("Coeficiente de Variação (CV)", "Indefinido (média zero)")
                    
                    curtose = df[col].kurt()
                    assimetria = df[col].skew()
                    st.metric("Curtose", f"{curtose:.2f}")
                    st.metric("Assimetria", f"{assimetria:.2f}")
            
            col_viz1, col_viz2 = st.columns(2)
            with col_viz1:
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
            
            contagem_unicos = df[col].nunique()
            contagem_ausentes = df[col].isnull().sum()
            
            col_met1, col_met2 = st.columns(2)
            with col_met1:
                st.metric("Categorias Únicas", contagem_unicos)
            with col_met2:
                st.metric("Valores Ausentes", contagem_ausentes)
            
            contagem_valores = df[col].value_counts().head(10)
            
            if len(contagem_valores) <= 5:
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
            
            st.markdown("##### 📋 Distribuição Completa das Categorias")
            
            distribuicao_completa = df[col].value_counts()
            percentuais = (df[col].value_counts(normalize=True) * 100).round(2)
            
            tabela_distribuicao = pd.DataFrame({
                'Categoria': distribuicao_completa.index,
                'Quantidade': distribuicao_completa.values,
                'Percentual (%)': percentuais.values
            })
            
            tabela_distribuicao = tabela_distribuicao.reset_index(drop=True)
            
            altura_tabela = max(200, min(400, 35 * len(tabela_distribuicao)))
            
            st.dataframe(
                tabela_distribuicao,
                use_container_width=True,
                height=altura_tabela,
                hide_index=True
            )
            
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
                for val, contagem in contagem_valores.items():
                    percentual = percentuais[val]
                    st.metric(
                        f"Contagem {val}", 
                        f"{contagem} ({percentual:.1f}%)"
                    )
            
            with col2:
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
            
            data_min = df[col].min()
            data_max = df[col].max()
            intervalo_data = data_max - data_min
            
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
    st.markdown('<div class="section-header">🔎 Insights Gerados</div>', unsafe_allow_html=True)
    
    if 'tempo_analise' in resultados:
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #2ecc71;">
            <p style="font-size: 1rem; margin: 0.5rem 0; color: #2ecc71;">
                ⏱️ <strong>Tempo de análise:</strong> {resultados['tempo_analise']:.2f} segundos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    if 'analise_ia' in resultados and 'estatisticas' in resultados:
        relatorio_combinado = f"# Relatório de Análise de Dados\n\n## Estatísticas Descritivas\n\n{resultados['estatisticas']}\n\n## Análise IA\n\n{resultados['analise_ia']}"
        st.markdown(obter_link_download(relatorio_combinado, "relatorio_analise_completo.txt", "📥 Baixar Relatório Completo (TXT)"), unsafe_allow_html=True)
    
    if 'analise_ia' not in resultados or not resultados['analise_ia']:
        st.error("Nenhuma análise IA disponível. Por favor, execute a análise primeiro.")
        return
    
    texto_analise = resultados['analise_ia']
    
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
        
        if secao_atual and not linha_limpa and not secoes[secao_atual]:
            continue
            
        if secao_atual and linha_limpa:
            secoes[secao_atual] += linha + '\n'
    
    secao_exibida = False
    for nome_secao, conteudo_secao in secoes.items():
        if conteudo_secao.strip():
            secao_exibida = True
            st.markdown(f'<div class="insight-section">', unsafe_allow_html=True)
            st.markdown(f"### {nome_secao}")
            st.markdown(conteudo_secao)
            st.markdown('</div>', unsafe_allow_html=True)
    
    if not secao_exibida:
        st.markdown("""
        <div class="insight-section">
            <h3>Análise Completa</h3>
            <p>A análise IA não pôde ser analisada em seções específicas. Aqui está a análise completa:</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="card">{texto_analise}</div>', unsafe_allow_html=True)

# === FUNÇÃO PRINCIPAL ===
def main():
    """Função principal do aplicativo"""
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
    if 'contexto_usuario' not in st.session_state:
        st.session_state.contexto_usuario = ""
    if 'scatter_x' not in st.session_state:
        st.session_state.scatter_x = None
    if 'scatter_y' not in st.session_state:
        st.session_state.scatter_y = None
    
    if not inicializar_analisador():
        return
    
    with st.sidebar:
        st.markdown("## ⚙️ Configuração")
        
        arquivo_carregado = st.file_uploader(
            "📁 Carregar Arquivo de Dados",
            type=['csv', 'xlsx', 'json'],
            help="Carregue arquivos CSV, Excel (XLSX) ou JSON"
        )
        
        if arquivo_carregado is not None:
            if (st.session_state.arquivo_atual is None or 
                st.session_state.arquivo_atual.name != arquivo_carregado.name):
                
                st.session_state.arquivo_carregado = True
                st.session_state.arquivo_atual = arquivo_carregado
                st.session_state.resultados_analise = None
                st.session_state.planilha_selecionada = None
                st.session_state.planilhas_excel = []
                st.session_state.contexto_usuario = ""
                st.session_state.scatter_x = None
                st.session_state.scatter_y = None
                
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
                            st.session_state.scatter_x = None
                            st.session_state.scatter_y = None
                            st.success(f"✅ Planilha '{planilha_selecionada}' carregada com sucesso!")
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao ler arquivo Excel: {str(e)}")
        
        st.markdown("---")
        analise_clicada = st.button(
            "🚀 Analisar Dados",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.arquivo_carregado or st.session_state.analisador.df is None
        )
        
        if analise_clicada:
            if st.session_state.analisador.df is not None:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def atualizar_progresso(fase, progresso):
                    status_text.text(f"⏳ {fase}...")
                    progress_bar.progress(progresso)
                
                with st.spinner("🔎 Iniciando análise completa..."):
                    try:
                        atualizar_progresso("Preparando dados", 10)
                        time.sleep(0.5)
                        
                        atualizar_progresso("Gerando estatísticas", 30)
                        time.sleep(0.3)
                        
                        contexto_usuario = st.session_state.get('contexto_usuario', '')
                        
                        atualizar_progresso("Solicitando análise da IA", 60)
                        resultados = st.session_state.analisador.analisar_conjunto_dados(contexto_usuario)
                        
                        atualizar_progresso("Processando resultados", 90)
                        
                        if resultados:
                            st.session_state.resultados_analise = resultados
                            atualizar_progresso("Análise concluída", 100)
                            st.success("✅ Análise concluída com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Análise falhou. Por favor, verifique seus dados e tente novamente.")
                            
                    except Exception as e:
                        st.error(f"❌ Erro durante a análise: {str(e)}")
                
                progress_bar.empty()
                status_text.empty()
            else:
                st.error("❌ Por favor, carregue e carregue um arquivo de dados primeiro.")
        
        if st.session_state.resultados_analise:
            if st.button("🗑️ Limpar Análise", type="secondary", use_container_width=True):
                st.session_state.resultados_analise = None
                st.session_state.arquivo_carregado = False
                st.session_state.arquivo_atual = None
                st.session_state.planilha_selecionada = None
                st.session_state.planilhas_excel = []
                st.session_state.analisador.df = None
                st.session_state.contexto_usuario = ""
                st.session_state.scatter_x = None
                st.session_state.scatter_y = None
                st.rerun()
    
    if st.session_state.resultados_analise is not None:
        aba1, aba2 = st.tabs(["📊 Análise Exploratória de Dados", "🔎 Insights IA"])
        with aba1:
            exibir_analise_exploratoria(st.session_state.resultados_analise)
        with aba2:
            exibir_insights_ia(st.session_state.resultados_analise)
    elif st.session_state.arquivo_carregado and st.session_state.arquivo_atual is not None:
        exibir_tela_boas_vindas(arquivo_carregado=st.session_state.arquivo_atual)
    else:
        exibir_tela_boas_vindas()

if __name__ == "__main__":
    main()