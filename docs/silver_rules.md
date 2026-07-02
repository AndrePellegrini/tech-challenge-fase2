# Regras da Camada Silver

## Objetivo

Este documento registra as regras de negócio, decisões técnicas e critérios de qualidade adotados na construção da camada Silver.

A Silver tem como objetivo transformar os dados brutos da Bronze em dados consistentes, padronizados, validados e prontos para consumo analítico.

---

## Arquitetura orientada por metadados

A camada Silver utiliza uma arquitetura orientada por metadados.

As regras de negócio não ficam distribuídas pelo código do pipeline. Elas são centralizadas no arquivo `src/silver/catalog.py`.

Cada tabela possui seus metadados definidos em um único local, incluindo:

- descrição;
- chave natural;
- colunas obrigatórias;
- regras de validação;
- colunas categóricas.

Esses metadados são utilizados automaticamente pelo pipeline para:

- validar duplicidades;
- validar colunas obrigatórias;
- validar faixas de valores;
- aplicar transformações padronizadas.

Essa abordagem reduz duplicação de código, facilita manutenção e torna a inclusão de novas tabelas mais simples.

---

## Chaves Naturais

As chaves abaixo foram definidas após análise exploratória das tabelas Bronze.

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

### Validações obrigatórias

As seguintes validações são executadas automaticamente durante a pipeline da Silver:

- existência das colunas obrigatórias;
- validação de valores nulos nas colunas críticas;
- validação de duplicidades utilizando a chave natural;
- validação de regras de faixa;
- geração de profiling da Bronze;
- geração de profiling da Silver;
- persistência dos relatórios de profiling em JSON.

---

### Regras por tabela

#### alunos

- `ano` obrigatório;
- `id_aluno` obrigatório;
- `proficiencia` deve ser maior ou igual a zero;
- `peso_aluno` deve ser maior ou igual a zero.

#### municipio

- `ano`, `id_municipio` e `rede` compõem a chave natural;
- `taxa_alfabetizacao` deve permanecer entre 0 e 100.

#### uf

- `ano`, `sigla_uf` e `rede` compõem a chave natural;
- `taxa_alfabetizacao` deve permanecer entre 0 e 100.

#### meta_municipio

- `ano` e `id_municipio` compõem a chave natural;
- `taxa_alfabetizacao` entre 0 e 100;
- `percentual_participacao` entre 0 e 100.

#### meta_uf

- `ano` e `sigla_uf` compõem a chave natural;
- `taxa_alfabetizacao` entre 0 e 100;
- `percentual_participacao` entre 0 e 100.

#### meta_brasil

- `ano` é a chave natural;
- `taxa_alfabetizacao` entre 0 e 100;
- `percentual_participacao` entre 0 e 100.

---

## Transformações aplicadas

Durante a construção da Silver são executadas as seguintes transformações:

- padronização dos nomes das colunas;
- normalização da coluna `ano`;
- remoção controlada de duplicidades;
- otimização dos tipos de dados;
- conversão de colunas categóricas para `category`;
- conversão de colunas numéricas para tipos mais eficientes.

Essas transformações são executadas pelo módulo `transform.py`.

---

## Profiling

Cada execução da Silver gera automaticamente dois perfis:

- Bronze;
- Silver.

Os relatórios são armazenados em:

```text
reports/

profiling/

    bronze/

    silver/
```

Esses relatórios permitem:

- auditoria;
- comparação Bronze × Silver;
- documentação da qualidade dos dados;
- rastreabilidade das transformações.

---

## Organização dos metadados

Todas as regras da Silver são centralizadas em:

```text
src/silver/catalog.py
```

Esse arquivo contém:

- descrição das tabelas;
- chaves naturais;
- colunas obrigatórias;
- regras de faixa;
- colunas categóricas.

O pipeline utiliza essas informações automaticamente durante a execução.

---

## Pendências

Embora a Silver esteja funcional, algumas melhorias podem ser implementadas futuramente:

- [ ] Gerar automaticamente um relatório comparando Bronze × Silver.
- [ ] Criar um Data Catalog automático.
- [ ] Centralizar os tipos esperados (`expected_dtypes`) no catálogo.
- [ ] Avaliar a permanência dos metadados `_ingestion_ts`, `_source` e `_table` na Silver.
- [ ] Adicionar testes automatizados para os módulos da Silver.

---

## Histórico de Decisões

| Data | Decisão | Justificativa |
|------|----------|---------------|
| 01/07/2026 | Inclusão de `rede` na chave de `municipio`. | Eliminou falsas duplicidades observadas durante o profiling. |
| 01/07/2026 | Inclusão de `rede` na chave de `uf`. | Eliminou falsas duplicidades observadas durante o profiling. |
| 01/07/2026 | Exclusão de `serie` da chave natural. | A coluna possui apenas um valor em todas as linhas da tabela. |
| 02/07/2026 | Criação do `catalog.py`. | Centralizar metadados e eliminar duplicação de regras. |
| 02/07/2026 | Implementação do `optimize_dtypes()`. | Redução de memória e melhoria de performance. |
| 02/07/2026 | Persistência do profiling em JSON. | Melhorar auditoria e rastreabilidade da pipeline. |

---

## Considerações finais

A camada Silver encontra-se implementada seguindo princípios de Engenharia de Dados modernos, com separação clara de responsabilidades, arquitetura orientada por metadados, validações automáticas e documentação técnica.

Ela representa a camada confiável do Data Lake e serve como fonte oficial para a construção da Gold Layer.