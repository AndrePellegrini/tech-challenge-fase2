# Tech Challenge Fase 2 - Pipeline de Dados para Avaliação da Alfabetização no Brasil

## Objetivo

Construir uma plataforma de dados para análise exploratória dos dados de alfabetização do Brasil utilizando arquitetura Lakehouse na AWS.

O projeto contempla:

- Ingestão Batch de dados públicos da Base dos Dados (BigQuery)
- Armazenamento em Data Lake (Amazon S3)
- Tratamento em arquitetura medalhão (Bronze, Silver e Gold)
- Streaming de dados utilizando Apache Kafka
- Disponibilização dos dados para análise exploratória e tomada de decisão

---

## Dataset

Fonte:

https://basedosdados.org/dataset/073a39d4-89cf-4068-b1e8-34ed0d9c0b72

Base:

Avaliação da Alfabetização - INEP

Tabelas utilizadas:

- alunos
- municipio
- uf
- meta_alfabetizacao_municipio
- meta_alfabetizacao_uf
- meta_alfabetizacao_brasil

---

## Arquitetura

```text
Base dos Dados
      ↓
  BigQuery
      ↓
    Python
      ↓
 Amazon S3 (Bronze)
      ↓
    Silver
      ↓
     Gold
      ↓
Análise Exploratória
```

---

## Estrutura do Projeto

```text
tech-challenge-fase2/
│
├── docs/
├── src/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── streaming/
│   └── quality/
├── notebooks/
├── tmp/
├── .env
├── .gitignore
├── .python-version
├── requirements.txt
└── README.md
```

---

## Tecnologias Utilizadas

- Python
- Pandas
- PyArrow
- Boto3
- Base dos Dados
- Google BigQuery
- Amazon S3
- Apache Kafka
- Git
- GitHub

---

# Configuração do Ambiente

## Pré-requisitos

- Git
- Python (versão definida em `.python-version`)

## Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd tech-challenge-fase2
```

## Criar o ambiente virtual

```bash
python -m venv .venv
```

## Ativar o ambiente virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## Instalar as dependências

```bash
pip install -r requirements.txt
```

## Verificar a instalação

```bash
python --version
pip list
```

---

## Decisões Técnicas

### Amazon S3

Escolhido por possuir:

- alta durabilidade
- baixo custo
- escalabilidade praticamente ilimitada
- integração nativa com Glue e Athena

---

### Formato Parquet

Escolhido por:

- armazenamento colunar
- menor espaço em disco
- consultas mais rápidas
- menor custo em motores analíticos

---

### Ingestão via Base dos Dados + BigQuery

Escolhido por:

- evitar extrações manuais em CSV
- processo reproduzível
- pipeline automatizável
- arquitetura mais próxima de ambientes corporativos

---

### Arquitetura Modular

O projeto foi dividido em módulos:

- config
- queries
- extract
- upload
- pipeline

Objetivos:

- separação de responsabilidades
- menor acoplamento
- maior manutenibilidade
- facilidade para testes e trabalho em equipe

---

### Camada Silver orientada por metadados

A camada Silver utiliza um catálogo centralizado localizado em `src/silver/catalog.py`.

Esse catálogo concentra as regras de negócio de cada tabela, incluindo:

- descrição;
- chave natural;
- colunas obrigatórias;
- regras de validação;
- colunas categóricas.

O pipeline utiliza essas informações para executar automaticamente as validações e transformações da camada Silver, reduzindo duplicação de código, facilitando manutenção e simplificando a inclusão de novas tabelas.

---

## Metadados de Ingestão

As tabelas Bronze recebem os seguintes metadados:

- `_ingestion_ts`
- `_source`
- `_table`

Objetivos:

- rastreabilidade
- auditoria
- governança de dados
- reprocessamento

---

# Como Contribuir

Para manter a organização do projeto, todas as alterações devem seguir o fluxo de versionamento abaixo.

## 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd tech-challenge-fase2
```

## 2. Atualizar a branch develop

```bash
git checkout develop
git pull
```

## 3. Criar uma branch de desenvolvimento

Utilize o padrão:

```text
feature/nome-da-feature
```

Exemplo:

```bash
git checkout -b feature/silver-layer
```

## 4. Desenvolver a funcionalidade

Implemente e teste sua alteração localmente.

## 5. Registrar as alterações

```bash
git add .
git commit -m "feat: implementação da camada Silver"
```

## 6. Enviar para o GitHub

```bash
git push -u origin feature/silver-layer
```

## 7. Abrir um Pull Request

Após concluir a implementação, abra um Pull Request para a branch `develop` para revisão e integração ao projeto.

---

## Status do Projeto

- ✅ Fase 1 - Setup e Ingestão Bronze concluída
- 🔄 Fase 2 - Construção da camada Silver
- ⬜ Fase 3 - Camada Gold
- ⬜ Fase 4 - Streaming Kafka
- ⬜ Fase 5 - Análise Exploratória e Apresentação