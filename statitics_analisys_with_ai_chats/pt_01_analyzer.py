# en_01_analyzer.py
import pandas as pd
import requests
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, Optional, List

# Importar streamlit no nível superior, mas lidar com o caso quando não estiver disponível
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

class ChatBotAnalyzer:
    def __init__(self, api_key: str = None):
        # Prioridade: chave fornecida > Segredos do Streamlit > variável de ambiente > arquivo
        if api_key is None:
            self.api_key = self.get_api_key_secure()
        else:
            self.api_key = api_key
        
        if not self.api_key:
            raise ValueError("Chave da API não encontrada. Por favor, defina a variável de ambiente OPENROUTER_API_KEY ou crie o arquivo 'api_key.txt'.")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://data-analyzer-pr.streamlit.app",
            "X-Title": "Analisador de Dados"
        }
        self.df = None

    def get_api_key_secure(self) -> Optional[str]:
        """
        Obter chave da API com segurança com prioridade:
        1. Segredos do Streamlit (se em ambiente Streamlit)
        2. Variável de Ambiente
        3. Arquivo local (apenas para desenvolvimento)
        """
        print(f"🔍 Iniciando busca pela chave da API...")
        print(f"🔍 STREAMLIT_AVAILABLE: {STREAMLIT_AVAILABLE}")
        
        # 1. Tentar Segredos do Streamlit
        if STREAMLIT_AVAILABLE:
            try:
                print("🔍 Verificando segredos do Streamlit...")
                if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
                    api_key = st.secrets['OPENROUTER_API_KEY']
                    print(f"🔍 Chave encontrada nos segredos, comprimento: {len(api_key) if api_key else 0}")
                    if api_key and api_key.strip():
                        print("✅ Chave da API carregada dos Segredos do Streamlit")
                        return api_key.strip()
                else:
                    print("❌ OPENROUTER_API_KEY não encontrada nos segredos do Streamlit")
            except Exception as e:
                print(f"⚠️ Segredos do Streamlit não acessíveis: {e}")
        
        # 2. Tentar Variável de Ambiente
        env_key = os.getenv('OPENROUTER_API_KEY')
        print(f"🔍 Verificação da variável de ambiente: {'Encontrada' if env_key else 'Não encontrada'}")
        if env_key and env_key.strip():
            print("✅ Chave da API carregada da variável de ambiente")
            return env_key.strip()
        
        # 3. Tentar arquivo local (apenas para desenvolvimento)
        file_key = self.read_api_key_from_file()
        print(f"🔍 Verificação de arquivo: {'Encontrada' if file_key else 'Não encontrada'}")
        if file_key:
            print("✅ Chave da API carregada do arquivo local")
            return file_key
        
        print("❌ Nenhuma chave da API encontrada em nenhuma fonte")
        return None

    def read_api_key_from_file(self, file_path: str = None) -> Optional[str]:
        """
        Ler chave da API do arquivo local (apenas para desenvolvimento)
        """
        try:
            if file_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, "api_key.txt")
            
            print(f"🔍 Procurando arquivo de chave da API em: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ Arquivo de chave da API não encontrado: {file_path}")
                # Tentar locais alternativos
                alternative_paths = [
                    "api_key.txt",
                    "./api_key.txt", 
                    "../api_key.txt",
                ]
                
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        file_path = alt_path
                        print(f"✅ Arquivo de chave da API encontrado em: {file_path}")
                        break
                else:
                    print("❌ Arquivo de chave da API não encontrado em locais comuns")
                    return None
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                print(f"📄 Comprimento do conteúdo do arquivo de chave da API: {len(content)} caracteres")
                
                # Lidar com diferentes formatos possíveis
                if content.startswith('open_router:'):
                    key = content.split('open_router:')[1].strip()
                elif ':' in content:
                    key = content.split(':', 1)[1].strip()
                else:
                    key = content.strip()
                
                if key:
                    print(f"✅ Chave da API carregada com sucesso (primeiros 5 caracteres): {key[:5]}...")
                    return key
                else:
                    print("❌ Nenhuma chave da API encontrada no arquivo")
                    return None
                    
        except Exception as e:
            print(f"❌ Erro ao ler arquivo de chave da API: {e}")
            return None

    def get_simple_column_types(self) -> Dict[str, List[str]]:
        """Obter tipos de coluna simplificados agrupados por categoria"""
        if self.df is None:
            return {}
        
        numerical_cols = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        boolean_cols = self.df.select_dtypes(include='bool').columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64', 'timedelta64']).columns.tolist()
        
        return {
            'Numéricas': numerical_cols,
            'Categóricas': categorical_cols,
            'Verdadeiro/Falso': boolean_cols,
            'Data/Hora': datetime_cols
        }

    def get_detailed_column_info(self) -> pd.DataFrame:
        """Obter informações detalhadas sobre cada coluna"""
        if self.df is None:
            return pd.DataFrame()
        
        column_info = []
        
        for col in self.df.columns:
            col_type = self._get_simple_dtype(self.df[col].dtype)
            non_null_count = self.df[col].count()
            null_count = self.df[col].isnull().sum()
            null_percentage = (null_count / len(self.df)) * 100
            
            column_info.append({
                'Nome da Coluna': col,
                'Tipo': col_type,
                'Contagem Não Nula': non_null_count,
                'Contagem Nula': null_count,
                'Porcentagem Nula': f"{null_percentage:.2f}%"
            })
        
        return pd.DataFrame(column_info)

    def _get_simple_dtype(self, dtype):
        """Converter dtype detalhado para categoria simplificada"""
        if np.issubdtype(dtype, np.number):
            return "Numérica"
        elif np.issubdtype(dtype, np.bool_):
            return "Verdadeiro/Falso"
        elif np.issubdtype(dtype, np.datetime64):
            return "Data/Hora"
        else:
            return "Categórica"

    def load_and_preview_data(self, file_path: str) -> pd.DataFrame:
        """Carregar arquivo CSV e retornar informações básicas"""
        try:
            self.df = pd.read_csv(file_path)
            print(f"✅ Conjunto de dados carregado com sucesso: {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")
            return self.df
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
            return None
    
    def generate_descriptive_stats(self) -> str:
        """Gerar estatísticas descritivas abrangentes em formato Markdown"""
        if self.df is None:
            return "## ❌ Nenhum dado carregado\n\nPor favor, carregue um conjunto de dados primeiro."
            
        stats_summary = "# 📊 Relatório de Estatísticas Descritivas\n\n"
        
        # Visão Geral do Conjunto de Dados
        stats_summary += "## 📋 Visão Geral do Conjunto de Dados\n\n"
        stats_summary += f"- **Total de Linhas**: {self.df.shape[0]:,}\n"
        stats_summary += f"- **Total de Colunas**: {self.df.shape[1]}\n"
        stats_summary += f"- **Valores Faltantes**: {self.df.isnull().sum().sum()}\n"
        stats_summary += f"- **Linhas Duplicadas**: {self.df.duplicated().sum()}\n\n"
        
        # Resumo de Tipos de Dados
        stats_summary += "## 🔧 Resumo de Tipos de Dados\n\n"
        
        # Contar por categoria em vez de iterar através de dtypes individuais
        numerical_count = len(self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns)
        categorical_count = len(self.df.select_dtypes(include=['object', 'category', 'string']).columns)
        boolean_count = len(self.df.select_dtypes(include='bool').columns)
        datetime_count = len(self.df.select_dtypes(include=['datetime64', 'timedelta64']).columns)
        
        if numerical_count > 0:
            stats_summary += f"- **Numéricas**: {numerical_count} colunas\n"
        if categorical_count > 0:
            stats_summary += f"- **Categóricas**: {categorical_count} colunas\n"
        if boolean_count > 0:
            stats_summary += f"- **Verdadeiro/Falso**: {boolean_count} colunas\n"
        if datetime_count > 0:
            stats_summary += f"- **Data/Hora**: {datetime_count} colunas\n"
        
        stats_summary += "\n"
        
        # Colunas numéricas
        numerical_cols = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(numerical_cols) > 0:
            stats_summary += "## 🔢 Colunas Numéricas\n\n"
            for col in numerical_cols:
                stats_summary += f"### 📈 {col}\n\n"
                stats_summary += f"- **Média**: {self.df[col].mean():.2f}\n"
                stats_summary += f"- **Mediana**: {self.df[col].median():.2f}\n"
                stats_summary += f"- **Variância**: {self.df[col].var():.2f}\n"
                stats_summary += f"- **Desvio Padrão**: {self.df[col].std():.2f}\n"
                stats_summary += f"- **Mínimo**: {self.df[col].min():.2f}\n"
                stats_summary += f"- **Máximo**: {self.df[col].max():.2f}\n"
                stats_summary += f"- **Amplitude**: {self.df[col].max() - self.df[col].min():.2f}\n"
                stats_summary += f"- **Valores Faltantes**: {self.df[col].isnull().sum()}\n\n"
        
        # Colunas categóricas
        categorical_cols = self.df.select_dtypes(include=['object', 'category', 'string']).columns
        if len(categorical_cols) > 0:
            stats_summary += "## 📝 Colunas Categóricas\n\n"
            for col in categorical_cols:
                stats_summary += f"### 🏷️ {col}\n\n"
                stats_summary += f"- **Valores Únicos**: {self.df[col].nunique()}\n"
                stats_summary += f"- **Valores Faltantes**: {self.df[col].isnull().sum()}\n"
                stats_summary += f"- **Top 3 Valores**:\n"
                top_values = self.df[col].value_counts().head(3)
                for value, count in top_values.items():
                    stats_summary += f"  - `{value}`: {count} ocorrências\n"
                stats_summary += "\n"
        
        # Colunas booleanas
        boolean_cols = self.df.select_dtypes(include='bool').columns
        if len(boolean_cols) > 0:
            stats_summary += "## ✅ Colunas Verdadeiro/Falso\n\n"
            for col in boolean_cols:
                stats_summary += f"### 🔘 {col}\n\n"
                value_counts = self.df[col].value_counts()
                percentage = self.df[col].value_counts(normalize=True) * 100
                stats_summary += f"- **Distribuição**:\n"
                for val, count in value_counts.items():
                    stats_summary += f"  - `{val}`: {count} ({percentage[val]:.1f}%)\n"
                stats_summary += f"- **Variância**: {self.df[col].var():.2f}\n"
                stats_summary += f"- **Desvio Padrão**: {self.df[col].std():.2f}\n"
                stats_summary += f"- **Valores Faltantes**: {self.df[col].isnull().sum()}\n\n"
        
        return stats_summary
    
    def create_analysis_prompt(self, stats_summary: str) -> str:
        """Criar prompt detalhado para API com solicitação de formatação markdown"""
        if self.df is None:
            return "Nenhum dado disponível para análise"
            
        prompt = f"""
        Você é um analista de dados especialista. Por favor, analise o seguinte conjunto de dados e forneça um relatório abrangente de estatísticas descritivas com interpretação textual elaborada.

        VISÃO GERAL DO CONJUNTO DE DADOS:
        - Formato: {self.df.shape}
        - Colunas: {list(self.df.columns)}
        - Tipos de dados: {dict(self.df.dtypes)}

        ESTATÍSTICAS DESCRITIVAS:
        {stats_summary}

        Por favor, forneça uma análise detalhada em formato MARKDOWN incluindo:

        # Resumo Executivo
        Visão geral breve dos principais achados e avaliação da qualidade dos dados.

        ## Análise Estatística Detalhada
        Interpretação das medidas e análise de distribuição.

        ## Identificação de Padrões
        Tendências, valores atípicos e padrões interessantes.

        ## Implicações para Negócios/Pesquisa
        O que os dados revelam e significância prática.

        ## Recomendações
        Próximos passos sugeridos e melhorias.

        Use formatação markdown adequada com cabeçalhos, pontos de lista e ênfase. Seja profissional e perspicaz.
        """
        
        return prompt
    
    def generate_visualizations(self) -> Dict[str, go.Figure]:
        """Gerar visualizações interativas para o conjunto de dados"""
        if self.df is None:
            return {}
        
        visualizations = {}
        
        # Gráfico de pizza de tipos de dados - Corrigido com categorização adequada de dtype
        def categorize_dtype(dtype):
            if np.issubdtype(dtype, np.number):
                return "Numérica"
            elif np.issubdtype(dtype, np.bool_):
                return "Booleana"
            elif np.issubdtype(dtype, np.datetime64):
                return "Data/Hora"
            else:
                return "Categórica"
        
        dtype_counts = self.df.dtypes.apply(categorize_dtype).value_counts()
        
        if len(dtype_counts) > 0:
            fig_dtypes = px.pie(
                values=dtype_counts.values,
                names=dtype_counts.index,
                title="Distribuição de Tipos de Dados",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_dtypes.update_traces(textposition='inside', textinfo='percent+label')
            fig_dtypes.update_layout(height=400, showlegend=False)
            visualizations['tipos_dados'] = fig_dtypes
        
        # Gráfico de barras de dados faltantes
        missing_data = self.df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if len(missing_data) > 0:
            fig_missing = px.bar(
                x=missing_data.values,
                y=missing_data.index,
                orientation='h',
                title="Valores Faltantes por Coluna",
                color=missing_data.values,
                color_continuous_scale='Viridis'
            )
            fig_missing.update_layout(height=400, xaxis_title="Contagem de Valores Faltantes", yaxis_title="Colunas")
            visualizations['dados_faltantes'] = fig_missing
        
        # Distribuições de colunas numéricas
        numerical_cols = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(numerical_cols) > 0:
            n_cols = min(3, len(numerical_cols))
            n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
            
            fig_dist = make_subplots(
                rows=n_rows, cols=n_cols,
                subplot_titles=numerical_cols[:n_rows*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(numerical_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                fig_dist.add_trace(
                    go.Histogram(x=self.df[col], name=col, nbinsx=20),
                    row=row, col=col_num
                )
            
            fig_dist.update_layout(height=300*n_rows, title_text="Distribuições de Variáveis Numéricas", showlegend=False)
            visualizations['distribuicoes_numericas'] = fig_dist
        
        # Distribuições de colunas categóricas - CORRIGIDO
        categorical_cols = self.df.select_dtypes(include=['object', 'category', 'string']).columns
        if len(categorical_cols) > 0:
            n_cols = min(3, len(categorical_cols))
            n_rows = (len(categorical_cols) + n_cols - 1) // n_cols

            fig_cat_dist = make_subplots(  # Nome da variável alterado para evitar conflito
                rows=n_rows, cols=n_cols,
                subplot_titles=categorical_cols[:n_rows*n_cols],  # Corrigido: usar categorical_cols
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(categorical_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # Para dados categóricos, usar gráfico de barras com contagem de valores
                value_counts = self.df[col].value_counts().head(10)  # Apenas os 10 principais valores
                fig_cat_dist.add_trace(
                    go.Bar(x=value_counts.index, y=value_counts.values, name=col),  # Corrigido: go.Bar não go.bar
                    row=row, col=col_num
                )
            
            fig_cat_dist.update_layout(height=300*n_rows, title_text="Distribuições de Variáveis Categóricas", showlegend=False)
            visualizations['distribuicoes_categoricas'] = fig_cat_dist

        # Distribuições de colunas booleanas - CORRIGIDO
        boolean_cols = self.df.select_dtypes(include='bool').columns
        if len(boolean_cols) > 0:
            n_cols = min(3, len(boolean_cols))
            n_rows = (len(boolean_cols) + n_cols - 1) // n_cols

            fig_bool_dist = make_subplots(  # Nome da variável alterado
                rows=n_rows, cols=n_cols,
                subplot_titles=boolean_cols[:n_rows*n_cols],  # Corrigido: usar boolean_cols
                horizontal_spacing=0.1,
                vertical_spacing=0.15,
                specs=[[{"type": "pie"} for _ in range(n_cols)] for _ in range(n_rows)]  # Especificar tipo de gráfico de pizza
            )
            
            for i, col in enumerate(boolean_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # Para dados booleanos, usar gráfico de pizza
                value_counts = self.df[col].value_counts()
                fig_bool_dist.add_trace(
                    go.Pie(labels=[str(label) for label in value_counts.index], 
                        values=value_counts.values, name=col),  # Corrigido: go.Pie não go.pie
                    row=row, col=col_num
                )
            
            fig_bool_dist.update_layout(height=300*n_rows, title_text="Distribuições de Variáveis Booleanas", showlegend=False)
            visualizations['distribuicoes_booleanas'] = fig_bool_dist

        # Distribuições de colunas de data/hora - CORRIGIDO
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns  # Removido timedelta64 para simplicidade
        if len(datetime_cols) > 0:
            n_cols = min(3, len(datetime_cols))
            n_rows = (len(datetime_cols) + n_cols - 1) // n_cols

            fig_date_dist = make_subplots(  # Nome da variável alterado
                rows=n_rows, cols=n_cols,
                subplot_titles=datetime_cols[:n_rows*n_cols],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            for i, col in enumerate(datetime_cols[:n_rows*n_cols]):
                row = i // n_cols + 1
                col_num = i % n_cols + 1
                
                # Para dados de data/hora, usar gráfico de linha com contagem de valores ao longo do tempo
                date_counts = self.df[col].value_counts().sort_index()
                fig_date_dist.add_trace(
                    go.Scatter(x=date_counts.index, y=date_counts.values, mode='lines', name=col),  # Corrigido: go.Scatter para gráfico de linha
                    row=row, col=col_num
                )
            
            fig_date_dist.update_layout(height=300*n_rows, title_text="Distribuições de Variáveis de Data/Hora", showlegend=False)  # Título corrigido
            visualizations['distribuicoes_data_hora'] = fig_date_dist  # Nome da chave corrigido

        # Mapa de calor de correlação apenas para dados numéricos - CORRIGIDO
        numerical_cols_for_corr = self.df.select_dtypes(include=['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16']).columns
        if len(numerical_cols_for_corr) > 1:
            corr_matrix = self.df[numerical_cols_for_corr].corr()
            fig_corr = px.imshow(
                corr_matrix,
                title="Mapa de Calor de Correlação (Variáveis Numéricas)",
                color_continuous_scale='RdBu_r',
                aspect="auto"
            )
            fig_corr.update_layout(height=500)
            visualizations['mapa_calor_correlacao'] = fig_corr
        
        return visualizations
         
    def call_open_router_api(self, prompt: str) -> Optional[str]:
        """Fazer chamada à API do Open Router"""
        payload = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um analista de dados especialista com forte conhecimento estatístico. Forneça análises detalhadas e precisas com interpretações práticas. Formate sua resposta em markdown bonito com cabeçalhos adequados, pontos de lista e ênfase. Seja completo e profissional."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 4000,
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro da API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta: {e.response.text}")
            return None
    
    def analyze_csv(self, file_path: str, save_output: bool = False, output_dir: str = None) -> Dict[str, Any]:
        """Método principal para analisar arquivo CSV"""
        
        print("🚀 Iniciando Análise CSV...")
        
        # Carregar dados
        df = self.load_and_preview_data(file_path)
        if df is None:
            return None
        
        # Gerar estatísticas descritivas
        print("📈 Gerando estatísticas descritivas...")
        stats_summary = self.generate_descriptive_stats()
        
        # Gerar visualizações
        print("🎨 Criando visualizações...")
        visualizations = self.generate_visualizations()
        
        # Criar prompt de análise
        prompt = self.create_analysis_prompt(stats_summary)
        
        # Chamar API
        print("🤖 Chamando API para análise detalhada...")
        analysis_result = self.call_open_router_api(prompt)
        
        if analysis_result:
            results = {
                'dataframe': df,
                'statistics': stats_summary,
                'ai_analysis': analysis_result,
                'visualizations': visualizations
            }
            
            # Salvar resultados se solicitado
            if save_output:
                self.save_results(results, file_path, output_dir)
            
            return results
        else:
            print("❌ Falha ao obter análise da API")
            return None
    
    def save_results(self, results: Dict[str, Any], original_file_path: str, output_dir: str = None):
        """Salvar resultados da análise em arquivos TXT"""
        base_name = os.path.splitext(os.path.basename(original_file_path))[0]
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_path = os.path.join(output_dir, base_name)
        else:
            base_path = base_name
        
        # Salvar estatísticas como markdown
        with open(f"{base_path}_estatisticas.txt", "w", encoding="utf-8") as f:
            f.write(results['statistics'])
        
        # Salvar análise de IA como markdown
        with open(f"{base_path}_analise_ia.txt", "w", encoding="utf-8") as f:
            f.write(results['ai_analysis'])
        
        # Salvar relatório combinado como markdown
        combined_report = f"""# 📊 Relatório de Análise de Dados

## Conjunto de Dados: {base_name}

## Estatísticas Descritivas

{results['statistics']}

## Análise

{results['ai_analysis']}

---
*Relatório gerado automaticamente com Analisador de Dados com IA*
"""
        with open(f"{base_path}_relatorio_completo.txt", "w", encoding="utf-8") as f:
            f.write(combined_report)
        
        print(f"💾 Resultados salvos como arquivos Markdown:")
        print(f"   - {base_path}_estatisticas.txt")
        print(f"   - {base_path}_analise_ia.txt")
        print(f"   - {base_path}_relatorio_completo.txt")