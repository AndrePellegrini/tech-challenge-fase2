# Decisões Técnicas

## AWS S3

Motivos:

- baixo custo
- alta disponibilidade
- alta durabilidade
- integração com Athena e Glue

---

## Parquet

Motivos:

- formato colunar
- compressão eficiente
- melhor performance analítica
- redução de custos

---

## Base dos Dados + BigQuery

Motivos:

- acesso programático
- ingestão reproduzível
- eliminação de etapas manuais
- arquitetura próxima de ambientes corporativos

---

## Arquitetura Medalhão

Bronze:
dados brutos com metadados.

Silver:
dados limpos e padronizados.

Gold:
dados preparados para consumo analítico.

---

## Camada Gold orientada por catálogo

Seguindo o mesmo padrão orientado por metadados da camada Silver, a Gold
utiliza um catálogo centralizado (`src/gold/catalog.py`) que declara, para
cada dataset analítico: descrição, tabelas Silver de origem e a função de
construção (builder).

Motivos:

- consistência com o desenho da Silver
- inclusão de novos datasets sem alterar o pipeline
- rastreabilidade da linhagem (fontes declaradas por dataset)

Datasets gerados:

- `indicador_alfabetizacao_municipio`
- `comparativo_metas_resultados` (metas 2024-2030 em formato longo, com
  `gap_para_meta` e `atingiu_meta`, nos níveis município, UF e Brasil)
- `evolucao_temporal_indicador`
- `desempenho_alunos_municipio` (proficiência média ponderada pelo peso
  amostral e percentual de alfabetizados)

---

## Streaming com Apache Kafka

Motivos:

- ingestão de eventos em tempo quase real, complementando o batch
- desacoplamento entre produtores e consumidores
- padrão de mercado para plataformas de dados

Implementação:

- `kafka-python` como cliente (leve, sem dependências nativas)
- Kafka local em modo KRaft via Docker Compose
  (`infra/docker-compose.kafka.yml`), sem Zookeeper
- producer publica eventos simulados de avaliação de alunos, com chave por
  município (preserva a ordem por partição)
- consumer valida cada evento na chegada (espelhando as regras da tabela
  `alunos` do catálogo Silver) e grava micro-batches Parquet no S3,
  particionados por `ingestion_date`; eventos reprovados vão para um
  prefixo de inválidos, preservando o dado para auditoria

---

## Modularização do Projeto

Aplicação do princípio de responsabilidade única (SRP):

config
queries
extract
upload
pipeline

Benefícios:

- manutenção simplificada
- reutilização
- facilidade de testes
- trabalho colaborativo