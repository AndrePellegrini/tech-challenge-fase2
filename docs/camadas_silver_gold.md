# Camadas Silver e Gold

Documentação técnica das camadas de tratamento (Silver) e analítica (Gold).

---

## Camada Silver

### Objetivo

Transformar os dados brutos da Bronze em dados **limpos, padronizados,
validados e integrados**, prontos para a construção da camada analítica.

### Módulos (`src/silver/`)

| Módulo | Responsabilidade |
|---|---|
| `reader.py` | Lê a partição mais recente das tabelas Bronze no S3 |
| `profiling.py` | Data Profiling: linhas, schema, nulos, duplicidades, estatísticas |
| `quality.py` | Regras de qualidade e separação válidos/inválidos |
| `transform.py` | Limpeza, padronização de tipos/chaves e consolidação de metas |
| `upload.py` | Gravação da Silver, quarentena e relatório de qualidade no S3 |
| `pipeline.py` | Orquestra todas as etapas |

### Estratégia (conforme o guia)

1. **Data Profiling** — diagnóstico das tabelas Bronze antes de transformar.
2. **Regras de qualidade** — definidas por tabela.
3. **Transformações** — conversões de tipo, normalização e remoção de duplicidades.
4. **Escrita Silver** — Parquet particionado por `processing_date`.
5. **Relatório de qualidade** — resumo das validações em `quality/`.

### Regras de qualidade implementadas

| Regra | Condição |
|---|---|
| `ano_obrigatorio` | `ano` não nulo e numérico |
| `taxa_entre_0_100` | `taxa_alfabetizacao` entre 0 e 100 (quando presente) |
| `proficiencia_nao_negativa` | `proficiencia` ≥ 0 (quando presente) |
| `sigla_uf_2_caracteres` | `sigla_uf` com 2 caracteres (quando presente) |
| `id_municipio_ibge_7_digitos` | `id_municipio` com 7 dígitos (quando presente) |
| `meta_entre_0_100` | `meta_alfabetizacao` entre 0 e 100 (quando presente) |
| Duplicidade de chave | reportada por tabela |
| Completude | percentual de preenchimento dos campos críticos |

Registros que falham em qualquer regra vão para a **quarentena**
(`quality/<tabela>_quarentena/`) com a coluna `_quality_errors` indicando quais
regras foram violadas. Os registros válidos seguem para `silver/`.

---

## Camada Gold

### Objetivo

Disponibilizar **datasets analíticos** prontos para dashboards, análises
estatísticas e treinamento de modelos de machine learning.

### Módulos (`src/gold/`)

| Módulo | Responsabilidade |
|---|---|
| `reader.py` | Lê as tabelas Silver (sem metadados técnicos) |
| `transform.py` | Constrói os datasets analíticos |
| `upload.py` | Grava os datasets na camada Gold |
| `pipeline.py` | Orquestra a construção da Gold |

### Datasets

- **`indicador_alfabetizacao_municipio`** — taxa de alfabetização e média de
  português por município, rede e série.
- **`comparativo_metas_resultados`** — junta a taxa realizada com as metas,
  calculando `gap_para_meta` (meta − realizado) e `atingiu_meta` (booleano).
- **`evolucao_temporal_indicador`** — série da taxa realizada por localidade e
  nível geográfico ao longo dos anos.

---

## Como executar

Pré-requisitos: `.env` configurado (credenciais AWS + `S3_BUCKET_NAME`) e a
camada Bronze já ingerida no S3.

```bash
# Camada Silver (lê Bronze, valida e grava Silver + relatórios)
python -m src.silver.pipeline

# Camada Gold (lê Silver e grava os datasets analíticos)
python -m src.gold.pipeline

# Testes de lógica (dados sintéticos, não exigem AWS)
python -m tests.test_silver_gold
```
