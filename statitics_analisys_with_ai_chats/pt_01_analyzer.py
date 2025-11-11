# pt_01_analyzer.py
import pandas as pd
import requests
import json
import os
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from scipy.stats import chi2_contingency, spearmanr, kendalltau, pearsonr
import scipy.stats as stats

try:
    import streamlit as st
    STREAMLIT_DISPONIVEL = True
except ImportError:
    STREAMLIT_DISPONIVEL = False

class AnalisadorChatBot:
    def __init__(self, chave_api: str = None):
        if chave_api is None:
            self.chave_api = self.obter_chave_api_segura()
        else:
            self.chave_api = chave_api
        
        if not self.chave_api:
            raise ValueError("Chave API não encontrada. Por favor, defina a variável de ambiente OPENROUTER_API_KEY ou crie o arquivo 'chave_api.txt'.")
        
        self.url_base = "https://openrouter.ai/api/v1/chat/completions"
        self.cabecalhos = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.chave_api}",
            "HTTP-Referer": "https://data-analyzer-pr.streamlit.app",
            "X-Title": "Analisador de Dados"
        }
        self.df = None
        self._cache_estatisticas = None
        self._cache_tipos = None

    # === MÉTODOS DE CONFIGURAÇÃO DA API ===
    def obter_chave_api_segura(self) -> Optional[str]:
        """Obter chave API com segurança"""
        if STREAMLIT_DISPONIVEL:
            try:
                if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
                    chave_api = st.secrets['OPENROUTER_API_KEY']
                    if chave_api and chave_api.strip():
                        return chave_api.strip()
            except Exception:
                pass
        
        chave_env = os.getenv('OPENROUTER_API_KEY')
        if chave_env and chave_env.strip():
            return chave_env.strip()
        
        return self.ler_chave_api_do_arquivo()

    def ler_chave_api_do_arquivo(self, caminho_arquivo: str = None) -> Optional[str]:
        """Ler chave API do arquivo local"""
        try:
            if caminho_arquivo is None:
                diretorio_atual = os.path.dirname(os.path.abspath(__file__))
                caminho_arquivo = os.path.join(diretorio_atual, "chave_api.txt")
            
            if not os.path.exists(caminho_arquivo):
                caminhos_alternativos = ["chave_api.txt", "./chave_api.txt", "../chave_api.txt"]
                for caminho_alt in caminhos_alternativos:
                    if os.path.exists(caminho_alt):
                        caminho_arquivo = caminho_alt
                        break
                else:
                    return None
            
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                conteudo = arquivo.read().strip()
                
                if conteudo.startswith('open_router:'):
                    chave = conteudo.split('open_router:')[1].strip()
                elif ':' in conteudo:
                    chave = conteudo.split(':', 1)[1].strip()
                else:
                    chave = conteudo.strip()
                
                return chave if chave else None
                    
        except Exception:
            return None

    # === MÉTODOS DE MANIPULAÇÃO DE DADOS ===
    def corrigir_tipos_incorretos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corrige tipos de dados automaticamente"""
        df = df.copy()
        n_amostra = max(1, int(len(df) * 0.05))
        df_amostra = df.sample(n=n_amostra, random_state=42) if len(df) > n_amostra else df
        
        for col in df.columns:
            if df[col].dtype == 'object':
                datetime_convertido = pd.to_datetime(df[col], errors='coerce')
                if datetime_convertido.notna().mean() > 0.7:
                    df[col] = datetime_convertido
                    continue
            
            valores_unicos = set(map(str, df_amostra[col].dropna().unique()))
            
            if valores_unicos.issubset({'0', '1', '0.0', '1.0', 0, 1, 0.0, 1.0}):
                df[col] = df[col].astype(bool)
            
            elif df[col].dtype == 'object':
                valores_texto = set(map(str.lower, map(str, df_amostra[col].dropna().unique())))
                valores_booleanos = {'true', 'false', 'sim', 'não', 'yes', 'no', 'v', 'f', 's', 'n'}
                
                if valores_texto.issubset(valores_booleanos):
                    mapa_booleanos = {
                        'true': True, 'false': False, 'sim': True, 'não': False,
                        'yes': True, 'no': False, '1': True, '0': False,
                        'v': True, 'f': False, 's': True, 'n': False
                    }
                    df[col] = (df[col].astype(str)
                                .str.strip()
                                .str.lower()
                                .map(mapa_booleanos)
                                .astype('boolean'))
        
        return df

    def carregar_dados(self, df: pd.DataFrame):
        """Carregar DataFrame no analisador"""
        self.df = df
        self.df = self.corrigir_tipos_incorretos(self.df)
        self._cache_estatisticas = None
        self._cache_tipos = None

    def detectar_formato_arquivo(self, caminho_arquivo: str) -> str:
        """Detectar formato do arquivo"""
        _, ext = os.path.splitext(caminho_arquivo)
        ext = ext.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext in ['.xlsx', '.xls']:
            return 'excel'
        elif ext == '.json':
            return 'json'
        else:
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    primeira_linha = f.readline().strip()
                    if primeira_linha.startswith('{') or primeira_linha.startswith('['):
                        return 'json'
                    elif ',' in primeira_linha:
                        return 'csv'
            except:
                pass
            
            return 'csv'

    def carregar_e_previsualizar_dados(self, caminho_arquivo: str, nome_planilha: str = None) -> pd.DataFrame:
        """Carregar arquivo CSV, Excel ou JSON"""
        try:
            formato_arquivo = self.detectar_formato_arquivo(caminho_arquivo)
            
            if formato_arquivo == 'csv':
                self.df = pd.read_csv(caminho_arquivo)
            elif formato_arquivo == 'excel':
                if nome_planilha:
                    self.df = pd.read_excel(caminho_arquivo, sheet_name=nome_planilha)
                else:
                    self.df = pd.read_excel(caminho_arquivo)
            elif formato_arquivo == 'json':
                self.df = pd.read_json(caminho_arquivo)
            else:
                raise ValueError(f"Formato não suportado: {formato_arquivo}")
            
            self.df = self.corrigir_tipos_incorretos(self.df)
            self._cache_estatisticas = None
            self._cache_tipos = None
            
            return self.df
            
        except Exception as e:
            if formato_arquivo == 'json':
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    self.df = pd.json_normalize(dados)
                    self.df = self.corrigir_tipos_incorretos(self.df)
                    self._cache_estatisticas = None
                    self._cache_tipos = None
                    return self.df
                except Exception:
                    pass
            return None

    # === MÉTODOS DE ANÁLISE ESTATÍSTICA ===
    def obter_tipos_coluna_simples(self) -> Dict[str, List[str]]:
        """Obter tipos de coluna simplificados (com cache)"""
        if self._cache_tipos is not None:
            return self._cache_tipos
            
        if self.df is None:
            return {
                'Numéricas': [], 'Categóricas': [], 
                'Verdadeiro/Falso': [], 'Data/Hora': []
            }
        
        colunas_numericas = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns.tolist()
        colunas_categoricas = self.df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        colunas_booleanas = self.df.select_dtypes(include='bool').columns.tolist()
        colunas_data_hora = self.df.select_dtypes(include=['datetime64', 'timedelta64']).columns.tolist()
        
        self._cache_tipos = {
            'Numéricas': colunas_numericas,
            'Categóricas': colunas_categoricas,
            'Verdadeiro/Falso': colunas_booleanas,
            'Data/Hora': colunas_data_hora
        }
        
        return self._cache_tipos

    def obter_info_coluna_detalhada(self) -> pd.DataFrame:
        """Obter informações detalhadas sobre cada coluna"""
        if self.df is None:
            return pd.DataFrame()
        
        info_colunas = []
        
        for col in self.df.columns:
            tipo_col = self._obter_tipo_dado_simples(self.df[col].dtype)
            contagem_nao_nulos = self.df[col].count()
            contagem_nulos = self.df[col].isnull().sum()
            percentual_nulos = (contagem_nulos / len(self.df)) * 100 if len(self.df) > 0 else 0
            valores_unicos = self.df[col].nunique()
            
            info_colunas.append({
                'Coluna': col, 'Tipo': tipo_col, 'Não Nulos': contagem_nao_nulos,
                'Nulos': contagem_nulos, '% Nulos': f"{percentual_nulos:.1f}%",
                'Valores Únicos': valores_unicos
            })
        
        return pd.DataFrame(info_colunas)

    def _obter_tipo_dado_simples(self, tipo_dado):
        """Converter tipo de dado para categoria simplificada"""
        if np.issubdtype(tipo_dado, np.number):
            return "Numérica"
        elif np.issubdtype(tipo_dado, np.bool_):
            return "Verdadeiro/Falso"
        elif np.issubdtype(tipo_dado, np.datetime64) or np.issubdtype(tipo_dado, np.timedelta64):
            return "Data/Hora"
        else:
            return "Categórica"

    def gerar_estatisticas_descritivas(self) -> str:
        """Gerar estatísticas descritivas abrangentes (com cache)"""
        if self._cache_estatisticas is not None:
            return self._cache_estatisticas
            
        if self.df is None:
            return "## ❌ Nenhum dado carregado\n\nPor favor, carregue um conjunto de dados primeiro."
            
        resumo_estatisticas = "# 📊 Relatório de Estatísticas Descritivas\n\n"
        
        # Visão Geral
        resumo_estatisticas += "## 📋 Visão Geral do Conjunto de Dados\n\n"
        resumo_estatisticas += f"- **Total de Linhas**: {self.df.shape[0]:,}\n"
        resumo_estatisticas += f"- **Total de Colunas**: {self.df.shape[1]}\n"
        resumo_estatisticas += f"- **Valores Ausentes**: {self.df.isnull().sum().sum()}\n"
        resumo_estatisticas += f"- **Linhas Duplicadas**: {self.df.duplicated().sum()}\n\n"
        
        # Resumo de Tipos
        resumo_estatisticas += "## 🔧 Resumo de Tipos de Dados\n\n"
        tipos_simples = self.obter_tipos_coluna_simples()
        
        for tipo, colunas in tipos_simples.items():
            if colunas:
                resumo_estatisticas += f"- **{tipo}**: {len(colunas)} colunas\n"
        resumo_estatisticas += "\n"
        
        # Colunas numéricas
        if tipos_simples['Numéricas']:
            resumo_estatisticas += "## 🔢 Colunas Numéricas\n\n"
            for col in tipos_simples['Numéricas']:
                resumo_estatisticas += self._gerar_estatisticas_numericas(col)
        
        # Colunas categóricas
        if tipos_simples['Categóricas']:
            resumo_estatisticas += "## 📝 Colunas Categóricas\n\n"
            for col in tipos_simples['Categóricas']:
                resumo_estatisticas += self._gerar_estatisticas_categoricas(col)
        
        # Colunas booleanas
        if tipos_simples['Verdadeiro/Falso']:
            resumo_estatisticas += "## ✅ Colunas Verdadeiro/Falso\n\n"
            for col in tipos_simples['Verdadeiro/Falso']:
                resumo_estatisticas += self._gerar_estatisticas_booleanas(col)
        
        self._cache_estatisticas = resumo_estatisticas
        return resumo_estatisticas

    def _gerar_estatisticas_numericas(self, col: str) -> str:
        """Gerar estatísticas para coluna numérica"""
        estatisticas = f"### 📈 {col}\n\n"
        estatisticas += f"- **Média**: {self.df[col].mean():.2f}\n"
        estatisticas += f"- **Mediana**: {self.df[col].median():.2f}\n"
        estatisticas += f"- **Variância**: {self.df[col].var():.2f}\n"
        estatisticas += f"- **Desvio Padrão**: {self.df[col].std():.2f}\n"
        estatisticas += f"- **Mínimo**: {self.df[col].min():.2f}\n"
        estatisticas += f"- **Máximo**: {self.df[col].max():.2f}\n"
        estatisticas += f"- **Intervalo**: {self.df[col].max() - self.df[col].min():.2f}\n"
        estatisticas += f"- **Valores Ausentes**: {self.df[col].isnull().sum()}\n"
        estatisticas += f"- **Percentil 05**: {self.df[col].quantile(0.05):.2f}\n"
        estatisticas += f"- **Percentil 25**: {self.df[col].quantile(0.25):.2f}\n"
        estatisticas += f"- **Percentil 75**: {self.df[col].quantile(0.75):.2f}\n"
        estatisticas += f"- **Percentil 95**: {self.df[col].quantile(0.95):.2f}\n"
        estatisticas += f"- **IQR**: {self.df[col].quantile(0.75) - self.df[col].quantile(0.25):.2f}\n"
        
        media = self.df[col].mean()
        if media != 0:
            cv = (self.df[col].std() / media) * 100
            estatisticas += f"- **Coeficiente de Variação**: {cv:.2f}%\n"
        
        estatisticas += f"- **Curtose**: {self.df[col].kurt():.2f}\n"
        estatisticas += f"- **Assimetria**: {self.df[col].skew():.2f}\n\n"
        
        return estatisticas

    def _gerar_estatisticas_categoricas(self, col: str) -> str:
        """Gerar estatísticas para coluna categórica"""
        estatisticas = f"### 🏷️ {col}\n\n"
        estatisticas += f"- **Valores Únicos**: {self.df[col].nunique()}\n"
        estatisticas += f"- **Valores Ausentes**: {self.df[col].isnull().sum()}\n"
        estatisticas += f"- **3 Valores Principais**:\n"
        
        valores_principais = self.df[col].value_counts().head(3)
        for valor, contagem in valores_principais.items():
            estatisticas += f"  - `{valor}`: {contagem} ocorrências\n"
        estatisticas += "\n"
        
        return estatisticas

    def _gerar_estatisticas_booleanas(self, col: str) -> str:
        """Gerar estatísticas para coluna booleana"""
        estatisticas = f"### 🔘 {col}\n\n"
        contagem_valores = self.df[col].value_counts()
        percentual = self.df[col].value_counts(normalize=True) * 100
        
        estatisticas += f"- **Distribuição**:\n"
        for val, contagem in contagem_valores.items():
            estatisticas += f"  - `{val}`: {contagem} ({percentual[val]:.1f}%)\n"
        
        estatisticas += f"- **Variância**: {self.df[col].var():.2f}\n"
        estatisticas += f"- **Desvio Padrão**: {self.df[col].std():.2f}\n"
        estatisticas += f"- **Valores Ausentes**: {self.df[col].isnull().sum()}\n\n"
        
        return estatisticas

    # === MÉTODOS DE ANÁLISE COM IA ===
    def criar_prompt_analise(self, resumo_estatisticas: str, contexto_usuario: str = "") -> str:
        """Criar prompt detalhado para API"""
        if self.df is None:
            return "Nenhum dado disponível para análise"

        try:
            diretorio_atual = os.path.dirname(os.path.abspath(__file__))
            
            caminho_instrucoes_analise = os.path.join(diretorio_atual, "pt_instrucoes_analise.md")
            with open(caminho_instrucoes_analise, "r", encoding="utf-8") as f:
                bloco_de_instrucao_para_analise = f.read()
            
            caminho_instrucoes_insights = os.path.join(diretorio_atual, "pt_instrucoes_retorno_insights.md")
            with open(caminho_instrucoes_insights, "r", encoding="utf-8") as f:
                bloco_de_instrucao_retorno_insights = f.read()
                
        except Exception:
            bloco_de_instrucao_para_analise = "Analise os dados fornecidos de forma detalhada e profissional."
            bloco_de_instrucao_retorno_insights = "Forneça insights acionáveis e recomendações baseadas nos dados."

        input_de_contexto_usuario = contexto_usuario[:500] if contexto_usuario.strip() else "Nenhum contexto adicional fornecido pelo usuário."

        info_dataframe = f"""
        FORMATO DO DATASET: {self.df.shape[0]} linhas × {self.df.shape[1]} colunas
        COLUNAS: {', '.join(self.df.columns.tolist())}
        TIPOS PRINCIPAIS: {dict(self.df.dtypes.value_counts())}
        """

        prompt = f"""
        INSTRUÇÕES PARA ANÁLISE:
        {bloco_de_instrucao_para_analise}

        INFORMAÇÕES DO DATASET:
        {info_dataframe}

        CONTEXTO DO USUÁRIO:
        {input_de_contexto_usuario}

        ESTATÍSTICAS DETALHADAS:
        {resumo_estatisticas}

        FORMATO DA RESPOSTA:
        {bloco_de_instrucao_retorno_insights}

        IMPORTANTE: Seja conciso mas completo. Priorize insights acionáveis.
        """
        
        if len(prompt) > 12000:
            prompt = prompt[:12000] + "\n\n[Continuação cortada por limite de tamanho]"
        
        return prompt

    def chamar_api_open_router(self, prompt: str) -> Optional[str]:
        """Fazer chamada API para Open Router"""
        payload = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um analista de dados especialista com forte conhecimento estatístico. Forneça análises detalhadas e precisas com interpretações práticas. Formate sua resposta em markdown bonito com cabeçalhos adequados, pontos de lista e ênfase. Seja minucioso e profissional."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000,
            "stream": False
        }
        
        try:
            resposta = requests.post(self.url_base, headers=self.cabecalhos, json=payload, timeout=120)
            resposta.raise_for_status()
            
            resultado = resposta.json()
            return resultado['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de API: {e}")
            return None

    def analisar_conjunto_dados(self, contexto_usuario: str = "") -> Dict[str, Any]:
        """Analisar o conjunto de dados atualmente carregado"""
        if self.df is None:
            return None
        
        inicio_tempo = time.time()
        
        resumo_estatisticas = self.gerar_estatisticas_descritivas()
        prompt = self.criar_prompt_analise(resumo_estatisticas, contexto_usuario)
        resultado_analise = self.chamar_api_open_router(prompt)
        visualizacoes = self.gerar_visualizacoes()
        
        tempo_decorrido = time.time() - inicio_tempo
        
        if resultado_analise:
            return {
                'dataframe': self.df,
                'estatisticas': resumo_estatisticas,
                'analise_ia': resultado_analise,
                'visualizacoes': visualizacoes,
                'tempo_analise': tempo_decorrido
            }
        
        return None

    # === MÉTODOS DE VISUALIZAÇÃO ===
    def gerar_visualizacoes(self) -> Dict[str, go.Figure]:
        """Gerar visualizações interativas para o conjunto de dados"""
        if self.df is None or self.df.empty:
            return {}
        
        visualizacoes = {}
        amostra_df = self.df.sample(1000, random_state=42) if len(self.df) > 1000 else self.df
        
        try:
            # Gráfico de tipos de dados
            def categorizar_tipo_dado(tipo_dado):
                if np.issubdtype(tipo_dado, np.number):
                    return "Numérica"
                elif np.issubdtype(tipo_dado, np.bool_):
                    return "Booleana"
                elif np.issubdtype(tipo_dado, np.datetime64) or np.issubdtype(tipo_dado, np.timedelta64):
                    return "Data/Hora"
                else:
                    return "Categórica"
            
            contagem_tipos = self.df.dtypes.apply(categorizar_tipo_dado).value_counts()
            
            if len(contagem_tipos) > 0:
                fig_tipos = px.pie(
                    values=contagem_tipos.values,
                    names=contagem_tipos.index,
                    title="Distribuição de Tipos de Dados",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_tipos.update_traces(textposition='inside', textinfo='percent+label')
                fig_tipos.update_layout(height=400, showlegend=False)
                visualizacoes['tipos_dados'] = fig_tipos
            
            # Gráfico de dados ausentes
            dados_ausentes = self.df.isnull().sum()
            dados_ausentes = dados_ausentes[dados_ausentes > 0].head(15)
            if len(dados_ausentes) > 0:
                fig_ausentes = px.bar(
                    x=dados_ausentes.values,
                    y=dados_ausentes.index,
                    orientation='h',
                    title="Valores Ausentes por Coluna (Top 15)",
                    color=dados_ausentes.values,
                    color_continuous_scale='Viridis'
                )
                fig_ausentes.update_layout(height=400, xaxis_title="Contagem de Valores Ausentes", yaxis_title="Colunas")
                visualizacoes['dados_ausentes'] = fig_ausentes
            
            # Distribuições numéricas
            colunas_numericas = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
            if len(colunas_numericas) > 0:
                visualizacoes.update(self._gerar_distribuicoes_numericas(amostra_df, colunas_numericas))
            
            # Distribuições categóricas
            colunas_categoricas = self.df.select_dtypes(include=['object', 'category', 'string']).columns
            if len(colunas_categoricas) > 0:
                visualizacoes.update(self._gerar_distribuicoes_categoricas(amostra_df, colunas_categoricas))

            # Mapa de calor de correlação
            colunas_numericas_corr = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
            if len(colunas_numericas_corr) > 1:
                visualizacoes.update(self._gerar_mapa_calor_correlacao(amostra_df, colunas_numericas_corr))
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar visualizações: {e}")
        
        return visualizacoes

    def _gerar_distribuicoes_numericas(self, amostra_df: pd.DataFrame, colunas_numericas: List[str]) -> Dict[str, go.Figure]:
        """Gerar distribuições para colunas numéricas"""
        colunas_para_grafico = colunas_numericas[:6]
        n_cols = min(3, len(colunas_para_grafico))
        n_linhas = (len(colunas_para_grafico) + n_cols - 1) // n_cols
        
        fig_dist = make_subplots(
            rows=n_linhas, cols=n_cols,
            subplot_titles=colunas_para_grafico,
            horizontal_spacing=0.1,
            vertical_spacing=0.15
        )
        
        for i, col in enumerate(colunas_para_grafico):
            linha = i // n_cols + 1
            col_num = i % n_cols + 1
            
            fig_dist.add_trace(
                go.Histogram(x=amostra_df[col], name=col, nbinsx=20),
                row=linha, col=col_num
            )
        
        fig_dist.update_layout(height=300*n_linhas, title_text="Distribuições de Variáveis Numéricas (Amostra)", showlegend=False)
        
        return {'distribuicoes_numericas': fig_dist}

    def _gerar_distribuicoes_categoricas(self, amostra_df: pd.DataFrame, colunas_categoricas: List[str]) -> Dict[str, go.Figure]:
        """Gerar distribuições para colunas categóricas"""
        colunas_para_grafico = colunas_categoricas[:6]
        n_cols = min(3, len(colunas_para_grafico))
        n_linhas = (len(colunas_para_grafico) + n_cols - 1) // n_cols

        fig_dist_cat = make_subplots(
            rows=n_linhas, cols=n_cols,
            subplot_titles=colunas_para_grafico,
            horizontal_spacing=0.1,
            vertical_spacing=0.15
        )
        
        for i, col in enumerate(colunas_para_grafico):
            linha = i // n_cols + 1
            col_num = i % n_cols + 1
            
            contagem_valores = amostra_df[col].value_counts().head(8)
            fig_dist_cat.add_trace(
                go.Bar(x=contagem_valores.index, y=contagem_valores.values, name=col),
                row=linha, col=col_num
            )
            fig_dist_cat.update_xaxes(tickangle=45, row=linha, col=col_num)
        
        fig_dist_cat.update_layout(height=300*n_linhas, title_text="Distribuições de Variáveis Categóricas (Amostra)", showlegend=False)
        
        return {'distribuicoes_categoricas': fig_dist_cat}

    def _gerar_mapa_calor_correlacao(self, amostra_df: pd.DataFrame, colunas_numericas_corr: List[str]) -> Dict[str, go.Figure]:
        """Gerar mapa de calor de correlação"""
        matriz_corr = amostra_df[colunas_numericas_corr].corr()
        fig_corr = px.imshow(
            matriz_corr,
            title="Mapa de Calor de Correlação (Amostra)",
            color_continuous_scale='RdBu_r',
            aspect="auto"
        )
        fig_corr.update_layout(height=500)
        
        return {'mapa_calor_correlacao': fig_corr}

    # === MÉTODOS DE CORRELAÇÃO ===
    @staticmethod
    def cramers_v(x, y) -> float:
        """Calcula Cramér's V para duas variáveis categóricas"""
        try:
            mask = ~x.isna() & ~y.isna()
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(x_clean) == 0 or len(y_clean) == 0:
                return np.nan
                
            confusion_matrix = pd.crosstab(x_clean, y_clean)
            chi2 = chi2_contingency(confusion_matrix)[0]
            n = confusion_matrix.sum().sum()
            
            if n == 0:
                return np.nan
                
            phi2 = chi2 / n
            r, k = confusion_matrix.shape
            phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
            rcorr = r - ((r-1)**2)/(n-1)
            kcorr = k - ((k-1)**2)/(n-1)
            return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))
        except:
            return np.nan

    @staticmethod
    def theils_u(x, y) -> float:
        """Calcula Theil's U para duas variáveis categóricas"""
        try:
            if x.name == y.name:
                return 1.0
            
            mask = ~x.isna() & ~y.isna()
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(x_clean) == 0 or len(y_clean) == 0:
                return np.nan
            
            x_clean = x_clean.reset_index(drop=True)
            y_clean = y_clean.reset_index(drop=True)
            
            conditional_entropy = 0
            for value in x_clean.unique():
                mask_value = x_clean == value
                y_subset = y_clean[mask_value.values]
                prob = len(y_subset) / len(x_clean)
                if prob > 0 and len(y_subset) > 0:
                    value_counts = y_subset.value_counts(normalize=True)
                    value_counts = value_counts[value_counts > 0]
                    if len(value_counts) > 0:
                        entropy = -np.sum(value_counts * np.log2(value_counts))
                        conditional_entropy += prob * entropy
            
            y_value_counts = y_clean.value_counts(normalize=True)
            y_value_counts = y_value_counts[y_value_counts > 0]
            if len(y_value_counts) == 0:
                return 1.0
                
            y_entropy = -np.sum(y_value_counts * np.log2(y_value_counts))
            
            if y_entropy == 0:
                return 1.0
            
            return (y_entropy - conditional_entropy) / y_entropy
        except Exception as e:
            return np.nan

    @staticmethod
    def phi_coefficient(x, y) -> float:
        """Calcula coeficiente Phi para duas variáveis binárias"""
        try:
            mask = ~x.isna() & ~y.isna()
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(x_clean) == 0 or len(y_clean) == 0:
                return np.nan
                
            confusion_matrix = pd.crosstab(x_clean, y_clean)
            if confusion_matrix.shape != (2, 2):
                return np.nan
            
            a, b = confusion_matrix.iloc[0, 0], confusion_matrix.iloc[0, 1]
            c, d = confusion_matrix.iloc[1, 0], confusion_matrix.iloc[1, 1]
            
            numerator = a * d - b * c
            denominator = np.sqrt((a + b) * (c + d) * (a + c) * (b + d))
            
            return numerator / denominator if denominator != 0 else 0
        except:
            return np.nan

    @staticmethod
    def correlation_ratio(categories, values) -> float:
        """Calcula Correlation Ratio (eta) entre categórica e numérica"""
        try:
            mask = ~categories.isna() & ~values.isna()
            categories_clean = categories[mask]
            values_clean = values[mask]
            
            if len(categories_clean) == 0 or len(values_clean) == 0:
                return np.nan
            
            categories_clean = categories_clean.reset_index(drop=True)
            values_clean = values_clean.reset_index(drop=True)
            
            categories_coded = pd.Categorical(categories_clean)
            overall_mean = values_clean.mean()
            
            if np.isnan(overall_mean):
                return np.nan
            
            between_variance = 0
            for category in categories_coded.categories:
                mask_category = categories_coded == category
                group_values = values_clean[mask_category.values]
                if len(group_values) > 0:
                    group_mean = group_values.mean()
                    if not np.isnan(group_mean):
                        between_variance += len(group_values) * (group_mean - overall_mean) ** 2
            
            between_variance /= len(values_clean)
            total_variance = values_clean.var()
            
            if total_variance == 0:
                return 0
                
            return np.sqrt(between_variance / total_variance)
        except Exception as e:
            return np.nan

    def calcular_matriz_correlacao(self, metodo: str) -> pd.DataFrame:
        """Calcula matriz de correlação baseada no método selecionado"""
        if self.df is None:
            return pd.DataFrame()
            
        colunas = self.df.columns
        n = len(colunas)
        matriz = pd.DataFrame(np.zeros((n, n)), columns=colunas, index=colunas)
        
        for i, col1 in enumerate(colunas):
            for j, col2 in enumerate(colunas):
                if i == j:
                    matriz.iloc[i, j] = 1.0
                    continue
                    
                try:
                    if metodo == "Automático":
                        df_codificado = self.df.copy()
                        
                        for col in df_codificado.select_dtypes(include=['object', 'category']).columns:
                            df_codificado[col] = pd.factorize(df_codificado[col])[0]
                        
                        for col in df_codificado.select_dtypes(include='bool').columns:
                            df_codificado[col] = df_codificado[col].astype(int)
                        
                        if len(df_codificado) > 1:
                            corr_matrix = df_codificado.corr()
                            matriz.iloc[i, j] = corr_matrix.loc[col1, col2]
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                    elif metodo == "Pearson":
                        if pd.api.types.is_numeric_dtype(self.df[col1]) and pd.api.types.is_numeric_dtype(self.df[col2]):
                            mask = ~self.df[col1].isna() & ~self.df[col2].isna()
                            if mask.sum() > 1:
                                x = self.df.loc[mask, col1]
                                y = self.df.loc[mask, col2]
                                corr, _ = pearsonr(x, y)
                                matriz.iloc[i, j] = corr
                            else:
                                matriz.iloc[i, j] = np.nan
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                    elif metodo == "Spearman":
                        if pd.api.types.is_numeric_dtype(self.df[col1]) and pd.api.types.is_numeric_dtype(self.df[col2]):
                            mask = ~self.df[col1].isna() & ~self.df[col2].isna()
                            if mask.sum() > 1:
                                x = self.df.loc[mask, col1]
                                y = self.df.loc[mask, col2]
                                corr, _ = spearmanr(x, y)
                                matriz.iloc[i, j] = corr
                            else:
                                matriz.iloc[i, j] = np.nan
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                    elif metodo == "Kendall Tau":
                        if pd.api.types.is_numeric_dtype(self.df[col1]) and pd.api.types.is_numeric_dtype(self.df[col2]):
                            mask = ~self.df[col1].isna() & ~self.df[col2].isna()
                            if mask.sum() > 1:
                                x = self.df.loc[mask, col1]
                                y = self.df.loc[mask, col2]
                                corr, _ = kendalltau(x, y)
                                matriz.iloc[i, j] = corr
                            else:
                                matriz.iloc[i, j] = np.nan
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                    elif metodo == "Cramers V":
                        if (pd.api.types.is_object_dtype(self.df[col1]) or pd.api.types.is_categorical_dtype(self.df[col1])) and \
                           (pd.api.types.is_object_dtype(self.df[col2]) or pd.api.types.is_categorical_dtype(self.df[col2])):
                            matriz.iloc[i, j] = self.cramers_v(self.df[col1], self.df[col2])
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                    elif metodo == "Theils U":
                        if (pd.api.types.is_object_dtype(self.df[col1]) or pd.api.types.is_categorical_dtype(self.df[col1])) and \
                           (pd.api.types.is_object_dtype(self.df[col2]) or pd.api.types.is_categorical_dtype(self.df[col2])):
                            matriz.iloc[i, j] = self.theils_u(self.df[col1], self.df[col2])
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                    elif metodo == "Phi":
                        if (pd.api.types.is_object_dtype(self.df[col1]) or pd.api.types.is_categorical_dtype(self.df[col1])) and \
                           (pd.api.types.is_object_dtype(self.df[col2]) or pd.api.types.is_categorical_dtype(self.df[col2])):
                            matriz.iloc[i, j] = self.phi_coefficient(self.df[col1], self.df[col2])
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                    elif metodo == "Correlation Ratio":
                        if (pd.api.types.is_object_dtype(self.df[col1]) or pd.api.types.is_categorical_dtype(self.df[col1])) and \
                           pd.api.types.is_numeric_dtype(self.df[col2]):
                            matriz.iloc[i, j] = self.correlation_ratio(self.df[col1], self.df[col2])
                        elif (pd.api.types.is_object_dtype(self.df[col2]) or pd.api.types.is_categorical_dtype(self.df[col2])) and \
                             pd.api.types.is_numeric_dtype(self.df[col1]):
                            matriz.iloc[i, j] = self.correlation_ratio(self.df[col2], self.df[col1])
                        else:
                            matriz.iloc[i, j] = np.nan
                            
                except (ValueError, TypeError, ZeroDivisionError):
                    matriz.iloc[i, j] = np.nan
                
        return matriz

    def criar_mapa_calor_correlacao_completo(self, metodo: str) -> Tuple[Optional[go.Figure], Optional[pd.DataFrame]]:
        """Criar mapa de calor de correlação para todas as variáveis"""
        if self.df is None or self.df.empty:
            return None, None
            
        matriz_corr = self.calcular_matriz_correlacao(metodo)
        
        try:
            valores = matriz_corr.values
            valores = np.clip(valores, -1, 1)
            matriz_corr_clipped = pd.DataFrame(valores, 
                                             index=matriz_corr.index, 
                                             columns=matriz_corr.columns)
            
            fig = px.imshow(
                matriz_corr_clipped,
                title=f"Matriz de Correlação - {metodo}",
                color_continuous_scale='RdBu_r',
                aspect="auto",
                range_color=[-1, 1],
                labels=dict(color="Correlação"),
                zmin=-1,
                zmax=1
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
            
            return fig, matriz_corr
        except Exception as e:
            return None, matriz_corr

    # === MÉTODOS AUXILIARES ===
    def obter_planilhas_excel(self, caminho_arquivo: str) -> List[str]:
        """Obter lista de planilhas disponíveis em arquivo Excel"""
        try:
            if not os.path.exists(caminho_arquivo):
                return []
            
            tamanho_arquivo = os.path.getsize(caminho_arquivo)
            if tamanho_arquivo == 0:
                return []
            
            engines_para_tentar = []
            if caminho_arquivo.endswith('.xlsx'):
                engines_para_tentar = ['openpyxl', 'xlrd']
            elif caminho_arquivo.endswith('.xls'):
                engines_para_tentar = ['xlrd', 'openpyxl']
            else:
                engines_para_tentar = ['openpyxl', 'xlrd']
            
            planilhas = []
            engine_sucesso = None
            
            for engine in engines_para_tentar:
                try:
                    arquivo_excel = pd.ExcelFile(caminho_arquivo, engine=engine)
                    planilhas = arquivo_excel.sheet_names
                    engine_sucesso = engine
                    break
                except ImportError:
                    continue
                except Exception:
                    continue
            
            if not planilhas and not engine_sucesso:
                try:
                    arquivo_excel = pd.ExcelFile(caminho_arquivo)
                    planilhas = arquivo_excel.sheet_names
                except Exception:
                    pass
            
            return planilhas
            
        except Exception:
            return []