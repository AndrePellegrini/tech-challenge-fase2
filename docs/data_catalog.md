# Catálogo de Dados

Documentação das tabelas em cada camada da arquitetura medalhão.

---

## Camada Bronze (`bronze/`)

Dados brutos extraídos da Base dos Dados / BigQuery, convertidos para Parquet e
enriquecidos apenas com metadados técnicos. Particionados por `ingestion_date`.

| Tabela | Descrição | Chaves principais |
|---|---|---|
| `alunos` | Microdados por aluno (proficiência, alfabetizado, peso) | ano, id_aluno, id_escola, id_municipio |
| `municipio` | Indicadores de alfabetização por município | ano, id_municipio, rede, serie |
| `uf` | Indicadores de alfabetização por UF | ano, sigla_uf, rede, serie |
| `meta_municipio` | Metas de alfabetização por município (2024–2030) | ano, id_municipio, rede |
| `meta_uf` | Metas de alfabetização por UF (2024–2030) | ano, sigla_uf, rede |
| `meta_brasil` | Metas nacionais de alfabetização (2024–2030) | ano, rede |

**Metadados técnicos:** `_ingestion_ts`, `_source`, `_table`.

---

## Camada Silver (`silver/`)

Dados limpos, padronizados e validados. Particionados por `processing_date`.

| Tabela Silver | Origem Bronze | Descrição |
|---|---|---|
| `alunos` | `alunos` | Microdados tratados (tipos padronizados, sem duplicidade de chave) |
| `alfabetizacao_municipio` | `municipio` | Indicadores municipais tratados |
| `alfabetizacao_uf` | `uf` | Indicadores estaduais tratados |
| `metas` | `meta_brasil` + `meta_uf` + `meta_municipio` | Metas consolidadas em formato longo (uma linha por ano-alvo) |

**Padronizações aplicadas:**
- nomes de colunas normalizados (minúsculas, sem espaços);
- `ano` como inteiro (`Int64`);
- `id_municipio` como string de dígitos (código IBGE, sem `.0`);
- `sigla_uf` em maiúsculas;
- taxas/proporções/metas como `float`;
- remoção controlada de duplicidades por chave lógica.

**Estrutura da tabela `metas` (formato longo):**

| Coluna | Descrição |
|---|---|
| `nivel_geografico` | `brasil`, `uf` ou `municipio` |
| `ano` | ano-base do dado |
| `ano_meta` | ano-alvo da meta (2024–2030) |
| `id_municipio` / `sigla_uf` | chave de localidade (conforme o nível) |
| `rede` | rede de ensino |
| `taxa_alfabetizacao` | taxa realizada no ano-base |
| `meta_alfabetizacao` | meta para o `ano_meta` |
| `percentual_participacao` | percentual de participação |

**Metadados técnicos:** `_silver_processing_ts`, `_source_layer`, `_table`.

**Quarentena e qualidade:** registros reprovados vão para
`quality/<tabela>_quarentena/` (com a coluna `_quality_errors`) e os relatórios
de qualidade para `quality/reports/<tabela>/`.

---

## Camada Gold (`gold/`)

Datasets analíticos prontos para dashboards, estatística e ML. Particionados por
`processing_date`.

| Dataset Gold | Origem Silver | Descrição |
|---|---|---|
| `indicador_alfabetizacao_municipio` | `alfabetizacao_municipio` | Indicador de alfabetização por município/rede/série |
| `comparativo_metas_resultados` | `metas` | Taxa realizada vs. meta, com `gap_para_meta` e `atingiu_meta` |
| `evolucao_temporal_indicador` | `metas` | Evolução da taxa realizada por localidade ao longo dos anos |

**Metadados técnicos:** `_gold_processing_ts`, `_source_layer`, `_table`.
