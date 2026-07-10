# Catálogo de Dados

## alunos

Descrição:
Informações individuais dos alunos avaliados.

Chave:
id_aluno

Principais campos:

- ano
- id_municipio
- id_escola
- proficiencia
- alfabetizado
- peso_aluno

---

## municipio

Descrição:
Indicadores de alfabetização por município.

Chave:
id_municipio

Campos:

- ano
- taxa_alfabetizacao
- media_portugues
- serie
- rede

---

## uf

Descrição:
Indicadores de alfabetização por estado.

Chave:
sigla_uf

Campos:

- ano
- taxa_alfabetizacao
- media_portugues
- serie
- rede

---

## meta_municipio

Descrição:
Metas de alfabetização por município.

Chave:
id_municipio

---

## meta_uf

Descrição:
Metas de alfabetização por UF.

Chave:
sigla_uf

---

## meta_brasil

Descrição:
Metas nacionais de alfabetização.

---

## Tabelas Silver integradas

- **alunos_integrado** — alunos + indicadores do município (join em ano, id_municipio, rede)
- **municipio_integrado** — município + metas municipais (join em ano, id_municipio)
- **uf_integrado** — UF + metas estaduais (join em ano, sigla_uf)

---

## Datasets Gold

### indicador_alfabetizacao_municipio

Indicador de alfabetização por município, rede e série.

Fonte: municipio

### comparativo_metas_resultados

Taxa realizada vs. metas 2024-2030 em formato longo, nos níveis município, UF e Brasil.

Campos derivados: ano_meta, meta_alfabetizacao, gap_para_meta, atingiu_meta

Fontes: municipio_integrado, uf_integrado, meta_brasil

### evolucao_temporal_indicador

Evolução da taxa de alfabetização ao longo dos anos, por nível geográfico.

Fontes: municipio, uf, meta_brasil

### desempenho_alunos_municipio

Desempenho agregado dos alunos por município e rede.

Campos derivados: total_alunos, proficiencia_media_ponderada, pct_alfabetizados, taxa_alfabetizacao_municipio

Fonte: alunos_integrado

---

## Eventos de Streaming

### alunos_eventos (tópico Kafka: alfabetizacao.alunos.eventos)

Eventos de avaliação de alunos ingeridos via Kafka, gravados em streaming/alunos_eventos/.

Campos: id_evento, ts_evento, ano, id_municipio, id_municipio_nome, sigla_uf, id_escola, id_aluno, serie, rede, presenca, preenchimento_caderno, alfabetizado, proficiencia, peso_aluno