# pt_01_analisador.py
import pandas as pd
import requests
import json
import os
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, Optional, List

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
                resumo_estatisticas += f"- **Valores Ausentes**: {self.df[col].isnull().sum()}\n"
                resumo_estatisticas += f"- **Percentil 05**: {self.df[col].quantile(0.05):.2f}\n"
                resumo_estatisticas += f"- **Percentil 25**: {self.df[col].quantile(0.25):.2f}\n"
                resumo_estatisticas += f"- **Percentil 75**: {self.df[col].quantile(0.75):.2f}\n"
                resumo_estatisticas += f"- **Percentil 95**: {self.df[col].quantile(0.95):.2f}\n"
                resumo_estatisticas += f"- **IQR**: {self.df[col].quantile(0.75) - self.df[col].quantile(0.25):.2f}\n"
                resumo_estatisticas += f"- **Coeficiente de Variação**: {self.df[col].std() / self.df[col].mean() * 100 if self.df[col].mean() != 0 else 0:.2f}%\n"
                resumo_estatisticas += f"- **Curtose**: {self.df[col].kurt():.2f}\n"
                resumo_estatisticas += f"- **Assimetria**: {self.df[col].skew():.2f}\n\n"
        
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
    
    def criar_prompt_analise(self, resumo_estatisticas: str, contexto_usuario: str = "") -> str:
        """Criar prompt detalhado para API - VERSÃO OTIMIZADA"""
        if self.df is None:
            return "Nenhum dado disponível para análise"

        # ✅ CARREGAR INSTRUÇÕES DE FORMA MAIS EFICIENTE
        try:
            diretorio_atual = os.path.dirname(os.path.abspath(__file__))
            
            # Ler apenas as instruções essenciais
            caminho_instrucoes_analise = os.path.join(diretorio_atual, "pt_instrucoes_analise.md")
            with open(caminho_instrucoes_analise, "r", encoding="utf-8") as f:
                bloco_de_instrucao_para_analise = f.read()
            
            # Incluir instruções de retorno apenas se necessário
            caminho_instrucoes_insights = os.path.join(diretorio_atual, "pt_instrucoes_retorno_insights.md")
            with open(caminho_instrucoes_insights, "r", encoding="utf-8") as f:
                bloco_de_instrucao_retorno_insights = f.read()
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar instruções: {e}")
            # Usar instruções padrão em caso de erro
            bloco_de_instrucao_para_analise = "Analise os dados fornecidos de forma detalhada e profissional."
            bloco_de_instrucao_retorno_insights = "Forneça insights acionáveis e recomendações baseadas nos dados."

        # ✅ RESUMIR CONTEXTO DO USUÁRIO
        if not contexto_usuario.strip():
            input_de_contexto_usuario = "Nenhum contexto adicional fornecido pelo usuário."
        else:
            input_de_contexto_usuario = contexto_usuario[:500]  # Limitar a 500 caracteres

        # ✅ COMPACTAR INFORMAÇÕES DO DATAFRAME
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
        
        # ✅ LIMITAR TAMANHO DO PROMPT
        if len(prompt) > 12000:
            print("⚠️ Prompt muito longo, compactando...")
            # Manter estatísticas mas reduzir detalhes excessivos
            prompt = prompt[:12000] + "\n\n[Continuação cortada por limite de tamanho]"
        
        return prompt

    def analisar_conjunto_dados(self, contexto_usuario: str = "") -> Dict[str, Any]:
        """Analisar o conjunto de dados atualmente carregado - VERSÃO OTIMIZADA"""
        if self.df is None:
            return None
        
        print("🚀 Iniciando Análise de Dados...")
        inicio_tempo = time.time()
        
        # ✅ PRIMEIRO: Gerar estatísticas descritivas (necessárias para o prompt)
        print("📈 Gerando estatísticas descritivas...")
        resumo_estatisticas = self.gerar_estatisticas_descritivas()
        
        # ✅ SEGUNDO: Criar prompt e chamar API IMEDIATAMENTE
        print("🤖 Chamando API para análise detalhada...")
        prompt = self.criar_prompt_analise(resumo_estatisticas, contexto_usuario)
        resultado_analise = self.chamar_api_open_router(prompt)
        
        # ✅ TERCEIRO: Gerar visualizações ENQUANTO espera pela IA
        print("🎨 Criando visualizações em paralelo...")
        visualizacoes = self.gerar_visualizacoes()
        
        tempo_decorrido = time.time() - inicio_tempo
        
        if resultado_analise:
            resultados = {
                'dataframe': self.df,
                'estatisticas': resumo_estatisticas,
                'analise_ia': resultado_analise,
                'visualizacoes': visualizacoes,
                'tempo_analise': tempo_decorrido
            }
            
            print(f"✅ Análise concluída em {tempo_decorrido:.2f} segundos")
            return resultados
        else:
            print(f"❌ Falha ao obter análise da API (tempo: {tempo_decorrido:.2f}s)")
        return None

    def gerar_visualizacoes(self) -> Dict[str, go.Figure]:
        """Gerar visualizações interativas para o conjunto de dados - VERSÃO OTIMIZADA"""
        if self.df is None or self.df.empty:
            return {}
        
        visualizacoes = {}
        
        # ✅ USAR AMOSTRA PARA DATASETS GRANDES
        amostra_df = self.df
        if len(self.df) > 1000:
            amostra_df = self.df.sample(1000, random_state=42)
            print("📊 Usando amostra de 1000 registros para visualizações")
        
        # ✅ LIMITAR NÚMERO DE COLUNAS POR GRÁFICO
        max_colunas_por_grafico = 10
        
        try:
            # Gráfico de pizza de tipos de dados (mantido, mas mais rápido)
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
            
            # ✅ GRÁFICO DE DADOS AUSENTES OTIMIZADO
            dados_ausentes = self.df.isnull().sum()
            dados_ausentes = dados_ausentes[dados_ausentes > 0]
            if len(dados_ausentes) > 0:
                # Limitar a 15 colunas para não sobrecarregar
                dados_ausentes = dados_ausentes.head(15)
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
            
            # ✅ DISTRIBUIÇÕES NUMÉRICAS OTIMIZADAS
            colunas_numericas = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
            if len(colunas_numericas) > 0:
                # Limitar a 6 colunas para performance
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
                visualizacoes['distribuicoes_numericas'] = fig_dist
            
            # ✅ DISTRIBUIÇÕES CATEGÓRICAS OTIMIZADAS
            colunas_categoricas = self.df.select_dtypes(include=['object', 'category', 'string']).columns
            if len(colunas_categoricas) > 0:
                # Limitar a 6 colunas
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
                    
                    # Para dados categóricos, usar amostra e limitar categorias
                    contagem_valores = amostra_df[col].value_counts().head(8)  # Apenas 8 valores principais
                    fig_dist_cat.add_trace(
                        go.Bar(x=contagem_valores.index, y=contagem_valores.values, name=col),
                        row=linha, col=col_num
                    )
                    # Rotacionar labels para melhor visualização
                    fig_dist_cat.update_xaxes(tickangle=45, row=linha, col=col_num)
                
                fig_dist_cat.update_layout(height=300*n_linhas, title_text="Distribuições de Variáveis Categóricas (Amostra)", showlegend=False)
                visualizacoes['distribuicoes_categoricas'] = fig_dist_cat

            # ✅ MAPA DE CALOR DE CORRELAÇÃO OTIMIZADO
            colunas_numericas_corr = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
            if len(colunas_numericas_corr) > 1:
                # Usar amostra para correlação
                matriz_corr = amostra_df[colunas_numericas_corr].corr()
                fig_corr = px.imshow(
                    matriz_corr,
                    title="Mapa de Calor de Correlação (Amostra)",
                    color_continuous_scale='RdBu_r',
                    aspect="auto"
                )
                fig_corr.update_layout(height=500)
                visualizacoes['mapa_calor_correlacao'] = fig_corr
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar visualizações: {e}")
            # Continuar mesmo com erro em uma visualização
        
        return visualizacoes
         
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
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta: {e.response.text}")
            return None
  
    def analisar_arquivo(self, caminho_arquivo: str, nome_planilha: str = None, salvar_saida: bool = False, diretorio_saida: str = None) -> Dict[str, Any]:
        """Método principal para analisar arquivo de dados (CSV, Excel, JSON)"""
        
        print("🚀 Iniciando Análise de Dados...")
        
        # Carregar dados
        df = self.carregar_e_previsualizar_dados(caminho_arquivo, nome_planilha)
        if df is None:
            return None
        
        # Gerar estatísticas descritivas
        print("📈 Gerando estatísticas descritivas...")
        resumo_estatisticas = self.gerar_estatisticas_descritivas()
        
        # Gerar visualizações
        print("🎨 Criando visualizações...")
        visualizacoes = self.gerar_visualizacoes()
        
        # Criar prompt de análise
        prompt = self.criar_prompt_analise(resumo_estatisticas)
        
        # Chamar API
        print("🤖 Chamando API para análise detalhada...")
        resultado_analise = self.chamar_api_open_router(prompt)
        
        if resultado_analise:
            resultados = {
                'dataframe': df,
                'estatisticas': resumo_estatisticas,
                'analise_ia': resultado_analise,
                'visualizacoes': visualizacoes
            }
            
            # Salvar resultados se solicitado
            if salvar_saida:
                self.salvar_resultados(resultados, caminho_arquivo, diretorio_saida)
            
            return resultados
        else:
            print("❌ Falha ao obter análise da API")
            return None
    
    def salvar_resultados(self, resultados: Dict[str, Any], caminho_arquivo_original: str, diretorio_saida: str = None):
        """Salvar resultados da análise em arquivos TXT"""
        nome_base = os.path.splitext(os.path.basename(caminho_arquivo_original))[0]
        
        if diretorio_saida:
            os.makedirs(diretorio_saida, exist_ok=True)
            caminho_base = os.path.join(diretorio_saida, nome_base)
        else:
            caminho_base = nome_base
        
        # Salvar estatísticas como markdown
        with open(f"{caminho_base}_estatisticas.txt", "w", encoding="utf-8") as f:
            f.write(resultados['estatisticas'])
        
        # Salvar análise IA como markdown
        with open(f"{caminho_base}_analise_ia.txt", "w", encoding="utf-8") as f:
            f.write(resultados['analise_ia'])
        
        # Salvar relatório combinado como markdown
        relatorio_combinado = f"""# 📊 Relatório de Análise de Dados

        ## Conjunto de Dados: {nome_base}

        ## Estatísticas Descritivas

        {resultados['estatisticas']}

        ## Análise

        {resultados['analise_ia']}

        ---
        *Relatório gerado automaticamente com Analisador de Dados IA*
        """
        with open(f"{caminho_base}_relatorio_completo.txt", "w", encoding="utf-8") as f:
            f.write(relatorio_combinado)
        
        print(f"💾 Resultados salvos como arquivos Markdown:")
        print(f"   - {caminho_base}_estatisticas.txt")
        print(f"   - {caminho_base}_analise_ia.txt")
        print(f"   - {caminho_base}_relatorio_completo.txt")