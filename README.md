# Processo Seletivo para Engenheiro de Dados Jr - beAnalytic

Autor: Pedro Vitor Soares Gomes de Lima.

Requisitos para rodar a aplicação: arquivo com credenciais para acessar o Google Sheets e ter o Docker instalado.

## Problema proposto

Acessar um arquivo JSON disponibilizado via link compartilhado do Google Drive (não adicionado aqui por questão de privacidade) e enviar os dados presentes para uma planilha do Google Sheets (não adicionada aqui por questão de privacidade).

## Abordagem escolhida para resolução do problema

### Resumo do funcionamento 

1. acessar o arquivo JSON a partir do link disponibilizado;

2. transformar o conteúdo do arquivo JSON em um dicionário do python e utilizar todas as chaves presentes como cabeçalho da planilha (todas as possíveis chaves, independente de estar ou não presente em todos os registros);

3. sempre que executar o script em python, criar uma aba na planilha com o nome sendo a data e hora atual e preencher as células sempre conferindo as chaves com o cabeçalho.

### Automação da aplicação

- a aplicação é executada com um cron job e, para efeito de demonstração, foi escolhido um intervalo de 10 minutos;

- existência de uma aba de consolidação, que guarda um resumo dos dados de todas as abas existentes.

### Requisitos

A escolha de rodar a aplicação com o Docker foi a forma de garantir que todos os requisitos necessários para a aplicação fossem satisfeitos em qualquer máquina, são eles: instalação de bibliotecas, correto agendamento da execução do script e padronização do fuso horário utilizado. Possuindo o Docker devidamente instalado na máquina, basta subir o container a partir do arquivo "docker-compose.yml".

### Planilha final

- para efeito de demonstração, a aplicação funcionou entre 15:00 e 16:00 do dia 16/06/2022. Por isso, é possível encontrar 7 abas com carimbo data e hora (15:00, 15:10, 15:20, 15:30, 15:40, 15:50 e 16:00);

- para mostrar o funcionamento da consolidação dos dados, o arquivo "testing-data-consolidation.json" foi criado. Nele consta todas as chaves presentes no arquivo JSON disponibilizado para o case e ainda foi adicionada uma nova chave e valor: "NOVA COLUNA": "TESTE";

- a primeira execução do script foi com esse arquivo criado e as seguintes foram com o disponibilizado para o case. A ideia é demonstrar o tratamento na questão de inserir o conteúdo de acordo com a relação chave e cabeçalho e de sempre considerar todos os dados existentes em todas as abas.


## Estrutura dos arquivos do repositório

- arquivo "docker-compose.yml": para funcionamento da aplicação, basta subir o container presente neste arquivo. Nele constam a criação da imagem e o mapeamento dos volumes;

- pasta "data": armazena o arquivo JSON utilizado para testar o algoritmo de consolidação e o arquivo JSON com as credenciais que autorizam o acesso à planilha;

- pasta "docker-image": armazena o arquivo do Dockerfile para criação da imagem e o arquivo crontab que agenda o funcionamento da aplicação;

- pasta "script": armazena o script em python que executa a leitura dos dados e escrita na planilha do Google Sheets.

## Pontos importantes considerados

- funcionamento do algoritmo de consolidação: é executado sempre que uma aba é criada, é verificado o que já tem de informação (chaves e conteúdo) na aba "DATA CONSOLIDATION" e, considerando uma chave identificadora, anexam-se novas linhas caso estas ainda não constem;

- chave identificadora: apesar de não ser a escolha ideal, para efeito de demonstração, foi definido o "email" como chave identificadora. Como os dados que estão sendo trabalhados já não apresenta um ID, uma abordagem para essa situação seria a de gerar uma chave identificadora, por exemplo, usando cada valor presente nos registros;

- alinhamento conteúdo e cabeçalho: um cuidado tomado em todo o desenvolvimento da aplicação foi o de garantir que a inserção dos dados sempre respeite o cabeçalho da planilha e, caso não exista correspondência, a célula é deixada em branco.
