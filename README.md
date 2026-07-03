# Tech Challenge Fase 2 - Pipeline de Dados para Avaliação da Alfabetização no Brasil

## Objetivo

Construir uma plataforma de dados para análise exploratória dos dados de alfabetização do Brasil utilizando arquitetura Lakehouse na AWS.

O projeto contempla:

- Ingestão Batch de dados públicos da Base dos Dados (BigQuery)
- Armazenamento em Data Lake (Amazon S3)
- Tratamento em arquitetura medalhão (Bronze, Silver e Gold)
- Streaming de dados utilizando Apache Kafka
- Disponibilização dos dados para análise exploratória e tomada de decisão

---

## Dataset

Fonte:

https://basedosdados.org/dataset/073a39d4-89cf-4068-b1e8-34ed0d9c0b72

Base:

Avaliação da Alfabetização - INEP

Tabelas utilizadas:

- alunos
- municipio
- uf
- meta_alfabetizacao_municipio
- meta_alfabetizacao_uf
- meta_alfabetizacao_brasil

---

## Arquitetura

Diagrama detalhado da pipeline (também em [docs/arquitetura.md](docs/arquitetura.md)):

```mermaid
flowchart TD
    A["Base dos Dados / BigQuery<br/><small>6 tabelas · SQL batch</small>"] --> B

    subgraph BRONZE["Bronze — dados brutos (S3)"]
        B["Parquet + metadados técnicos<br/><small>partição: ingestion_date</small>"]
    end

    B --> S1

    subgraph SILVER["Silver — dados tratados e integrados"]
        direction LR
        S1["Leitura"] --> S2["Profiling"]
        S2 --> S3["Qualidade"]
        S3 --> S4["Transformação"]
        S4 --> S5["Escrita"]
        S3 -. inválidos .-> Q["Quarentena"]
        S5 --> R["Relatório"]
    end

    S5 --> I["Integração"]
    I --> G1

    subgraph GOLD["Gold — datasets analíticos"]
        direction LR
        G1["Indicador por<br/>município"]
        G2["Metas ×<br/>resultados"]
        G3["Evolução<br/>temporal"]
        G4["Desempenho<br/>dos alunos"]
    end

    subgraph STREAMING["Streaming — Apache Kafka"]
        direction LR
        P["Producer"] --> K["Tópico Kafka"]
        K --> CO["Consumer"]
    end

    CO --> B2["S3 · streaming/"]

    GOLD --> C1["Dashboards"]
    GOLD --> C2["Machine learning"]
    GOLD --> C3["Políticas públicas"]
```

Fluxo resumido: Base dos Dados → BigQuery → Python → Amazon S3 (Bronze) →
Silver (profiling + qualidade + padronização + integração) → Gold (datasets
analíticos) → análise exploratória, dashboards e IA.

---

## Estrutura do Projeto

```text
tech-challenge-fase2/
│
├── src/
│   ├── common/     # logger e utilitários compartilhados
│   ├── bronze/     # ingestão dos dados brutos (Base dos Dados -> S3)
│   ├── silver/     # limpeza, qualidade, padronização e integração (orientada por metadados)
│   ├── gold/       # datasets analíticos
│   └── streaming/  # ingestão em streaming (Kafka)
│
├── tests/          # testes de lógica com dados sintéticos
├── reports/        # cópia local dos relatórios de qualidade
├── docs/           # documentação técnica e catálogo de dados
├── notebooks/
├── tmp/
│
├── .env
├── .gitignore
├── .python-version
├── requirements.txt
└── README.md
```

---

## Tecnologias Utilizadas

- Python
- Pandas
- PyArrow
- Boto3
- Base dos Dados
- Google BigQuery
- Amazon S3
- Apache Kafka
- Git
- GitHub

---

# Configuração do Ambiente

## Pré-requisitos

- Git
- Python (versão definida em `.python-version`)

## Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd tech-challenge-fase2
```

## Criar o ambiente virtual

```bash
python -m venv .venv
```

## Ativar o ambiente virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## Instalar as dependências

```bash
pip install -r requirements.txt
```

## Verificar a instalação

```bash
python --version
pip list
```

---

## Decisões Técnicas

### Amazon S3

Escolhido por possuir:

- alta durabilidade
- baixo custo
- escalabilidade praticamente ilimitada
- integração nativa com Glue e Athena

---

### Formato Parquet

Escolhido por:

- armazenamento colunar
- menor espaço em disco
- consultas mais rápidas
- menor custo em motores analíticos

---

### Ingestão via Base dos Dados + BigQuery

Escolhido por:

- evitar extrações manuais em CSV
- processo reproduzível
- pipeline automatizável
- arquitetura mais próxima de ambientes corporativos

---

### Arquitetura Modular

O projeto foi dividido em módulos:

- config
- queries
- extract
- upload
- pipeline

Objetivos:

- separação de responsabilidades
- menor acoplamento
- maior manutenibilidade
- facilidade para testes e trabalho em equipe

---

### Camada Silver orientada por metadados

A camada Silver utiliza um catálogo centralizado localizado em `src/silver/catalog.py`.

Esse catálogo concentra as regras de negócio de cada tabela, incluindo:

- descrição;
- chave natural;
- colunas obrigatórias;
- regras de validação;
- colunas categóricas.

O pipeline utiliza essas informações para executar automaticamente as validações e transformações da camada Silver, reduzindo duplicação de código, facilitando manutenção e simplificando a inclusão de novas tabelas.

---

## Metadados de Ingestão

As tabelas Bronze recebem os seguintes metadados:

- `_ingestion_ts`
- `_source`
- `_table`

Objetivos:

- rastreabilidade
- auditoria
- governança de dados
- reprocessamento

---

## Camada Silver

A camada Silver transforma os dados brutos da Bronze em dados **limpos,
padronizados, validados e integrados**, de forma **orientada por metadados**:
as regras de cada tabela (chave natural, colunas obrigatórias, validações e
colunas categóricas) ficam centralizadas em `src/silver/catalog.py` e o
pipeline as aplica automaticamente. O detalhamento está em
[docs/silver_rules.md](docs/silver_rules.md).

Fluxo por tabela: leitura da Bronze → *data profiling* → regras de qualidade →
transformações → integração relacional (`src/silver/integration.py`) →
gravação em `silver/` + relatórios de qualidade e de relacionamento.

---

## Camada Gold

A camada Gold disponibiliza **datasets analíticos** prontos para dashboards,
estatística e machine learning. Assim como a Silver, ela é **orientada por
metadados**: cada dataset é declarado em `src/gold/catalog.py` com descrição,
tabelas Silver de origem e função de construção.

- `indicador_alfabetizacao_municipio` — indicador por município/rede/série.
- `comparativo_metas_resultados` — taxa realizada vs. metas 2024-2030 em
  formato longo (`ano_meta`, `meta_alfabetizacao`, `gap_para_meta`,
  `atingiu_meta`), nos níveis município, UF e Brasil, a partir das tabelas
  integradas da Silver.
- `evolucao_temporal_indicador` — evolução da taxa por localidade ao longo do tempo.
- `desempenho_alunos_municipio` — agregado por município/rede a partir de
  `alunos_integrado`: total de alunos, proficiência média ponderada pelo peso
  amostral e percentual de alfabetizados.

Os datasets são gravados em `gold/{tabela}/processing_date=YYYY-MM-DD/` no S3,
com metadados técnicos (`_processed_ts`, `_layer`, `_table`) e relatório de
profiling em `reports/profiling/gold/`.

---

## Streaming com Kafka

Ingestão de eventos de avaliação de alunos em tempo quase real
(`src/streaming/`):

- **Producer** (`src/streaming/producer.py`) — publica eventos simulados de
  avaliação no tópico `alfabetizacao.alunos.eventos`, com chave por município.
- **Consumer** (`src/streaming/consumer.py`) — valida cada evento na chegada
  (regras espelhadas do catálogo Silver da tabela `alunos`) e grava
  micro-batches Parquet em `streaming/alunos_eventos/ingestion_date=.../`;
  eventos inválidos vão para `streaming/alunos_eventos_invalidos/`.

Subir o Kafka local (modo KRaft, sem Zookeeper):

```bash
docker compose -f infra/docker-compose.kafka.yml up -d
```

Executar o fluxo:

```bash
python -m src.streaming.producer --total 100 --intervalo 0.2
python -m src.streaming.consumer               # grava no S3
python -m src.streaming.consumer --sink local  # grava em tmp/ (sem AWS)
```

Configuração via `.env` (opcional): `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`,
`KAFKA_CONSUMER_GROUP`, `STREAMING_BATCH_SIZE`, `STREAMING_IDLE_TIMEOUT_MS`.

---

## Como Executar

Pré-requisitos: `.env` configurado (credenciais AWS + `S3_BUCKET_NAME`) e a
Bronze já ingerida no S3.

```bash
python -m src.bronze.pipeline    # Ingestão Bronze
python -m src.silver.pipeline    # Tratamento, qualidade e integração (Silver)
python -m src.gold.pipeline      # Datasets analíticos (Gold)
python -m tests.test_silver_gold # Testes de lógica (sem AWS/Kafka)
```

Para o streaming com Kafka, ver a seção [Streaming com Kafka](#streaming-com-kafka).

---

## FinOps — Otimização de Custos

Detalhes em [docs/finops.md](docs/finops.md). Principais decisões que reduzem
custo operacional:

- **Parquet + compressão** e **particionamento por data**, permitindo
  *partition pruning* e reduzindo o volume escaneado por consulta.
- **Arquitetura serverless** (S3 + Athena sugerido), sem cluster persistente:
  custo proporcional ao uso.
- **Leitura apenas da partição mais recente** e **quarentena única** na Silver,
  evitando reprocessamento.
- Recomendação de **S3 Lifecycle Policies** para arquivar partições Bronze
  antigas em classes mais baratas.

---

## Monitoramento

Observabilidade básica via `logging`: cada etapa registra início, fim, volume
processado e falhas. As pipelines consolidam tabelas com sucesso e com erro e
falham explicitamente (`RuntimeError`) quando há tabelas com falha, facilitando
alertas. Os relatórios ficam em `reports/` (profiling por camada em
`reports/profiling/{bronze,silver,gold}/` e qualidade em `reports/quality/`,
com status OK/WARNING/ERROR por tabela). No streaming, eventos reprovados na
validação são preservados em `streaming/alunos_eventos_invalidos/` para
auditoria.

---

## Aplicação em IA

A camada Gold foi desenhada para viabilizar:

- **Modelos de predição de alfabetização** por município (regressão da
  `taxa_alfabetizacao` a partir de variáveis territoriais e socioeconômicas).
- **Análise de desigualdade educacional** e **clusters de vulnerabilidade**
  (agrupamento de municípios por desempenho e distância até a meta).
- **Políticas públicas baseadas em dados**, priorizando localidades com maior
  `gap_para_meta` no comparativo metas × resultados.

A estrutura permite enriquecimento futuro com fontes externas (Censo Escolar,
IBGE/PNAD, FUNDEB) para ampliar o poder preditivo.

---

# Como Contribuir

Para manter a organização do projeto, todas as alterações devem seguir o fluxo de versionamento abaixo.

## 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd tech-challenge-fase2
```

## 2. Atualizar a branch develop

```bash
git checkout develop
git pull
```

## 3. Criar uma branch de desenvolvimento

Utilize o padrão:

```text
feature/nome-da-feature
```

Exemplo:

```bash
git checkout -b feature/silver-layer
```

## 4. Desenvolver a funcionalidade

Implemente e teste sua alteração localmente.

## 5. Registrar as alterações

```bash
git add .
git commit -m "feat: implementação da camada Silver"
```

## 6. Enviar para o GitHub

```bash
git push -u origin feature/silver-layer
```

## 7. Abrir um Pull Request

Após concluir a implementação, abra um Pull Request para a branch `develop` para revisão e integração ao projeto.

---

## Status do Projeto

- ✅ Fase 1 - Setup e Ingestão Bronze concluída
- ✅ Fase 2 - Camada Silver (orientada por metadados, qualidade e integração)
- 🔄 Fase 3 - Camada Gold (datasets analíticos)
- 🔄 Fase 4 - Streaming Kafka
- ⬜ Fase 5 - Análise Exploratória e Apresentação
