"""
Transformações da camada Silver (Passo 3 da estratégia).

Aplica limpeza e padronização sobre os dados Bronze:
- normalização de nomes de colunas;
- conversão de tipos (ano, chaves, taxas);
- padronização de chaves (id_municipio no formato IBGE de 7 dígitos, sigla_uf
  em maiúsculas);
- remoção controlada de duplicidades;
- consolidação das três tabelas de metas em uma única estrutura analítica.
"""
import pandas as pd

# Colunas técnicas herdadas da Bronze que não pertencem ao schema Silver.
_BRONZE_METADATA = ["_ingestion_ts", "_source", "_table"]

# Colunas numéricas de proporção/nível presentes em municipio e uf.
_PROPORCAO_COLS = [f"proporcao_aluno_nivel_{i}" for i in range(9)]

# Colunas de meta por ano-alvo presentes nas tabelas meta_*.
_META_COLS = [f"meta_alfabetizacao_{ano}" for ano in range(2024, 2031)]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes de colunas (minúsculas e sem espaços nas bordas)."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _drop_bronze_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Remove as colunas técnicas de metadados herdadas da Bronze."""
    return df.drop(columns=[c for c in _BRONZE_METADATA if c in df.columns])


def _strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços em branco nas bordas de todas as colunas textuais."""
    df = df.copy()
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()
    return df


def _cast_ano(df: pd.DataFrame) -> pd.DataFrame:
    """Converte a coluna `ano` para inteiro anulável (Int64)."""
    if "ano" in df.columns:
        df = df.copy()
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    return df


def _cast_id_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza id_municipio como string de dígitos (código IBGE).

    Remove o artefato ".0" gerado quando o código é lido como número, mas NÃO
    aplica preenchimento com zeros à esquerda: códigos IBGE de município têm 7
    dígitos começando pelo código da UF (11 a 53), então nunca possuem zero
    inicial. Ids com tamanho incorreto são preservados e sinalizados na camada
    de qualidade.
    """
    if "id_municipio" in df.columns:
        df = df.copy()
        df["id_municipio"] = (
            df["id_municipio"]
            .astype("string")
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )
        df.loc[df["id_municipio"].isin(["", "nan", "<NA>", "None"]), "id_municipio"] = pd.NA
    return df


def _cast_sigla_uf(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza sigla_uf em maiúsculas e sem espaços."""
    if "sigla_uf" in df.columns:
        df = df.copy()
        df["sigla_uf"] = df["sigla_uf"].astype("string").str.strip().str.upper()
    return df


def _cast_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Converte as colunas informadas para float, tratando erros como nulo."""
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def _base_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Sequência de limpeza comum a todas as tabelas Silver."""
    df = _normalize_columns(df)
    df = _drop_bronze_metadata(df)
    df = _strip_string_columns(df)
    df = _cast_ano(df)
    df = _cast_id_municipio(df)
    df = _cast_sigla_uf(df)
    return df


def transform_alunos(df: pd.DataFrame) -> pd.DataFrame:
    """Trata a tabela de microdados de alunos."""
    df = _base_clean(df)
    df = _cast_numeric(df, ["proficiencia", "peso_aluno"])
    key = [c for c in ["ano", "id_aluno", "id_escola", "id_municipio"] if c in df.columns]
    if key:
        df = df.drop_duplicates(subset=key, keep="first")
    return df.reset_index(drop=True)


def transform_alfabetizacao_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Trata os indicadores de alfabetização por município."""
    df = _base_clean(df)
    df = _cast_numeric(df, ["taxa_alfabetizacao", "media_portugues"] + _PROPORCAO_COLS)
    key = [c for c in ["ano", "id_municipio", "rede", "serie"] if c in df.columns]
    if key:
        df = df.drop_duplicates(subset=key, keep="first")
    return df.reset_index(drop=True)


def transform_alfabetizacao_uf(df: pd.DataFrame) -> pd.DataFrame:
    """Trata os indicadores de alfabetização por UF."""
    df = _base_clean(df)
    df = _cast_numeric(df, ["taxa_alfabetizacao", "media_portugues"] + _PROPORCAO_COLS)
    key = [c for c in ["ano", "sigla_uf", "rede", "serie"] if c in df.columns]
    if key:
        df = df.drop_duplicates(subset=key, keep="first")
    return df.reset_index(drop=True)


def _prepare_meta(df: pd.DataFrame, nivel: str) -> pd.DataFrame:
    """Prepara uma tabela de metas para consolidação (formato largo)."""
    df = _base_clean(df)
    df = _cast_numeric(df, ["taxa_alfabetizacao", "percentual_participacao"] + _META_COLS)
    df = df.copy()
    df["nivel_geografico"] = nivel

    # Garante que todas as colunas de identificação existam em todos os níveis.
    # Usa dtype "string" tipado para evitar colunas all-NA sem tipo no concat.
    for column in [
        "id_municipio",
        "id_municipio_nome",
        "sigla_uf",
        "sigla_uf_nome",
        "nivel_alfabetizacao",
    ]:
        if column not in df.columns:
            df[column] = pd.Series(pd.NA, index=df.index, dtype="string")

    return df


def build_metas(
    meta_brasil: pd.DataFrame,
    meta_uf: pd.DataFrame,
    meta_municipio: pd.DataFrame,
) -> pd.DataFrame:
    """
    Consolida meta_brasil, meta_uf e meta_municipio em uma única tabela
    analítica em formato longo (uma linha por ano-alvo de meta).
    """
    frames = [
        _prepare_meta(meta_brasil, "brasil"),
        _prepare_meta(meta_uf, "uf"),
        _prepare_meta(meta_municipio, "municipio"),
    ]
    consolidado = pd.concat(frames, ignore_index=True)

    id_vars = [
        "nivel_geografico",
        "ano",
        "id_municipio",
        "id_municipio_nome",
        "sigla_uf",
        "sigla_uf_nome",
        "rede",
        "taxa_alfabetizacao",
        "percentual_participacao",
        "nivel_alfabetizacao",
    ]
    value_vars = [c for c in _META_COLS if c in consolidado.columns]

    metas_long = consolidado.melt(
        id_vars=[c for c in id_vars if c in consolidado.columns],
        value_vars=value_vars,
        var_name="ano_meta",
        value_name="meta_alfabetizacao",
    )

    # Extrai o ano-alvo do nome da coluna (meta_alfabetizacao_2024 -> 2024).
    metas_long["ano_meta"] = (
        metas_long["ano_meta"].str.extract(r"(\d{4})").astype("Int64")
    )

    # Remove linhas sem valor de meta (ano-alvo inexistente para o registro).
    metas_long = metas_long.dropna(subset=["meta_alfabetizacao"])

    return metas_long.reset_index(drop=True)
