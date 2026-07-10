# 📚 Pipeline de Dados para Análise da Alfabetização no Brasil

Projeto desenvolvido para o **Tech Challenge da Pós-Tech FIAP**.

O objetivo é construir uma plataforma de dados moderna para apoiar a análise da alfabetização no Brasil, utilizando arquitetura **Lakehouse** em ambiente **AWS**, processamento **batch** e **streaming**, além da integração de diferentes fontes de dados públicas.

---

# 🎯 Objetivo

Construir uma pipeline híbrida de dados capaz de coletar, tratar, integrar e disponibilizar indicadores de alfabetização para consumo analítico.

A solução foi desenvolvida seguindo a arquitetura **Medallion (Bronze, Silver e Gold)**, permitindo a separação entre dados brutos, dados tratados e datasets analíticos.

O projeto contempla:

- ingestão batch de dados públicos da **Base dos Dados (BigQuery)**;
- ingestão de fonte externa do **Atlas do Desenvolvimento Humano**;
- armazenamento em **Amazon S3**;
- processamento em arquitetura Medalhão;
- validação automática da qualidade dos dados;
- integração entre diferentes bases públicas;
- geração de datasets analíticos (Gold);
- simulação de ingestão em tempo real utilizando **Apache Kafka**;
- disponibilização dos dados por meio de um dashboard em **Streamlit**.

---

# 🏗️ Arquitetura da Solução

```text
                     Base dos Dados
                         (BigQuery)
                              │
                              ▼
                      Bronze Layer
                              ▲
                              │
       Atlas do Desenvolvimento Humano
                              │
                              ▼
                      Silver Layer
                              │
                              ▼
                 Silver Integrada (Joins)
                              │
                              ▼
                        Gold Layer
                              │
                              ▼
                    Dashboard (Streamlit)

Kafka Producer ─────► Kafka ─────► Kafka Consumer
```

A solução foi desenvolvida de forma modular, onde cada camada possui responsabilidades bem definidas, facilitando manutenção, escalabilidade e reutilização dos componentes.

# 📂 Fontes de Dados

A solução integra diferentes fontes públicas de dados relacionadas ao contexto da alfabetização no Brasil.

## 1. Base dos Dados (BigQuery)

Principal fonte de dados do projeto, contendo os indicadores oficiais do programa **Compromisso Nacional Criança Alfabetizada**.

Foram utilizadas as seguintes entidades:

- Alunos
- Município
- Unidade da Federação (UF)
- Meta Brasil
- Meta por UF
- Meta por Município

Esses dados são ingeridos periodicamente via **BigQuery**, compondo a camada Bronze do Data Lake.

---

## 2. Atlas do Desenvolvimento Humano

Como enriquecimento da solução, foi integrada uma segunda fonte pública de dados proveniente do **Atlas do Desenvolvimento Humano no Brasil**.

A integração dessa fonte foi realizada em quatro etapas:

### 1. Seleção da base

Os dados foram obtidos no portal oficial do Atlas do Desenvolvimento Humano:

https://www.atlasbrasil.org.br/acervo/biblioteca

Foi selecionada a base **PNAD Contínua (2012 até 2024)**, contendo indicadores socioeconômicos em diferentes granularidades geográficas. Foi feito também o download da base **Metadados de PNAD Contínua** para avaliarmos o significado de cada coluna e estrutura da base.

---

### 2. Exploração e Pré-processamento no Notebook

Antes da integração à pipeline, foi realizada uma análise exploratória e pré-processamento da base no notebook:

```text
notebooks/03_atlas_exploration.ipynb
```

Nesse notebook foram executadas as seguintes atividades:

- exploração da estrutura da base;
- análise das granularidades disponíveis;
- identificação dos indicadores disponíveis;
- avaliação da compatibilidade com a modelagem do projeto.

Após essa etapa, optou-se por utilizar apenas a granularidade de **Unidade da Federação (UF)**, por ser compatível com a tabela `uf` da camada Silver. As regras de transformação definidas em `src/atlas/transform.py` foram aplicadas para:

- seleção apenas da granularidade de UF;
- padronização dos nomes das colunas;
- conversão do código IBGE para sigla da UF;
- seleção dos indicadores utilizados no projeto (IDHM, IDHM Educação, IDHM Renda, IDHM Longevidade);
- seleção apenas dos anos de interesse (2023 e 2024).

Como resultado desse pré-processamento, foi gerada uma versão reduzida da base em formato **Parquet**:

```text
data/external/atlas_uf.parquet
```

Essa versão contém apenas os registros e colunas necessários para o projeto (54 registros — 27 UFs × 2 anos). A pipeline do Atlas utiliza diretamente esse arquivo como entrada, tornando o projeto totalmente reproduzível sem necessidade de novos downloads durante a avaliação.

---

## Integração entre as fontes

A integração ocorre durante a camada Silver, onde as tabelas tratadas são relacionadas utilizando chaves padronizadas.

As integrações implementadas são:

- Município ↔ Metas Municipais;
- UF ↔ Metas por UF;
- UF ↔ Atlas do Desenvolvimento Humano.

Os indicadores do Atlas são posteriormente disponibilizados na camada Gold, permitindo análises que relacionam desenvolvimento humano e desempenho educacional.

---

# 🥉 Arquitetura Medalhão

A solução foi construída seguindo a arquitetura **Medallion**, organizando os dados em três camadas com responsabilidades distintas.

## Bronze

Responsável pela ingestão e armazenamento dos dados em seu formato original.

Nesta camada são realizadas:

- ingestão batch dos dados da Base dos Dados (BigQuery);
- ingestão da fonte externa Atlas do Desenvolvimento Humano;
- armazenamento em formato Parquet no Amazon S3;
- inclusão de metadados técnicos (`_source`, `_table` e `_ingestion_ts`).

Nenhuma regra de negócio é aplicada nessa etapa.

---

## Silver

Responsável pela padronização, validação e integração dos dados.

As principais atividades realizadas são:

- validação de colunas obrigatórias;
- validação de valores nulos;
- validação de duplicidades;
- validação de regras de faixa;
- validação de integridade referencial;
- padronização de nomes de colunas;
- otimização dos tipos de dados;
- geração de profiling;
- geração de relatórios de qualidade;
- integração entre as diferentes entidades da Base dos Dados;
- enriquecimento dos dados de UF com indicadores do Atlas do Desenvolvimento Humano.

Todas as regras de qualidade são centralizadas em metadados (`catalog.py`), permitindo que o pipeline seja orientado por configuração e facilmente extensível.

---

## Gold

Responsável pela construção dos datasets analíticos utilizados por dashboards e análises.

Atualmente a camada Gold disponibiliza:

- indicadores de alfabetização por município;
- comparativo entre metas e resultados;
- evolução temporal dos indicadores;
- desempenho agregado dos alunos por município.

Esses datasets são construídos exclusivamente a partir da camada Silver, preservando o princípio de separação entre dados operacionais e dados analíticos.

---

## Streaming

Além do processamento batch, o projeto implementa uma pipeline de streaming utilizando Apache Kafka.

Os eventos produzidos simulam a chegada contínua de dados educacionais, sendo consumidos por um consumidor responsável pelo processamento e persistência dessas informações.

Essa arquitetura demonstra a coexistência de processamento batch e streaming dentro do mesmo Data Lake.

---

# 📁 Estrutura do Projeto

O projeto foi organizado em módulos independentes, separando responsabilidades entre ingestão, transformação, integração, disponibilização analítica e streaming.

```text
tech-challenge-fase2/

├── dashboard/              # Dashboard Streamlit
│   └── app.py
│
├── data/
│   └── external/
│       └── atlas_uf.parquet
│
├── docs/                   # Documentação técnica
│
├── notebooks/              # Estudos exploratórios
│   └── 03_atlas_exploration.ipynb
│
├── reports/
│   ├── profiling/
│   └── quality/
│
├── src/
│   ├── atlas/              # Pipeline da fonte Atlas
│   ├── bronze/             # Ingestão Base dos Dados
│   ├── common/             # Componentes compartilhados
│   ├── gold/               # Datasets analíticos
│   ├── silver/             # Limpeza, qualidade e integração
│   └── streaming/          # Kafka Producer / Consumer
│
├── .env
├── requirements.txt
└── README.md
```

---

## Organização das camadas

### 🥉 Bronze

Responsável pela ingestão das fontes de dados e armazenamento dos dados brutos em formato Parquet.

### 🥈 Silver

Responsável pela padronização, validação de qualidade, integração entre tabelas e enriquecimento com dados externos.

### 🥇 Gold

Responsável pela construção dos datasets analíticos consumidos por dashboards e análises exploratórias.

### ⚡ Streaming

Responsável pela simulação de eventos em tempo real utilizando Apache Kafka.

--- 

# ▶️ Como Executar

## 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd tech-challenge-fase2
```

---

## 2. Criar um ambiente virtual

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## 4. Configurar as variáveis de ambiente

Criar um arquivo `.env` na raiz do projeto contendo:

```text
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=...
S3_BUCKET_NAME=...
BILLING_PROJECT_ID=...
```

As variáveis possuem as seguintes finalidades:

| Variável | Descrição |
|----------|-----------|
| `AWS_ACCESS_KEY_ID` | Chave de acesso da conta AWS utilizada para autenticação no Amazon S3. |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta associada ao usuário IAM da AWS. |
| `AWS_REGION` | Região onde o bucket S3 está provisionado (ex.: `us-east-1`). |
| `S3_BUCKET_NAME` | Nome do bucket utilizado como Data Lake do projeto. |
| `BILLING_PROJECT_ID` | ID do projeto do Google Cloud utilizado para executar consultas no BigQuery por meio da Base dos Dados. |

> **Observação:** para executar a camada Bronze é necessário possuir um projeto ativo no Google Cloud com permissão para criação de jobs no BigQuery, além de informar seu `BILLING_PROJECT_ID` no arquivo `.env`.

### Validação das Configurações

O projeto inclui um mecanismo de validação das variáveis de ambiente (implementado em `src/common/config.py`). Todas as variáveis listadas acima são verificadas no início da execução de qualquer módulo. Certifique-se de que todas as chaves AWS e o `BILLING_PROJECT_ID` estejam configurados corretamente para evitar erros de execução.

---

## 4.1. Configurar o Apache Kafka (para Streaming)

Para simular a ingestão de dados em tempo real, o projeto utiliza o Apache Kafka. Antes de executar as pipelines de streaming, é necessário iniciar o broker Kafka localmente utilizando Docker Compose.

```bash
docker compose -f infra/docker-compose.kafka.yml up -d
```

Para derrubar o ambiente Kafka após o uso:

```bash
docker compose -f infra/docker-compose.kafka.yml down
```

---

## 5. Executar a pipeline

### Bronze

```bash
python -m src.bronze.pipeline
```

### Atlas

```bash
python -m src.atlas.pipeline

python -m src.atlas.silver_pipeline
```

### Silver

```bash
python -m src.silver.pipeline
```

### Gold

```bash
python -m src.gold.pipeline
```

### Streaming

Producer

```bash
python -m src.streaming.producer
```

Consumer

```bash
python -m src.streaming.consumer
```

---

## 6. Executar o Dashboard

```bash
streamlit run dashboard/app.py
```

---

## Ordem recomendada de execução

```text
Bronze
      │
      ▼
Atlas
      │
      ▼
Silver
      │
      ▼
Gold
      │
      ▼
Dashboard

Streaming (Producer / Consumer)
```

---

# 💰 Estratégias de FinOps

Durante o desenvolvimento da solução foram adotadas decisões arquiteturais visando reduzir custos de armazenamento, processamento e transferência de dados.

## Armazenamento em Parquet

Todas as camadas do Data Lake utilizam o formato **Apache Parquet**, reduzindo significativamente o volume de dados armazenados e melhorando a performance de leitura quando comparado a formatos textuais como CSV.

---

## Particionamento dos dados

As tabelas são armazenadas no Amazon S3 utilizando partições por data de processamento.

Exemplo:

```text
silver/
    municipio/
        processing_date=2026-07-10/
            municipio.parquet
```

Essa estratégia permite:

- leitura apenas das partições necessárias;
- redução do volume de dados processados;
- melhor organização do Data Lake;
- menor custo de processamento.

---

## Arquitetura Medalhão

A separação entre Bronze, Silver e Gold evita reprocessamentos desnecessários.

Cada camada possui responsabilidades específicas:

- Bronze: ingestão dos dados brutos;
- Silver: limpeza, validação e integração;
- Gold: construção de datasets analíticos.

Dessa forma, alterações em dashboards ou análises não exigem nova ingestão dos dados de origem.

---

## Integração de fontes externas

A base do Atlas do Desenvolvimento Humano foi previamente explorada e reduzida para apenas os registros necessários ao projeto.

A versão utilizada pela pipeline contém apenas:

- anos de interesse (2023 e 2024);
- granularidade de Unidade da Federação;
- indicadores efetivamente utilizados nas análises.

Essa decisão reduziu a quantidade de registros de aproximadamente **700 para apenas 54**, diminuindo o volume processado em todas as etapas seguintes da pipeline.

---

## Reutilização de dados

As integrações entre tabelas são realizadas na camada Silver e reutilizadas pela Gold.

Essa abordagem evita a repetição de joins durante a construção dos datasets analíticos, reduzindo tempo de processamento e simplificando a manutenção da solução.

---

# 📊 Dashboard

Como exemplo de consumo da camada Gold, foi desenvolvido um dashboard interativo utilizando **Streamlit**.

O dashboard consome exclusivamente datasets da camada Gold, demonstrando a separação entre processamento de dados e consumo analítico.

Atualmente o dashboard disponibiliza:

- indicadores gerais da base;
- filtros por ano e rede de ensino;
- comparação da taxa de alfabetização entre as Unidades da Federação;
- análise da relação entre IDHM e taxa de alfabetização;
- tabela dinâmica para exploração dos dados.

O objetivo do dashboard é demonstrar como os datasets analíticos produzidos pela Gold podem ser utilizados para apoiar análises e tomada de decisão.

## Execução

```bash
streamlit run dashboard/app.py
```

## Exemplo

![Dashboard](https://private-us-east-1.manuscdn.com/sessionFile/2H6K1UX8yTldcujVzVowaD/sandbox/9q6cUWfhKgYdtsiaHH1zMP-images_1783691730749_na1fn_L2hvbWUvdWJ1bnR1L3RlY2gtY2hhbGxlbmdlL3RlY2gtY2hhbGxlbmdlLWZhc2UyIC0gdjEvZGFzaGJvYXJkL2ltYWdlcy9kYXNoYm9hcmQ.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvMkg2SzFVWDh5VGxkY3VqVnpWb3dhRC9zYW5kYm94LzlxNmNVV2ZoS2dZZHRzaWFISDF6TVAtaW1hZ2VzXzE3ODM2OTE3MzA3NDlfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzUmxZMmd0WTJoaGJHeGxibWRsTDNSbFkyZ3RZMmhoYkd4bGJtZGxMV1poYzJVeUlDMGdkakV2WkdGemFHSnZZWEprTDJsdFlXZGxjeTlrWVhOb1ltOWhjbVEucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzg1NTQyNDAwfX19XX0_&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=nlsu2F2KXPWqxfbO7JOplB4afLCRPOCvTRpmASYRPiXMYEKbEMq2T~uLmHa-~yIlWMkBVrQYBTQuWb-oExbGdppciP6PHB5AiNV6FwRPnquyDUuXI-KN7~d6LKHYsP60dQEqdDYdLkfRkAawQQi5TFyLBkfMLhrFQDfB2lImiDAkhF8m-rh7ReqaXXjmdpKGfDPTV20HLDF83Yy7H07BUFZ0IqtL9Uyuwzn0S8vwcZigaPifEF1Z7EDUDu9uxXS2UZbK5HI4OluBEOMXg~VR5SdNbwsfoM7Gi-FV8LMfQN6~3bvvVYxKPImjcaxpPJnaPlsSPNMAmLbw-68-HN0pNw__)

📄 Versão em alta resolução:
[dashboard.pdf](dashboard/images/dash_streamlit.pdf)

---

# ⚡ Streaming

Além do processamento batch, o projeto implementa uma pipeline de streaming utilizando **Apache Kafka**, simulando a chegada contínua de eventos relacionados ao contexto educacional.

A solução é composta por dois componentes principais:

- **Producer:** responsável por publicar eventos em um tópico Kafka;
- **Consumer:** responsável por consumir os eventos e realizar o processamento correspondente.

Essa arquitetura demonstra a coexistência de processamento **batch** e **streaming** dentro da mesma plataforma de dados.

## Fluxo de processamento

```text
Producer
    │
    ▼
Apache Kafka
    │
    ▼
Consumer
```

## Execução

Producer:

```bash
python -m src.streaming.producer
```

Consumer:

```bash
python -m src.streaming.consumer
```

O módulo de streaming foi desenvolvido de forma independente das pipelines batch, permitindo que novos eventos sejam processados continuamente sem interferir nas cargas periódicas do Data Lake.

---

# 🚀 Principais Entregas

Ao final do projeto foi construída uma plataforma de dados capaz de integrar múltiplas fontes públicas e disponibilizar informações consolidadas para consumo analítico.

As principais entregas incluem:

✅ Arquitetura Medalhão (Bronze, Silver e Gold);

✅ Pipeline de ingestão da Base dos Dados utilizando BigQuery;

✅ Pipeline de ingestão para fonte externa (Atlas do Desenvolvimento Humano);

✅ Integração entre indicadores educacionais e indicadores socioeconômicos;

✅ Validação automática de qualidade dos dados;

✅ Profiling das camadas Bronze e Silver;

✅ Relatórios automáticos de qualidade;

✅ Arquitetura orientada por metadados para validações e integrações;

✅ Pipeline de streaming utilizando Apache Kafka;

✅ Dashboard interativo desenvolvido em Streamlit;

✅ Documentação técnica e notebooks exploratórios.

---

A solução demonstra como diferentes técnicas de Engenharia de Dados podem ser combinadas para construir uma plataforma moderna de ingestão, tratamento, integração e disponibilização de dados para análise.


---

Desenvolvido como parte do **Tech Challenge — Pós-Tech FIAP**.

Arquitetura de Dados • Engenharia de Dados • Streaming • Data Lake • Analytics