# Regras da Camada Silver

## Objetivo

Este documento registra as decisões arquiteturais, regras de negócio, critérios de qualidade e transformações implementadas na camada Silver.

A Silver tem como objetivo transformar os dados brutos da Bronze em dados consistentes, padronizados, validados e prontos para consumo analítico, servindo como base oficial para a construção da Gold Layer.

---

## Arquitetura orientada por metadados

A camada Silver utiliza uma arquitetura orientada por metadados.

As regras de negócio não ficam distribuídas ao longo do código do pipeline. Elas são centralizadas no arquivo:

```text
src/silver/catalog.py
```

Cada tabela possui seus metadados definidos em um único local, incluindo:

- descrição;
- chave natural;
- colunas obrigatórias;
- regras de faixa;
- colunas categóricas;
- regras de relacionamento entre tabelas.

Durante a execução da pipeline, esses metadados são consumidos automaticamente pelos módulos da Silver para:

- validar colunas obrigatórias;
- validar duplicidades;
- validar regras de faixa;
- validar integridade referencial;
- aplicar transformações padronizadas.

Essa abordagem reduz duplicação de código, facilita manutenção, melhora a governança dos dados e simplifica a inclusão de novas tabelas na arquitetura.

---

## Fluxo da camada Silver

A execução da camada Silver segue o fluxo abaixo:

```text
Bronze Layer

        ↓

Reader

        ↓

Profiling Bronze

        ↓

Quality Validation

        ↓

Transform

        ↓

Profiling Silver

        ↓

Quality Report

        ↓

Upload

        ↓

Silver Layer
```

---

## Chaves Naturais

As chaves naturais abaixo foram definidas após Data Profiling exploratório das tabelas Bronze.

| Tabela | Chave Natural | Observações |
|---------|---------------|-------------|
| alunos | ano + id_aluno | Não foram identificadas duplicidades. |
| municipio | ano + id_municipio + rede | A coluna `serie` possui apenas um valor ("2º ano"), portanto não compõe a chave. |
| uf | ano + sigla_uf + rede | A coluna `serie` possui apenas um valor ("2º ano"), portanto não compõe a chave. |
| meta_municipio | ano + id_municipio | A coluna `rede` possui apenas um valor ("Municipal"). |
| meta_uf | ano + sigla_uf | A coluna `rede` possui apenas um valor ("Pública"). |
| meta_brasil | ano | Existe apenas um registro por ano. |

---

## Regras de Qualidade

### Validações executadas

A pipeline executa automaticamente as seguintes validações:

- existência das colunas obrigatórias;
- valores nulos em colunas críticas;
- duplicidades utilizando a chave natural;
- regras de faixa;
- integridade referencial entre tabelas.

As seguintes validações são consideradas críticas e interrompem a execução da pipeline:

- colunas obrigatórias ausentes;
- valores nulos em colunas críticas;
- duplicidades na chave natural;
- violações de regras de faixa.

As verificações de integridade referencial possuem caráter informativo.

Diferenças de cobertura entre bases oficiais podem gerar registros sem correspondência e, por esse motivo, essas ocorrências são classificadas como **WARNING** e registradas no relatório consolidado de qualidade, sem interromper o processamento da pipeline.

---

### Artefatos gerados

Cada execução da Silver produz automaticamente:

- profiling da Bronze;
- profiling da Silver;
- relatório consolidado de qualidade;
- persistência dos relatórios em formato JSON.

---

## Regras por tabela

### alunos

- `ano` obrigatório;
- `id_aluno` obrigatório;
- `proficiencia ≥ 0`;
- `peso_aluno ≥ 0`.

### municipio

- chave natural: `ano + id_municipio + rede`;
- `taxa_alfabetizacao` entre 0 e 100.

### uf

- chave natural: `ano + sigla_uf + rede`;
- `taxa_alfabetizacao` entre 0 e 100.

### meta_municipio

- chave natural: `ano + id_municipio`;
- `taxa_alfabetizacao` entre 0 e 100;
- `percentual_participacao` entre 0 e 100.

### meta_uf

- chave natural: `ano + sigla_uf`;
- `taxa_alfabetizacao` entre 0 e 100;
- `percentual_participacao` entre 0 e 100.

### meta_brasil

- chave natural: `ano`;
- `taxa_alfabetizacao` entre 0 e 100;
- `percentual_participacao` entre 0 e 100.

---

## Transformações aplicadas

Durante a execução da Silver são aplicadas automaticamente as seguintes transformações:

- padronização dos nomes das colunas;
- normalização da coluna `ano`;
- remoção controlada de duplicidades;
- otimização dos tipos de dados;
- conversão de colunas categóricas para `category`;
- conversão de colunas numéricas para tipos mais eficientes (`int16` e `float32` quando aplicável).

Essas transformações são implementadas pelo módulo `transform.py`.

---

## Profiling

Cada execução gera dois relatórios independentes:

- Bronze;
- Silver.

Estrutura:

```text
reports/

    profiling/

        bronze/

        silver/
```

Esses relatórios permitem:

- auditoria;
- documentação da estrutura dos dados;
- comparação Bronze × Silver;
- rastreabilidade das transformações.

---

## Relatório de Qualidade

Além do profiling, a pipeline gera automaticamente um relatório consolidado de qualidade.

Estrutura:

```text
reports/

    quality/

        processing_date=AAAA-MM-DD/

            alunos.json

            municipio.json

            ...
```

Cada relatório contém:

- status (`OK`, `WARNING` ou `ERROR`);
- colunas obrigatórias ausentes;
- valores nulos;
- duplicidades;
- violações de regras de faixa;
- inconsistências de relacionamento.

Durante a implementação da Silver foram identificadas diferenças de cobertura entre algumas bases oficiais.

| Relacionamento | Registros sem correspondência | Status |
|----------------|------------------------------:|--------|
| alunos → municipio | 5 | WARNING |
| municipio → meta_municipio | 359 | WARNING |
| uf → meta_uf | 0 | OK |

Após investigação exploratória verificou-se que essas inconsistências não decorrem de problemas de tipo ou formatação das chaves (`id_municipio` possui mesmo tipo e tamanho em todas as tabelas), indicando que provavelmente representam diferenças de cobertura entre os datasets disponibilizados pela Base dos Dados.

Esses relacionamentos deverão ser considerados durante a implementação da Gold Layer, principalmente na definição da estratégia de joins entre metas e indicadores.

---

## Organização dos metadados

Todas as regras da Silver encontram-se centralizadas em:

```text
src/silver/catalog.py
```

O catálogo define, para cada tabela:

- descrição;
- chave natural;
- colunas obrigatórias;
- regras de faixa;
- colunas categóricas;
- regras de relacionamento.

O pipeline consulta automaticamente essas definições durante sua execução, tornando a arquitetura orientada por metadados e reduzindo o acoplamento entre os módulos.

---

## Pendências

Embora a camada Silver esteja funcional, algumas evoluções futuras foram identificadas:

- [ ] Gerar automaticamente um relatório comparativo Bronze × Silver.
- [ ] Criar um Data Catalog automático.
- [ ] Centralizar `expected_dtypes` no catálogo.
- [ ] Avaliar a permanência dos metadados `_ingestion_ts`, `_source` e `_table`.
- [ ] Implementar testes automatizados para os módulos da Silver.

---

## Histórico de Decisões

| Data | Decisão | Justificativa |
|------|----------|---------------|
| 01/07/2026 | Inclusão de `rede` na chave de `municipio`. | Eliminou falsas duplicidades identificadas durante o Data Profiling. |
| 01/07/2026 | Inclusão de `rede` na chave de `uf`. | Eliminou falsas duplicidades identificadas durante o Data Profiling. |
| 01/07/2026 | Exclusão de `serie` da chave natural. | A coluna possui apenas um valor em todas as linhas da tabela. |
| 02/07/2026 | Criação do `catalog.py`. | Centralizar metadados e eliminar duplicação de regras. |
| 02/07/2026 | Implementação do `optimize_dtypes()`. | Redução de memória e melhoria de performance. |
| 02/07/2026 | Persistência automática do profiling. | Melhorar auditoria e rastreabilidade da pipeline. |
| 02/07/2026 | Implementação da validação de integridade referencial. | Identificar diferenças de cobertura entre tabelas relacionadas sem interromper a pipeline. |
| 02/07/2026 | Criação do relatório consolidado de qualidade. | Consolidar automaticamente o resultado das validações da pipeline. |
| 02/07/2026 | Classificação das inconsistências relacionais como WARNING. | A investigação demonstrou que as diferenças representam cobertura distinta entre bases oficiais e deverão ser tratadas na Gold Layer. |

---

## Considerações finais

A camada Silver encontra-se implementada seguindo boas práticas modernas de Engenharia de Dados, incluindo arquitetura modular, separação de responsabilidades, governança baseada em metadados, validações automáticas, profiling persistido e documentação técnica.

Ela representa a camada confiável do Data Lake, reduzindo a complexidade das transformações analíticas e servindo como fonte oficial para a construção da Gold Layer.