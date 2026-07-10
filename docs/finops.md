# FinOps — Otimização de Custos

Boas práticas de eficiência de custo em nuvem adotadas no projeto.

---

## Armazenamento

- **Formato Parquet + compressão**: formato colunar reduz drasticamente o
  volume em disco frente a CSV/JSON, diminuindo custo de armazenamento no S3 e
  de leitura em motores analíticos (Athena/Glue).
- **Particionamento por data** (`ingestion_date` / `processing_date`): permite
  *partition pruning*, lendo apenas as partições necessárias em cada consulta e
  reduzindo o volume escaneado (e, portanto, o custo por query no Athena).
- **Separação por camada** (bronze/silver/gold): dados brutos volumosos ficam
  isolados; consultas analíticas recorrentes rodam sobre a Gold, muito menor.

## Ciclo de vida (recomendado)

- Aplicar **S3 Lifecycle Policies** para mover partições Bronze antigas para
  classes mais baratas (S3 Standard-IA / Glacier), preservando o histórico a
  baixo custo.
- Manter apenas a Gold em classe de acesso frequente.

## Processamento

- **Leitura da partição mais recente**: o pipeline lê apenas a última partição
  de cada tabela, evitando reprocessar todo o histórico.
- **Quarentena**: registros inválidos são separados uma única vez na Silver,
  evitando reprocessamento e retrabalho a jusante.
- **Athena serverless** (consumo sugerido): sem cluster ocioso; paga-se apenas
  pelos dados escaneados — reforçado pelo Parquet particionado.

## Estimativa de custo da arquitetura

A arquitetura é *storage-first* e serverless, com custo dominado por:

1. **Armazenamento S3** — baixo, graças ao Parquet comprimido e particionado.
2. **Consultas Athena** — pago por dado escaneado; minimizado por particionamento
   e pela consulta preferencial da camada Gold (reduzida).
3. **Ingestão/BigQuery** — via Base dos Dados, com `billing_project_id`; os
   scans BigQuery são periódicos (batch), não contínuos.

Não há custo de cluster persistente (sem EMR/Spark dedicado), o que mantém o
custo operacional baixo e proporcional ao uso.
