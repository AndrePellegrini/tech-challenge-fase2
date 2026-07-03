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