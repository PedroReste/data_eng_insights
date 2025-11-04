import pandas as pd
import requests
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, Optional, List
from scipy.stats import chi2_contingency
import scipy.stats as stats

# Importar streamlit no nível superior, mas lidar com o caso quando não estiver disponível
try:
    import streamlit as st
    STREAMLIT_DISPONIVEL = True
except ImportError:
    STREAMLIT_DISPONIVEL = False

class AnalisadorChatBot:
    def __init__(self, chave_api: str = None):
        # Prioridade: chave fornecida > Segredos do Streamlit > variável de ambiente > arquivo
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

    def obter_chave_api_segura(self) -> Optional[str]:
        """
        Obter chave API com segurança com prioridade:
        1. Segredos do Streamlit (se em ambiente Streamlit)
        2. Variável de Ambiente
        3. Arquivo local (apenas para desenvolvimento)
        """
        print(f"🔍 Iniciando busca da chave API...")
        print(f"🔍 STREAMLIT_DISPONIVEL: {STREAMLIT_DISPONIVEL}")
        
        # 1. Tentar Segredos do Streamlit
        if STREAMLIT_DISPONIVEL:
            try:
                print("🔍 Verificando segredos do Streamlit...")
                if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
                    chave_api = st.secrets['OPENROUTER_API_KEY']
                    print(f"🔍 Chave encontrada nos segredos, comprimento: {len(chave_api) if chave_api else 0}")
                    if chave_api and chave_api.strip():
                        print("✅ Chave API carregada dos Segredos do Streamlit")
                        return chave_api.strip()
                else:
                    print("❌ OPENROUTER_API_KEY não encontrada nos segredos do Streamlit")
            except Exception as e:
                print(f"⚠️ Segredos do Streamlit não acessíveis: {e}")
        
        # 2. Tentar Variável de Ambiente
        chave_env = os.getenv('OPENROUTER_API_KEY')
        print(f"🔍 Verificação de variável de ambiente: {'Encontrada' if chave_env else 'Não encontrada'}")
        if chave_env and chave_env.strip():
            print("✅ Chave API carregada da variável de ambiente")
            return chave_env.strip()
        
        # 3. Tentar arquivo local (apenas para desenvolvimento)
        chave_arquivo = self.ler_chave_api_do_arquivo()
        print(f"🔍 Verificação de arquivo: {'Encontrada' if chave_arquivo else 'Não encontrada'}")
        if chave_arquivo:
            print("✅ Chave API carregada do arquivo local")
            return chave_arquivo
        
        print("❌ Nenhuma chave API encontrada em nenhuma fonte")
        return None

    def ler_chave_api_do_arquivo(self, caminho_arquivo: str = None) -> Optional[str]:
        """
        Ler chave API do arquivo local (apenas para desenvolvimento)
        """
        try:
            if caminho_arquivo is None:
                diretorio_atual = os.path.dirname(os.path.abspath(__file__))
                caminho_arquivo = os.path.join(diretorio_atual, "chave_api.txt")
            
            print(f"🔍 Procurando arquivo de chave API em: {caminho_arquivo}")
            
            if not os.path.exists(caminho_arquivo):
                print(f"❌ Arquivo de chave API não encontrado: {caminho_arquivo}")
                # Tentar locais alternativos
                caminhos_alternativos = [
                    "chave_api.txt",
                    "./chave_api.txt", 
                    "../chave_api.txt",
                ]
                
                for caminho_alt in caminhos_alternativos:
                    if os.path.exists(caminho_alt):
                        caminho_arquivo = caminho_alt
                        print(f"✅ Arquivo de chave API encontrado em: {caminho_arquivo}")
                        break
                else:
                    print("❌ Arquivo de chave API não encontrado em locais comuns")
                    return None
            
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                conteudo = arquivo.read().strip()
                print(f"📄 Comprimento do conteúdo do arquivo de chave API: {len(conteudo)} caracteres")
                
                # Lidar com formatos possíveis diferentes
                if conteudo.startswith('open_router:'):
                    chave = conteudo.split('open_router:')[1].strip()
                elif ':' in conteudo:
                    chave = conteudo.split(':', 1)[1].strip()
                else:
                    chave = conteudo.strip()
                
                if chave:
                    print(f"✅ Chave API carregada com sucesso (primeiros 5 caracteres): {chave[:5]}...")
                    return chave
                else:
                    print("❌ Nenhuma chave API encontrada no arquivo")
                    return None
                    
        except Exception as e:
            print(f"❌ Erro ao ler arquivo de chave API: {e}")
            return None

    def corrigir_tipos_incorretos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Corrige apenas booleanos e datetime que foram identificados erroneamente
        Inclui conversão de colunas numéricas com apenas 0 e 1 para booleanas
        """
        df = df.copy()
        n_amostra = max(1, int(len(df) * 0.05))
        df_amostra = df.sample(n=n_amostra, random_state=42) if len(df) > n_amostra else df
        
        for col in df.columns:
            # 1. Corrigir datetime: se for object mas contém datas
            if df[col].dtype == 'object':
                # Tentar converter para datetime
                datetime_convertido = pd.to_datetime(df[col], errors='coerce')
                if datetime_convertido.notna().mean() > 0.7:  # 70% de sucesso na conversão
                    df[col] = datetime_convertido
                    continue  # Pular para próxima coluna se converteu para datetime
            
            # 2. Corrigir booleanos: verificar TODOS os tipos de dados, incluindo numéricos
            valores_unicos = set(map(str, df_amostra[col].dropna().unique()))
            
            # Verificar se são apenas 0 e 1 (em qualquer tipo de dado)
            if valores_unicos.issubset({'0', '1', '0.0', '1.0', 0, 1, 0.0, 1.0}):
                # Converter para booleano
                df[col] = df[col].astype(bool)
                print(f"🔧 Coluna '{col}' convertida de {df[col].dtype} para booleana (valores: 0/1)")
            
            # 3. Corrigir booleanos em colunas object com valores textuais
            elif df[col].dtype == 'object':
                valores_texto = set(map(str.lower, map(str, df_amostra[col].dropna().unique())))
                valores_booleanos = {'true', 'false', 'sim', 'não', 'yes', 'no', 'v', 'f', 's', 'n'}
                
                if valores_texto.issubset(valores_booleanos):
                    mapa_booleanos = {
                        'true': True, 'false': False,
                        'sim': True, 'não': False,
                        'yes': True, 'no': False,
                        '1': True, '0': False,
                        'v': True, 'f': False,
                        's': True, 'n': False
                    }
                    df[col] = (df[col].astype(str)
                                .str.strip()
                                .str.lower()
                                .map(mapa_booleanos)
                                .astype('boolean'))
                    print(f"🔧 Coluna '{col}' convertida de object para booleana")
        
        return df

    def carregar_dados(self, df: pd.DataFrame):
        """Carregar DataFrame no analisador com correção automática de tipos"""
        self.df = df
        print(f"✅ Dados carregados com sucesso: {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
        
        # Aplicar correção de tipos automaticamente
        self.df = self.corrigir_tipos_incorretos(self.df)
        print("🔧 Tipos de dados corrigidos automaticamente")

    def obter_planilhas_excel(self, caminho_arquivo: str) -> List[str]:
        """Obter lista de planilhas disponíveis em arquivo Excel"""
        try:
            print(f"📑 Tentando ler arquivo Excel: {caminho_arquivo}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(caminho_arquivo):
                print(f"❌ Arquivo não existe: {caminho_arquivo}")
                return []
            
            # Verificar tamanho do arquivo
            tamanho_arquivo = os.path.getsize(caminho_arquivo)
            print(f"📁 Tamanho do arquivo: {tamanho_arquivo} bytes")
            
            if tamanho_arquivo == 0:
                print("❌ Arquivo está vazio")
                return []
            
            # Tentar diferentes engines para leitura do Excel
            engines_para_tentar = []
            
            # Determinar quais engines tentar baseado na extensão do arquivo
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
                    print(f"🔧 Tentando engine: {engine}")
                    arquivo_excel = pd.ExcelFile(caminho_arquivo, engine=engine)
                    planilhas = arquivo_excel.sheet_names
                    engine_sucesso = engine
                    print(f"✅ Arquivo Excel lido com sucesso com {engine}. Planilhas encontradas: {planilhas}")
                    break
                except ImportError as e:
                    print(f"⚠️ Engine {engine} não disponível: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ Erro com engine {engine}: {e}")
                    continue
            
            if not planilhas and not engine_sucesso:
                # Última tentativa sem engine específica
                try:
                    print("🔧 Tentando engine padrão")
                    arquivo_excel = pd.ExcelFile(caminho_arquivo)
                    planilhas = arquivo_excel.sheet_names
                    print(f"✅ Arquivo Excel lido com sucesso com engine padrão. Planilhas encontradas: {planilhas}")
                except Exception as e:
                    print(f"❌ Falha ao ler arquivo Excel com qualquer engine: {e}")
            
            return planilhas
            
        except Exception as e:
            print(f"❌ Erro ao ler planilhas do Excel: {e}")
            # Log adicional para debug
            import traceback
            print(f"🔍 Stack trace: {traceback.format_exc()}")
            return []

    def obter_tipos_coluna_simples(self) -> Dict[str, List[str]]:
        """Obter tipos de coluna simplificados agrupados por categoria"""
        if self.df is None:
            return {
                'Numéricas': [],
                'Categóricas': [],
                'Verdadeiro/Falso': [],
                'Data/Hora': []
            }
        
        colunas_numericas = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns.tolist()
        colunas_categoricas = self.df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        colunas_booleanas = self.df.select_dtypes(include='bool').columns.tolist()
        colunas_data_hora = self.df.select_dtypes(include=['datetime64', 'timedelta64']).columns.tolist()
        
        return {
            'Numéricas': colunas_numericas,
            'Categóricas': colunas_categoricas,
            'Verdadeiro/Falso': colunas_booleanas,
            'Data/Hora': colunas_data_hora
        }

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
                'Coluna': col,
                'Tipo': tipo_col,
                'Não Nulos': contagem_nao_nulos,
                'Nulos': contagem_nulos,
                '% Nulos': f"{percentual_nulos:.1f}%",
                'Valores Únicos': valores_unicos
            })
        
        return pd.DataFrame(info_colunas)

    def _obter_tipo_dado_simples(self, tipo_dado):
        """Converter tipo de dado detalhado para categoria simplificada"""
        if np.issubdtype(tipo_dado, np.number):
            return "Numérica"
        elif np.issubdtype(tipo_dado, np.bool_):
            return "Verdadeiro/Falso"
        elif np.issubdtype(tipo_dado, np.datetime64) or np.issubdtype(tipo_dado, np.timedelta64):
            return "Data/Hora"
        else:
            return "Categórica"

    def detectar_formato_arquivo(self, caminho_arquivo: str) -> str:
        """Detectar formato do arquivo baseado na extensão e conteúdo"""
        _, ext = os.path.splitext(caminho_arquivo)
        ext = ext.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext in ['.xlsx', '.xls']:
            return 'excel'
        elif ext == '.json':
            return 'json'
        else:
            # Tentar detectar pelo conteúdo para arquivos sem extensão ou desconhecidos
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    primeira_linha = f.readline().strip()
                    # Verificar se é JSON
                    if primeira_linha.startswith('{') or primeira_linha.startswith('['):
                        return 'json'
                    # Verificar se é CSV (separado por vírgula)
                    elif ',' in primeira_linha:
                        return 'csv'
            except:
                pass
            
            # Padrão para CSV para formatos desconhecidos
            return 'csv'

    def carregar_e_previsualizar_dados(self, caminho_arquivo: str, nome_planilha: str = None) -> pd.DataFrame:
        """Carregar arquivo CSV, Excel ou JSON e retornar informações básicas"""
        try:
            formato_arquivo = self.detectar_formato_arquivo(caminho_arquivo)
            print(f"📁 Formato de arquivo detectado: {formato_arquivo}")
            
            if formato_arquivo == 'csv':
                self.df = pd.read_csv(caminho_arquivo)
            elif formato_arquivo == 'excel':
                if nome_planilha:
                    self.df = pd.read_excel(caminho_arquivo, sheet_name=nome_planilha)
                else:
                    # Carregar primeira planilha por padrão
                    self.df = pd.read_excel(caminho_arquivo)
            elif formato_arquivo == 'json':
                self.df = pd.read_json(caminho_arquivo)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {formato_arquivo}")
            
            print(f"✅ Conjunto de dados carregado com sucesso: {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            print(f"📊 Tipos de dados: {dict(self.df.dtypes)}")
            
            # Aplicar correção de tipos automaticamente
            self.df = self.corrigir_tipos_incorretos(self.df)
            print("🔧 Tipos de dados corrigidos automaticamente")
            
            return self.df
            
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo {caminho_arquivo}: {e}")
            # Tentar métodos alternativos de carregamento para JSON
            if formato_arquivo == 'json':
                try:
                    print("🔄 Tentando método alternativo de carregamento JSON...")
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    self.df = pd.json_normalize(dados)
                    print(f"✅ JSON carregado com sucesso com json_normalize: {self.df.shape}")
                    
                    # Aplicar correção de tipos também para JSON
                    self.df = self.corrigir_tipos_incorretos(self.df)
                    
                    return self.df
                except Exception as erro_json:
                    print(f"❌ Carregamento alternativo JSON também falhou: {erro_json}")
            return None

    def gerar_estatisticas_descritivas(self) -> str:
        """Gerar estatísticas descritivas abrangentes em formato Markdown"""
        if self.df is None:
            return "## ❌ Nenhum dado carregado\n\nPor favor, carregue um conjunto de dados primeiro."
            
        resumo_estatisticas = "# 📊 Relatório de Estatísticas Descritivas\n\n"
        
        # Visão Geral do Conjunto de Dados
        resumo_estatisticas += "## 📋 Visão Geral do Conjunto de Dados\n\n"
        resumo_estatisticas += f"- **Total de Linhas**: {self.df.shape[0]:,}\n"
        resumo_estatisticas += f"- **Total de Colunas**: {self.df.shape[1]}\n"
        resumo_estatisticas += f"- **Valores Ausentes**: {self.df.isnull().sum().sum()}\n"
        resumo_estatisticas += f"- **Linhas Duplicadas**: {self.df.duplicated().sum()}\n\n"
        
        # Resumo de Tipos de Dados
        resumo_estatisticas += "## 🔧 Resumo de Tipos de Dados\n\n"
        
        # Contar por categoria em vez de iterar através de tipos de dados individuais
        contagem_numericas = len(self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns)
        contagem_categoricas = len(self.df.select_dtypes(include=['object', 'category', 'string']).columns)
        contagem_booleanas = len(self.df.select_dtypes(include='bool').columns)
        contagem_data_hora = len(self.df.select_dtypes(include=['datetime64', 'timedelta64']).columns)
        
        if contagem_numericas > 0:
            resumo_estatisticas += f"- **Numéricas**: {contagem_numericas} colunas\n"
        if contagem_categoricas > 0:
            resumo_estatisticas += f"- **Categóricas**: {contagem_categoricas} colunas\n"
        if contagem_booleanas > 0:
            resumo_estatisticas += f"- **Verdadeiro/Falso**: {contagem_booleanas} colunas\n"
        if contagem_data_hora > 0:
            resumo_estatisticas += f"- **Data/Hora**: {contagem_data_hora} colunas\n"
        
        resumo_estatisticas += "\n"
        
        # Colunas numéricas
        colunas_numericas = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(colunas_numericas) > 0:
            resumo_estatisticas += "## 🔢 Colunas Numéricas\n\n"
            for col in colunas_numericas:
                resumo_estatisticas += f"### 📈 {col}\n\n"
                resumo_estatisticas += f"- **Média**: {self.df[col].mean():.2f}\n"
                resumo_estatisticas += f"- **Mediana**: {self.df[col].median():.2f}\n"
                resumo_estatisticas += f"- **Variância**: {self.df[col].var():.2f}\n"
                resumo_estatisticas += f"- **Desvio Padrão**: {self.df[col].std():.2f}\n"
                resumo_estatisticas += f"- **Mínimo**: {self.df[col].min():.2f}\n"
                resumo_estatisticas += f"- **Máximo**: {self.df[col].max():.2f}\n"
                resumo_estatisticas += f"- **Intervalo**: {self.df[col].max() - self.df[col].min():.2f}\n"
                resumo_estatisticas += f"- **Valores Ausentes**: {self.df[col].isnull().sum()}\n\n"
        
        # Colunas categóricas
        colunas_categoricas = self.df.select_dtypes(include=['object', 'category', 'string']).columns
        if len(colunas_categoricas) > 0:
            resumo_estatisticas += "## 📝 Colunas Categóricas\n\n"
            for col in colunas_categoricas:
                resumo_estatisticas += f"### 🏷️ {col}\n\n"
                resumo_estatisticas += f"- **Valores Únicos**: {self.df[col].nunique()}\n"
                resumo_estatisticas += f"- **Valores Ausentes**: {self.df[col].isnull().sum()}\n"
                resumo_estatisticas += f"- **3 Valores Principais**:\n"
                valores_principais = self.df[col].value_counts().head(3)
                for valor, contagem in valores_principais.items():
                    resumo_estatisticas += f"  - `{valor}`: {contagem} ocorrências\n"
                resumo_estatisticas += "\n"
        
        # Colunas booleanas
        colunas_booleanas = self.df.select_dtypes(include='bool').columns
        if len(colunas_booleanas) > 0:
            resumo_estatisticas += "## ✅ Colunas Verdadeiro/Falso\n\n"
            for col in colunas_booleanas:
                resumo_estatisticas += f"### 🔘 {col}\n\n"
                contagem_valores = self.df[col].value_counts()
                percentual = self.df[col].value_counts(normalize=True) * 100
                resumo_estatisticas += f"- **Distribuição**:\n"
                for val, contagem in contagem_valores.items():
                    resumo_estatisticas += f"  - `{val}`: {contagem} ({percentual[val]:.1f}%)\n"
                resumo_estatisticas += f"- **Variância**: {self.df[col].var():.2f}\n"
                resumo_estatisticas += f"- **Desvio Padrão**: {self.df[col].std():.2f}\n"
                resumo_estatisticas += f"- **Valores Ausentes**: {self.df[col].isnull().sum()}\n\n"
        
        return resumo_estatisticas
    
    def criar_prompt_analise(self, resumo_estatisticas: str) -> str:
        """Criar prompt detalhado para API com solicitação de formatação markdown"""
        if self.df is None:
            return "Nenhum dado disponível para análise"

        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_instrucoes_analise = os.path.join(diretorio_atual, "pt_instrucoes_analise.md")
        caminho_instrucoes_insights = os.path.join(diretorio_atual, "pt_instrucoes_retorno_insights.md")

        with open(caminho_instrucoes_analise, "r", encoding="utf-8") as f:
            bloco_de_instrucao_para_analise = f.read()

        with open(caminho_instrucoes_insights, "r", encoding="utf-8") as f:
            bloco_de_instrucao_retorno_insights = f.read()

        prompt = f"""
        UTILIZE O BLOCO DE INSTRUÇÃO ABAIXO PARA GERAR OS RESULTADOS:
        {bloco_de_instrucao_para_analise}

        VISÃO GERAL DO CONJUNTO DE Dados:
        - Formato: {self.df.shape}
        - Colunas: {list(self.df.columns)}
        - Tipos de dados: {dict(self.df.dtypes)}

        ESTATÍSTICAS DESCRITIVAS:
        {resumo_estatisticas}

        RETORNO ESPERADO DA ANÁLISE DO PROMPT ABAIXO:
        {bloco_de_instrucao_retorno_insights}
        """
        
        return prompt
    
    def gerar_visualizacoes(self) -> Dict[str, go.Figure]:
        """Gerar visualizações interativas para o conjunto de dados"""
        if self.df is None or self.df.empty:
            return {}
        
        visualizacoes = {}
        
        # Gráfico de pizza de tipos de dados
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
        
        # Gráfico de barras de dados ausentes
        dados_ausentes = self.df.isnull().sum()
        dados_ausentes = dados_ausentes[dados_ausentes > 0]
        if len(dados_ausentes) > 0:
            fig_ausentes = px.bar(
                x=dados_ausentes.values,
                y=dados_ausentes.index,
                orientation='h',
                title="Valores Ausentes por Coluna",
                color=dados_ausentes.values,
                color_continuous_scale='Viridis'
            )
            fig_ausentes.update_layout(height=400, xaxis_title="Contagem de Valores Ausentes", yaxis_title="Colunas")
            visualizacoes['dados_ausentes'] = fig_ausentes
        
        # Distribuições de colunas numéricas
        colunas_numericas = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(colunas_numericas) > 0:
            n_cols = min(3, len(colunas_numericas))
            n_linhas = (len(colunas_numericas) + n_cols - 1) // n_cols
            
            fig_dist = make_subplots(
                rows=n_linhas, cols=n_cols,
                subplot_titles=colunas_numericas[:n_linhas*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(colunas_numericas[:n_linhas*n_cols]):
                linha = i // n_cols + 1
                col_num = i % n_cols + 1
                
                fig_dist.add_trace(
                    go.Histogram(x=self.df[col], name=col, nbinsx=20),
                    row=linha, col=col_num
                )
            
            fig_dist.update_layout(height=300*n_linhas, title_text="Distribuições de Variáveis Numéricas", showlegend=False)
            visualizacoes['distribuicoes_numericas'] = fig_dist
        
        # Distribuições de colunas categóricas
        colunas_categoricas = self.df.select_dtypes(include=['object', 'category', 'string']).columns
        if len(colunas_categoricas) > 0:
            n_cols = min(3, len(colunas_categoricas))
            n_linhas = (len(colunas_categoricas) + n_cols - 1) // n_cols

            fig_dist_cat = make_subplots(
                rows=n_linhas, cols=n_cols,
                subplot_titles=colunas_categoricas[:n_linhas*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(colunas_categoricas[:n_linhas*n_cols]):
                linha = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # Para dados categóricos, usar gráfico de barras com contagem de valores
                contagem_valores = self.df[col].value_counts().head(10)  # Apenas 10 valores principais
                fig_dist_cat.add_trace(
                    go.Bar(x=contagem_valores.index, y=contagem_valores.values, name=col),
                    row=linha, col=col_num
                )
            
            fig_dist_cat.update_layout(height=300*n_linhas, title_text="Distribuições de Variáveis Categóricas", showlegend=False)
            visualizacoes['distribuicoes_categoricas'] = fig_dist_cat

        # Distribuições de colunas booleanas
        colunas_booleanas = self.df.select_dtypes(include='bool').columns
        if len(colunas_booleanas) > 0:
            n_cols = min(3, len(colunas_booleanas))
            n_linhas = (len(colunas_booleanas) + n_cols - 1) // n_cols

            fig_dist_bool = make_subplots(
                rows=n_linhas, cols=n_cols,
                subplot_titles=colunas_booleanas[:n_linhas*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15,
                specs=[[{"type": "pie"} for _ in range(n_cols)] for _ in range(n_linhas)]
            )
            
            for i, col in enumerate(colunas_booleanas[:n_linhas*n_cols]):
                linha = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # Para dados booleanos, usar gráfico de pizza
                contagem_valores = self.df[col].value_counts()
                fig_dist_bool.add_trace(
                    go.Pie(labels=[str(rotulo) for rotulo in contagem_valores.index], 
                          values=contagem_valores.values, name=col),
                    row=linha, col=col_num
                )
            
            fig_dist_bool.update_layout(height=300*n_linhas, title_text="Distribuições de Variáveis Booleanas", showlegend=False)
            visualizacoes['distribuicoes_booleanas'] = fig_dist_bool

        # Distribuições de colunas data/hora
        colunas_data_hora = self.df.select_dtypes(include=['datetime64']).columns
        if len(colunas_data_hora) > 0:
            n_cols = min(3, len(colunas_data_hora))
            n_linhas = (len(colunas_data_hora) + n_cols - 1) // n_cols

            fig_dist_data = make_subplots(
                rows=n_linhas, cols=n_cols,
                subplot_titles=colunas_data_hora[:n_linhas*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(colunas_data_hora[:n_linhas*n_cols]):
                linha = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # Para dados de data/hora, usar gráfico de linha com contagem de valores ao longo do tempo
                contagem_datas = self.df[col].value_counts().sort_index()
                fig_dist_data.add_trace(
                    go.Scatter(x=contagem_datas.index, y=contagem_datas.values, mode='lines', name=col),
                    row=linha, col=col_num
                )
            
            fig_dist_data.update_layout(height=300*n_linhas, title_text="Distribuições de Variáveis de Data/Hora", showlegend=False)
            visualizacoes['distribuicoes_data_hora'] = fig_dist_data

        return visualizacoes

    def gerar_matriz_correlacao(self, metodo: str = 'pearson') -> go.Figure:
        """Gerar matriz de correlação usando diferentes métodos"""
        if self.df is None or self.df.empty:
            return go.Figure()
        
        # Selecionar apenas colunas numéricas
        colunas_numericas = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        
        if len(colunas_numericas) < 2:
            # Criar figura vazia com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="⚠️ Número insuficiente de colunas numéricas para correlação",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Matriz de Correlação ({metodo.title()})",
                height=400
            )
            return fig
        
        # Calcular matriz de correlação baseada no método
        if metodo == 'pearson':
            matriz_corr = self.df[colunas_numericas].corr(method='pearson')
            titulo = "Matriz de Correlação (Pearson)"
        elif metodo == 'spearman':
            matriz_corr = self.df[colunas_numericas].corr(method='spearman')
            titulo = "Matriz de Correlação (Spearman)"
        elif metodo == 'kendall':
            matriz_corr = self.df[colunas_numericas].corr(method='kendall')
            titulo = "Matriz de Correlação (Kendall Tau)"
        else:
            matriz_corr = self.df[colunas_numericas].corr(method='pearson')
            titulo = "Matriz de Correlação (Pearson)"
        
        # Criar heatmap
        fig = px.imshow(
            matriz_corr,
            x=colunas_numericas,
            y=colunas_numericas,
            color_continuous_scale='RdBu_r',
            aspect="auto",
            title=titulo
        )
        
        # Adicionar anotações com valores
        for i, linha in enumerate(matriz_corr.index):
            for j, col in enumerate(matriz_corr.columns):
                fig.add_annotation(
                    x=j, y=i,
                    text=f"{matriz_corr.iloc[i, j]:.2f}",
                    showarrow=False,
                    font=dict(color="white" if abs(matriz_corr.iloc[i, j]) > 0.5 else "black", size=10)
                )
        
        fig.update_layout(height=600)
        return fig

    def calcular_cramers_v(self, col1: str, col2: str) -> float:
        """Calcular correlação de Cramér's V para variáveis categóricas"""
        try:
            # Criar tabela de contingência
            tabela_contingencia = pd.crosstab(self.df[col1], self.df[col2])
            
            # Calcular qui-quadrado
            chi2, p, dof, esperado = chi2_contingency(tabela_contingencia)
            
            # Calcular Cramér's V
            n = tabela_contingencia.sum().sum()
            min_dim = min(tabela_contingencia.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim))
            
            return cramers_v
        except:
            return np.nan

    def calcular_theils_u(self, col1: str, col2: str) -> float:
        """Calcular Theil's U (incerteza) para variáveis categóricas"""
        try:
            # Theil's U é assimétrico: U(x|y) != U(y|x)
            # Vamos calcular U(col1|col2)
            tabela_contingencia = pd.crosstab(self.df[col1], self.df[col2])
            
            # Calcular entropia condicional
            total = tabela_contingencia.sum().sum()
            entropia_condicional = 0
            
            for j in tabela_contingencia.columns:
                p_y = tabela_contingencia[j].sum() / total
                for i in tabela_contingencia.index:
                    p_xy = tabela_contingencia.loc[i, j] / total
                    if p_xy > 0 and p_y > 0:
                        entropia_condicional += p_xy * np.log(p_xy / p_y)
            
            entropia_condicional = -entropia_condicional
            
            # Calcular entropia de col1
            contagem_col1 = self.df[col1].value_counts()
            entropia_col1 = 0
            for count in contagem_col1:
                p = count / total
                entropia_col1 -= p * np.log(p)
            
            # Theil's U
            if entropia_col1 > 0:
                theils_u = 1 - (entropia_condicional / entropia_col1)
            else:
                theils_u = 0
                
            return theils_u
        except:
            return np.nan

    def calcular_phi(self, col1: str, col2: str) -> float:
        """Calcular coeficiente Phi para variáveis binárias"""
        try:
            # Verificar se ambas as colunas são binárias
            if self.df[col1].nunique() != 2 or self.df[col2].nunique() != 2:
                return np.nan
            
            tabela_contingencia = pd.crosstab(self.df[col1], self.df[col2])
            
            if tabela_contingencia.shape != (2, 2):
                return np.nan
            
            a, b = tabela_contingencia.iloc[0, 0], tabela_contingencia.iloc[0, 1]
            c, d = tabela_contingencia.iloc[1, 0], tabela_contingencia.iloc[1, 1]
            
            phi = (a * d - b * c) / np.sqrt((a + b) * (c + d) * (a + c) * (b + d))
            return phi
        except:
            return np.nan

    def calcular_correlation_ratio(self, col_categorica: str, col_numerica: str) -> float:
        """Calcular Correlation Ratio (eta) para relação categórica-numérica"""
        try:
            # Agrupar por categoria e calcular variância
            grupos = [grupo for _, grupo in self.df.groupby(col_categorica)[col_numerica]]
            
            if len(grupos) < 2:
                return 0
            
            # Variância entre grupos
            media_global = self.df[col_numerica].mean()
            variancia_entre = sum(len(grupo) * (grupo.mean() - media_global)**2 for grupo in grupos) / len(self.df)
            
            # Variância total
            variancia_total = self.df[col_numerica].var()
            
            if variancia_total > 0:
                eta = np.sqrt(variancia_entre / variancia_total)
            else:
                eta = 0
                
            return eta
        except:
            return np.nan

    def gerar_matriz_correlacao_avancada(self, metodo: str = 'pearson') -> tuple:
        """Gerar matriz de correlação usando diferentes métodos avançados"""
        if self.df is None or self.df.empty:
            return go.Figure(), pd.DataFrame()
        
        # Obter todas as colunas
        todas_colunas = self.df.columns.tolist()
        n_colunas = len(todas_colunas)
        
        if n_colunas < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="⚠️ Número insuficiente de colunas para análise de correlação",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Matriz de Correlação ({metodo.title()})",
                height=400
            )
            return fig, pd.DataFrame()
        
        # Inicializar matriz de correlação
        matriz_corr = pd.DataFrame(np.zeros((n_colunas, n_colunas)), 
                                 index=todas_colunas, columns=todas_colunas)
        
        # Preencher matriz baseada no método
        for i, col1 in enumerate(todas_colunas):
            for j, col2 in enumerate(todas_colunas):
                if i == j:
                    matriz_corr.iloc[i, j] = 1.0
                    continue
                
                # Determinar tipos das colunas
                tipo1 = self._obter_tipo_dado_simples(self.df[col1].dtype)
                tipo2 = self._obter_tipo_dado_simples(self.df[col2].dtype)
                
                # Calcular correlação baseada nos tipos e método
                if metodo == 'pearson':
                    if tipo1 == "Numérica" and tipo2 == "Numérica":
                        corr = self.df[col1].corr(self.df[col2], method='pearson')
                    else:
                        corr = np.nan
                
                elif metodo == 'spearman':
                    if tipo1 == "Numérica" and tipo2 == "Numérica":
                        corr = self.df[col1].corr(self.df[col2], method='spearman')
                    else:
                        # Spearman pode lidar com ordinais, mas vamos manter simples por enquanto
                        corr = np.nan
                
                elif metodo == 'kendall':
                    if tipo1 == "Numérica" and tipo2 == "Numérica":
                        corr = self.df[col1].corr(self.df[col2], method='kendall')
                    else:
                        corr = np.nan
                
                elif metodo == 'cramers_v':
                    if tipo1 == "Categórica" and tipo2 == "Categórica":
                        corr = self.calcular_cramers_v(col1, col2)
                    else:
                        corr = np.nan
                
                elif metodo == 'theils_u':
                    if tipo1 == "Categórica" and tipo2 == "Categórica":
                        corr = self.calcular_theils_u(col1, col2)
                    else:
                        corr = np.nan
                
                elif metodo == 'phi':
                    if (tipo1 == "Verdadeiro/Falso" or self.df[col1].nunique() == 2) and \
                       (tipo2 == "Verdadeiro/Falso" or self.df[col2].nunique() == 2):
                        corr = self.calcular_phi(col1, col2)
                    else:
                        corr = np.nan
                
                elif metodo == 'correlation_ratio':
                    if (tipo1 == "Categórica" and tipo2 == "Numérica"):
                        corr = self.calcular_correlation_ratio(col1, col2)
                    elif (tipo2 == "Categórica" and tipo1 == "Numérica"):
                        corr = self.calcular_correlation_ratio(col2, col1)
                    else:
                        corr = np.nan
                
                else:
                    corr = np.nan
                
                matriz_corr.iloc[i, j] = corr
        
        # Criar heatmap
        fig = px.imshow(
            matriz_corr,
            x=todas_colunas,
            y=todas_colunas,
            color_continuous_scale='RdBu_r',
            aspect="auto",
            title=f"Matriz de Correlação ({metodo.replace('_', ' ').title()})",
            zmin=-1, zmax=1
        )
        
        # Adicionar anotações com valores
        for i, linha in enumerate(matriz_corr.index):
            for j, col in enumerate(matriz_corr.columns):
                valor = matriz_corr.iloc[i, j]
                if not np.isnan(valor):
                    fig.add_annotation(
                        x=j, y=i,
                        text=f"{valor:.2f}",
                        showarrow=False,
                        font=dict(color="white" if abs(valor) > 0.5 else "black", size=8)
                    )
        
        fig.update_layout(height=600)
        return fig, matriz_corr

    def analisar_dados_com_ia(self, pergunta_usuario: str = "") -> str:
        """Analisar dados usando IA via OpenRouter"""
        if self.df is None:
            return "❌ Nenhum dado carregado. Por favor, carregue um conjunto de dados primeiro."
        
        try:
            # Gerar estatísticas descritivas
            estatisticas = self.gerar_estatisticas_descritivas()
            
            # Criar prompt para IA
            prompt = self.criar_prompt_analise(estatisticas)
            
            if pergunta_usuario:
                prompt += f"\n\nPERGUNTA ESPECÍFICA DO USUÁRIO: {pergunta_usuario}"
            
            # Preparar dados para envio
            dados_mensagem = {
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            print("🚀 Enviando solicitação para API OpenRouter...")
            
            # Fazer requisição para API
            resposta = requests.post(self.url_base, headers=self.cabecalhos, json=dados_mensagem, timeout=120)
            
            if resposta.status_code == 200:
                dados_resposta = resposta.json()
                conteudo = dados_resposta['choices'][0]['message']['content']
                print("✅ Resposta recebida com sucesso da API")
                return conteudo
            else:
                erro_msg = f"❌ Erro na API: {resposta.status_code} - {resposta.text}"
                print(erro_msg)
                return erro_msg
                
        except requests.exceptions.Timeout:
            erro_msg = "❌ Timeout: A requisição demorou muito para ser processada."
            print(erro_msg)
            return erro_msg
        except Exception as e:
            erro_msg = f"❌ Erro inesperado: {str(e)}"
            print(erro_msg)
            return erro_msg

# Função auxiliar para uso em scripts não-Streamlit
def criar_analisador():
    """Função factory para criar instância do analisador"""
    return AnalisadorChatBot()