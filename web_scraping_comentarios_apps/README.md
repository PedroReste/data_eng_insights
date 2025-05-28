# Web Scraping de Comentários de Aplicativos
**O que você vai encontrar nessa pasta?** \
Um exemplo de script simples de coleta dos comentários públicos de aplicativos feitos na **App Store** da Apple e na **Play Store** da Google, utilizado a biblioteca **google_play_scraper** e a uma **API pública** da Apple Store. \
Esse formato de coleta pode ser uma alternativa a momentos aonde não existe a possibilidade de contratar empresas especializadas nessa área ou para coletar dados públicos de concorrentes do mesmo ramo para realizar benchmarks. \
A coleta desses dados possibilita análises de desempenho de resposta ao público para comentários negativos e análise de sentimento para entender, além da nota geral, o que os usuários estão comentado sobre o aplicativo.

**Extração de Dados da Play Store**
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>app</th>
      <th>system</th>
      <th>score</th>
      <th>content</th>
      <th>app_version</th>
      <th>date</th>
      <th>reply_content</th>
      <th>reply_date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Claro</td>
      <td>Android</td>
      <td>5</td>
      <td>legal 😎</td>
      <td>18.7.0</td>
      <td>2025-05-27 18:54:37</td>
      <td>None</td>
      <td>NaT</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>Android</td>
      <td>5</td>
      <td>Encontro facilidade por aqui 👏</td>
      <td>18.6.0</td>
      <td>2025-05-27 18:10:04</td>
      <td>None</td>
      <td>NaT</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>Android</td>
      <td>5</td>
      <td>muito bom</td>
      <td>18.7.0</td>
      <td>2025-05-27 17:49:18</td>
      <td>None</td>
      <td>NaT</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>Android</td>
      <td>1</td>
      <td>ruim que vc deseja não tem informações</td>
      <td>None</td>
      <td>2025-05-27 17:46:20</td>
      <td>Olá,Junior! Estou aqui para te ajudar. Por gen...</td>
      <td>2025-05-28 08:58:31</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>Android</td>
      <td>5</td>
      <td>melhor do mundo</td>
      <td>18.7.0</td>
      <td>2025-05-27 17:20:22</td>
      <td>None</td>
      <td>NaT</td>
    </tr>
  </tbody>
</table>

**Extração de dados da App Store**
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>app</th>
      <th>system</th>
      <th>score</th>
      <th>content</th>
      <th>app_version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Claro</td>
      <td>iOS</td>
      <td>1</td>
      <td>Tenho essa aplicativo instalado há anos e quan...</td>
      <td>17.53.0</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>iOS</td>
      <td>1</td>
      <td>Poluído, muito ruim, esconde informação</td>
      <td>17.48.0</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>iOS</td>
      <td>1</td>
      <td>App is not at all intuitive. One thing it does...</td>
      <td>17.46.0</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>iOS</td>
      <td>4</td>
      <td>Boa tarde, sou cliente Claro e não vou mudar, ...</td>
      <td>17.27.0</td>
    </tr>
    <tr>
      <td>Claro</td>
      <td>iOS</td>
      <td>1</td>
      <td>Ate hoje nao ha suporte para eSIM… tudo relaci...</td>
      <td>17.26.0</td>
    </tr>
  </tbody>
</table>