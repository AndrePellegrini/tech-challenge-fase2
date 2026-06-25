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

Base dos Dados
↓
BigQuery
↓
Python
↓
Amazon S3 (Bronze)
↓
Silver
↓
Gold
↓
Análise Exploratória

---

## Estrutura do Projeto

```text
tech-challenge-fase2/

src/
│
├── bronze/
├── silver/
├── gold/
├── streaming/
└── quality/

docs/
infra/
notebooks/
tmp/

.env
.gitignore
requirements.txt
README.md
```

---

## Tecnologias Utilizadas

- Python 3.13
- Pandas
- PyArrow
- Base dos Dados
- BigQuery
- Amazon S3
- Apache Kafka
- Git
- GitHub

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

## Metadados de Ingestão

As tabelas Bronze recebem os seguintes metadados:

- _ingestion_ts
- _source
- _table

Objetivos:

- rastreabilidade
- auditoria
- governança de dados
- reprocessamento

---

## Status do Projeto

✅ Fase 1 - Setup e Ingestão Bronze concluída

🔄 Fase 2 - Construção da camada Silver

⬜ Fase 3 - Camada Gold

⬜ Fase 4 - Streaming Kafka

⬜ Fase 5 - Análise Exploratória e Apresentação