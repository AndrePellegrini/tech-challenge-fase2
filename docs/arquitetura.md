# Arquitetura do Projeto

## Diagrama da pipeline (arquitetura medalhão)

```mermaid
flowchart TD
    A["Base dos Dados / BigQuery<br/><small>6 tabelas · SQL batch</small>"] --> B

    subgraph BRONZE["Bronze — dados brutos (S3)"]
        B["Parquet + metadados técnicos<br/><small>partição: ingestion_date</small>"]
    end

    B --> S1

    subgraph SILVER["Silver — dados tratados e integrados"]
        direction LR
        S1["Leitura<br/>reader.py"] --> S2["Profiling<br/>profiling.py"]
        S2 --> S3["Qualidade<br/>quality.py"]
        S3 --> S4["Transformação<br/>transform.py"]
        S4 --> S5["Escrita<br/>upload.py"]
        S3 -. inválidos .-> Q["Quarentena<br/>quality/"]
        S5 --> R["Relatório<br/>quality/reports/"]
    end

    S5 --> G1

    subgraph GOLD["Gold — datasets analíticos"]
        direction LR
        G1["Indicador por<br/>município"]
        G2["Metas ×<br/>resultados"]
        G3["Evolução<br/>temporal"]
    end

    GOLD --> C1["Dashboards"]
    GOLD --> C2["Machine learning"]
    GOLD --> C3["Políticas públicas"]
```

## Fluxo textual

```text
                 Base dos Dados
                         │
                         │ SQL
                         ▼
                    BigQuery
                         │
                         ▼
                    Python ETL
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
        Parquet                 Metadados
            │                         │
            └────────────┬────────────┘
                         │
                         ▼
                    Amazon S3
                  Camada Bronze
                         │
                         ▼
                    Silver Layer
                         │
                         ▼
                     Gold Layer
                         │
                         ▼
                 Exploração de Dados
```