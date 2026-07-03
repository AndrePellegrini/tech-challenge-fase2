# Regras da Camada Gold

## Objetivo

Este documento registra as decisões arquiteturais, regras de negócio e transformações implementadas na camada Gold.

A Gold tem como objetivo transformar os dados tratados e integrados da Silver em **datasets analíticos** prontos para consumo direto por dashboards, análises estatísticas e modelos de machine learning, sem exigir joins ou tratamentos adicionais de quem consome.

---

## Arquitetura orientada por catálogo

Seguindo o mesmo padrão orientado por metadados da camada Silver, a Gold centraliza a definição dos datasets no arquivo:

```text
src/gold/catalog.py
```

Cada dataset possui seus metadados definidos em um único local, incluindo:

- descrição;
- tabelas Silver de origem (`sources`);
- função de construção (`builder`).

Durante a execução, a pipeline consulta o catálogo para:

- ler automaticamente as tabelas Silver de origem de cada dataset;
- aplicar a função de construção correspondente;
- gerar o profiling do resultado;
- gravar o dataset na camada Gold.

Essa abordagem garante rastreabilidade da linhagem dos dados (as fontes de cada dataset são declaradas explicitamente) e permite incluir novos datasets sem alterar o código da pipeline.

---

## Fluxo da camada Gold

```text
Silver Layer
    (tabelas base e integradas)

        ↓

Reader
    (remoção dos metadados técnicos)

        ↓

Builder
    (transformações analíticas por dataset)

        ↓

Profiling Gold

        ↓

Upload

        ↓

Gold Layer
```

---

## Módulos (`src/gold/`)

| Módulo | Responsabilidade |
|---|---|
| `catalog.py` | Catálogo de datasets: descrição, fontes Silver e builder |
| `reader.py` | Leitura das tabelas Silver, removendo metadados técnicos (colunas `_*`) |
| `transform.py` | Funções de construção (builders) dos datasets analíticos |
| `upload.py` | Metadados técnicos da Gold e gravação no S3 |
| `pipeline.py` | Orquestra leitura, construção, profiling e gravação |

---

## Datasets analíticos

### indicador_alfabetizacao_municipio

Indicador de alfabetização por município, rede e série.

- **Fonte:** `municipio`
- **Granularidade:** ano + id_municipio + rede
- **Colunas:** `ano`, `id_municipio`, `id_municipio_nome`, `serie`, `rede`, `taxa_alfabetizacao`, `media_portugues`, `proporcao_aluno_nivel_0` a `proporcao_aluno_nivel_8`
- **Uso:** dashboards de desempenho municipal, mapas coropléticos, features territoriais para modelos.

---

### comparativo_metas_resultados

Comparação entre a taxa de alfabetização realizada e as metas oficiais por ano-alvo (2024 a 2030), consolidando os níveis município, UF e Brasil em um único dataset de formato longo.

- **Fontes:** `municipio_integrado`, `uf_integrado`, `meta_brasil`
- **Granularidade:** nivel_geografico + localidade + rede + ano (base) + ano_meta
- **Colunas:** `nivel_geografico` (`municipio` | `uf` | `brasil`), `ano`, `id_municipio`, `id_municipio_nome`, `sigla_uf`, `sigla_uf_nome`, `rede`, `taxa_alfabetizacao`, `ano_meta`, `meta_alfabetizacao`, `gap_para_meta`, `atingiu_meta`

Campos derivados:

| Campo | Regra |
|---|---|
| `ano_meta` | Extraído do nome da coluna larga (`meta_alfabetizacao_2024` → `2024`) |
| `meta_alfabetizacao` | Valor da meta para o ano-alvo (formato longo via *melt*) |
| `gap_para_meta` | `meta_alfabetizacao - taxa_alfabetizacao` (positivo = faltam pontos para a meta) |
| `atingiu_meta` | `taxa_alfabetizacao >= meta_alfabetizacao` |

- **Uso:** acompanhamento do atingimento das metas do INEP, priorização de localidades com maior `gap_para_meta`.

---

### evolucao_temporal_indicador

Evolução da taxa de alfabetização realizada ao longo dos anos, por nível geográfico.

- **Fontes:** `municipio`, `uf`, `meta_brasil`
- **Granularidade:** nivel_geografico + localidade + rede + ano (uma linha por localidade/rede/ano)
- **Colunas:** `nivel_geografico`, `ano`, `id_municipio`, `id_municipio_nome`, `sigla_uf`, `sigla_uf_nome`, `rede`, `serie`, `taxa_alfabetizacao`
- **Uso:** séries temporais, análise de tendência e sazonalidade, base para modelos de previsão.

No nível Brasil, a taxa realizada nacional é obtida da tabela `meta_brasil`, que registra a taxa observada no ano-base junto das metas.

---

### desempenho_alunos_municipio

Desempenho agregado dos alunos avaliados, por ano, município e rede, calculado a partir da base individual integrada.

- **Fonte:** `alunos_integrado`
- **Granularidade:** ano + id_municipio + rede
- **Colunas:** `ano`, `id_municipio`, `id_municipio_nome`, `rede`, `total_alunos`, `pct_alfabetizados`, `taxa_alfabetizacao_municipio`, `proficiencia_media_ponderada`

Campos derivados:

| Campo | Regra |
|---|---|
| `total_alunos` | Contagem de `id_aluno` no grupo |
| `proficiencia_media_ponderada` | `Σ(proficiencia × peso_aluno) / Σ(peso_aluno)` — respeita o desenho amostral da avaliação |
| `pct_alfabetizados` | Percentual de alunos com `alfabetizado = "Sim"` |
| `taxa_alfabetizacao_municipio` | Taxa oficial do município/rede, trazida pela integração da Silver |

- **Uso:** confronto entre o microdado (alunos) e o indicador oficial (município), análise de consistência e estudos de equidade por rede.

---

## Decisões de modelagem

### Metas em formato longo

Na origem, as metas chegam em formato largo (uma coluna por ano-alvo: `meta_alfabetizacao_2024` ... `meta_alfabetizacao_2030`). A Gold converte para formato longo (`ano_meta` + `meta_alfabetizacao`), porque:

- dashboards e modelos consomem naturalmente uma linha por ano-alvo;
- evita que consumidores repitam a lógica de *unpivot*;
- novas colunas de meta (ex.: 2031) são absorvidas automaticamente pelo padrão de nome, sem alteração de código.

### Uso das tabelas integradas da Silver

O comparativo de metas usa `municipio_integrado` e `uf_integrado` (e não joins refeitos na Gold), mantendo a Silver como fonte única da lógica de integração. As colunas conflitantes do lado das metas chegam com sufixo `_ref` e não são propagadas para a Gold — a taxa realizada considerada é sempre a da tabela de indicadores (`municipio`/`uf`).

### Tratamento dos WARNINGs de relacionamento da Silver

O quality report da Silver identificou registros sem correspondência entre bases (ex.: `municipio → meta_municipio` com 359 ocorrências), classificados como WARNING por representarem diferença de cobertura entre bases oficiais. Na Gold, o tratamento é:

- a integração da Silver usa **left join**, então esses registros chegam com metas nulas;
- no `comparativo_metas_resultados`, linhas sem meta são **descartadas** após o *melt* (`dropna` em `meta_alfabetizacao`) — não faz sentido comparar contra meta inexistente;
- os mesmos municípios **permanecem** em `indicador_alfabetizacao_municipio` e `evolucao_temporal_indicador`, que não dependem de meta.

Ou seja: nenhum dado é perdido — apenas o dataset de comparação se restringe às localidades que possuem meta definida.

### Remoção dos metadados técnicos na leitura

O reader da Gold remove todas as colunas iniciadas por `_` (`_processed_ts`, `_layer`, `_table` e suas variantes `_ref` das tabelas integradas), garantindo que os builders trabalhem apenas com colunas de negócio.

---

## Metadados técnicos e gravação

Cada dataset recebe, no momento da gravação:

- `_processed_ts` — timestamp UTC do processamento;
- `_layer` = `"gold"`;
- `_table` — nome do dataset.

Estrutura no S3 (mesmo padrão de particionamento da Silver):

```text
gold/

    indicador_alfabetizacao_municipio/
        processing_date=AAAA-MM-DD/

    comparativo_metas_resultados/
        processing_date=AAAA-MM-DD/

    evolucao_temporal_indicador/
        processing_date=AAAA-MM-DD/

    desempenho_alunos_municipio/
        processing_date=AAAA-MM-DD/
```

---

## Profiling

Cada execução gera o profiling de todos os datasets produzidos, no mesmo formato das demais camadas:

```text
reports/

    profiling/

        gold/

            processing_date=AAAA-MM-DD/

                indicador_alfabetizacao_municipio.json

                ...
```

---

## Como executar

Pré-requisitos: `.env` configurado (credenciais AWS + `S3_BUCKET_NAME`) e a Silver já processada no S3 (incluindo as tabelas integradas).

```bash
python -m src.gold.pipeline
```

A pipeline processa todos os datasets do catálogo, registra sucesso/falha por dataset e encerra com `RuntimeError` caso algum falhe, facilitando alertas em orquestradores.

---

## Testes

A lógica dos builders é coberta por testes com dados sintéticos no formato produzido pela Silver, sem dependência de AWS:

```bash
python -m tests.test_silver_gold
```

Cobrem: seleção e ordenação do indicador, *melt* das metas com descarte de metas nulas, cálculo de `gap_para_meta`/`atingiu_meta` nos três níveis, contagem da evolução temporal e agregação ponderada do desempenho dos alunos.

---

## Aplicação em IA

Os datasets foram desenhados para viabilizar:

- **modelos de predição** da `taxa_alfabetizacao` por município (features territoriais do indicador + histórico da evolução temporal);
- **clusters de vulnerabilidade educacional**, agrupando municípios por desempenho e distância até a meta (`gap_para_meta`);
- **priorização de políticas públicas**, ordenando localidades por gap e percentual de alfabetizados;
- **análises de consistência amostral**, comparando a proficiência ponderada dos alunos com o indicador oficial do município.

---

## Histórico de Decisões

| Data | Decisão | Justificativa |
|------|----------|---------------|
| 03/07/2026 | Criação do `catalog.py` da Gold. | Manter o mesmo padrão orientado por metadados da Silver e dar rastreabilidade à linhagem dos datasets. |
| 03/07/2026 | Consumo das tabelas integradas da Silver no comparativo. | Evitar joins duplicados e manter a Silver como fonte única da lógica de integração. |
| 03/07/2026 | Conversão das metas para formato longo. | Facilitar consumo analítico e absorver novos anos-alvo sem alteração de código. |
| 03/07/2026 | Descarte de linhas sem meta no comparativo (pós-melt). | Tratamento dos WARNINGs de cobertura identificados na Silver; localidades sem meta permanecem nos demais datasets. |
| 03/07/2026 | Proficiência média ponderada por `peso_aluno`. | Respeitar o desenho amostral da avaliação do INEP na agregação dos microdados. |
| 03/07/2026 | Remoção de colunas `_*` na leitura da Silver. | Isolar os builders das colunas técnicas e dos sufixos `_ref` das integrações. |

---

## Considerações finais

A camada Gold completa a arquitetura medalhão do projeto: consome exclusivamente a Silver oficial (tabelas base e integradas), aplica as transformações analíticas de forma declarativa via catálogo e disponibiliza datasets prontos para exploração, dashboards e machine learning, com profiling persistido e o mesmo padrão de metadados e particionamento das demais camadas.
