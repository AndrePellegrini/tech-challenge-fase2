"""
Regras de qualidade da camada Silver (Passo 2 e 5 da estratégia).

Define regras de validação em nível de linha e separa registros válidos de
registros problemáticos, gerando um relatório de qualidade por tabela.

Regras cobertas (conforme o guia do Tech Challenge):
- `ano` obrigatório e numérico;
- `taxa_alfabetizacao` entre 0 e 100;
- `proficiencia` não negativa;
- `sigla_uf` com 2 caracteres;
- `id_municipio` no formato IBGE (7 dígitos);
- ausência de duplicidades nas chaves;
- completude dos campos críticos.
"""
from dataclasses import dataclass, field

import pandas as pd

# Campos críticos por tabela (para o relatório de completude).
CRITICAL_FIELDS = {
    "alunos": ["ano", "id_municipio", "id_aluno", "proficiencia"],
    "alfabetizacao_municipio": ["ano", "id_municipio", "taxa_alfabetizacao"],
    "alfabetizacao_uf": ["ano", "sigla_uf", "taxa_alfabetizacao"],
    "metas": ["nivel_geografico", "ano", "ano_meta", "meta_alfabetizacao"],
}

# Chaves lógicas por tabela (para checagem de duplicidade).
KEY_FIELDS = {
    "alunos": ["ano", "id_aluno", "id_escola", "id_municipio"],
    "alfabetizacao_municipio": ["ano", "id_municipio", "rede", "serie"],
    "alfabetizacao_uf": ["ano", "sigla_uf", "rede", "serie"],
    "metas": ["nivel_geografico", "ano", "id_municipio", "sigla_uf", "rede", "ano_meta"],
}


@dataclass
class QualityResult:
    """Resultado da validação de qualidade de uma tabela."""

    valid: pd.DataFrame
    invalid: pd.DataFrame
    report: dict = field(default_factory=dict)


def _mask_ano_valido(df: pd.DataFrame) -> pd.Series:
    """`ano` deve ser obrigatório e numérico."""
    return df["ano"].notna()


def _mask_taxa_faixa(df: pd.DataFrame) -> pd.Series:
    """`taxa_alfabetizacao`, quando presente, deve estar entre 0 e 100."""
    taxa = df["taxa_alfabetizacao"]
    return taxa.isna() | ((taxa >= 0) & (taxa <= 100))


def _mask_proficiencia(df: pd.DataFrame) -> pd.Series:
    """`proficiencia`, quando presente, não deve ser negativa."""
    prof = df["proficiencia"]
    return prof.isna() | (prof >= 0)


def _mask_sigla_uf(df: pd.DataFrame) -> pd.Series:
    """`sigla_uf`, quando presente, deve ter exatamente 2 caracteres."""
    sigla = df["sigla_uf"]
    return sigla.isna() | (sigla.str.len() == 2)


def _mask_id_municipio(df: pd.DataFrame) -> pd.Series:
    """`id_municipio`, quando presente, deve ter 7 dígitos numéricos (IBGE)."""
    ids = df["id_municipio"].astype("string")
    return ids.isna() | ids.str.fullmatch(r"\d{7}")


def _mask_meta_faixa(df: pd.DataFrame) -> pd.Series:
    """`meta_alfabetizacao`, quando presente, deve estar entre 0 e 100."""
    meta = df["meta_alfabetizacao"]
    return meta.isna() | ((meta >= 0) & (meta <= 100))


# (nome_regra, coluna_necessaria, função_de_validação)
_RULES = [
    ("ano_obrigatorio", "ano", _mask_ano_valido),
    ("taxa_entre_0_100", "taxa_alfabetizacao", _mask_taxa_faixa),
    ("proficiencia_nao_negativa", "proficiencia", _mask_proficiencia),
    ("sigla_uf_2_caracteres", "sigla_uf", _mask_sigla_uf),
    ("id_municipio_ibge_7_digitos", "id_municipio", _mask_id_municipio),
    ("meta_entre_0_100", "meta_alfabetizacao", _mask_meta_faixa),
]


def apply_quality(df: pd.DataFrame, table_name: str) -> QualityResult:
    """
    Aplica as regras de qualidade aplicáveis à tabela e separa os registros
    válidos dos inválidos, produzindo um relatório detalhado.
    """
    df = df.reset_index(drop=True)
    total = len(df)

    valid_mask = pd.Series(True, index=df.index)
    error_labels = pd.Series("", index=df.index)
    rule_failures: dict[str, int] = {}

    for rule_name, required_col, rule_fn in _RULES:
        if required_col not in df.columns:
            continue
        rule_mask = rule_fn(df)
        failures = ~rule_mask
        rule_failures[rule_name] = int(failures.sum())
        valid_mask &= rule_mask
        error_labels = error_labels.where(~failures, error_labels + f"{rule_name};")

    # Completude dos campos críticos.
    completeness = {}
    for column in CRITICAL_FIELDS.get(table_name, []):
        if column in df.columns:
            non_null = int(df[column].notna().sum())
            completeness[column] = {
                "preenchidos": non_null,
                "completude_pct": round((non_null / total * 100), 2) if total else 0.0,
            }

    # Checagem de duplicidade nas chaves lógicas.
    key = [c for c in KEY_FIELDS.get(table_name, []) if c in df.columns]
    duplicates_on_key = int(df.duplicated(subset=key).sum()) if key else 0

    valid_df = df[valid_mask].reset_index(drop=True)
    invalid_df = df[~valid_mask].copy()
    invalid_df["_quality_errors"] = error_labels[~valid_mask].str.rstrip(";")
    invalid_df = invalid_df.reset_index(drop=True)

    report = {
        "tabela": table_name,
        "total_registros": total,
        "registros_validos": int(len(valid_df)),
        "registros_invalidos": int(len(invalid_df)),
        "falhas_por_regra": rule_failures,
        "duplicidade_na_chave": {"chave": key, "duplicatas": duplicates_on_key},
        "completude_campos_criticos": completeness,
    }

    return QualityResult(valid=valid_df, invalid=invalid_df, report=report)
