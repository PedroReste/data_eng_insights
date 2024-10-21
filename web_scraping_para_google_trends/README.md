

<div style="text-align: center; padding-bottom: 10px; color: #6a5acd;">

# **Web Scraping para o Google Trends**

</div>


<div style="text-align: center; padding-bottom: 10px;">
  <img src="imagens/google_trends.png" alt="Google Trends" width="400">
</div>

**<span style="color:#6a5acd">O que você vai encontrar aqui?</span>** Uma forma de extrair dados do Google Trends de uma forma mais automatizada sobre termos popupalares na buscador da Google. Ao invés de extrair os dados "na mão", é possível utilizar o Python para reduzir o esforço necessário e o tempo gasto para obter essas informações.

Para essa "automatização" foi utilizado a biblioteca do [**PyTrends**](https://pypi.org/project/pytrends/), se trata de uma API não oficial que realiza requisições ao Google Trends para extrair os dados solicitados apartir de endpoints de APIs utilizadas no próprio Google Trends, se trata de uma forma de web scraping.

Por se tratar de uma forma de web scraping, é importante tormar cuidado na quantidade e a velocidade das requisições para evitar que seja bloqueada pela platorfoma, impedindo a obtenção dos dados.

<div style="text-align: center; padding-top: 2px; color: #6a5acd;">

## **Como Funciona o Google Trends?**

</div>

O Google Trends é uma ferramenta disponibilizada gratuitamente para acompanhar e analisar a popularidade de palavras-chaves que foram buscadas na pesquisa do Google em uma janela de tempo.


 **<span style="color:#6a5acd">**Como funciona o índice de popularidade?**</span>**

Baseado na período selecionado, na categoria, na região, no tipo de pesquisa e na quantidade de termos selecionados (01 à 05). O indíce é gerado com base na quantidade de pesquisas do Google para gerar um índice naquale período que vai de 0 à 100. Entendendo que:
- **00**: não há dados o suficiente para gerar uma nota.
- **50**: tem uma popularidade média.
- **100**: está no pico da popularidade.



<div style="text-align: center; padding-top: 10px;">
  <img src="imagens\interest_over_time.png" alt="Interest by Over Time" width="600">
</div>
