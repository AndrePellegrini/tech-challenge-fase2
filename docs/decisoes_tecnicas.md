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