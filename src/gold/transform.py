"""
Construção dos datasets analíticos da camada Gold.

Cada builder recebe um dicionário {nome_da_tabela_silver: DataFrame} com as
fontes declaradas no GOLD_CATALOG e devolve um DataFrame pronto para consumo
analítico (dashboards, estatística e machine learning).
"""
import pandas as pd

META_COLUMN_PREFIX = "meta_alfabetizacao_"


def _melt_metas(df: pd.DataFrame, id_vars: list[str]) -> pd.DataFrame:
    """
    Converte as colunas de meta em formato largo (meta_alfabetizacao_2024,
    ..., meta_alfabetizacao_2030) para formato longo (ano_meta,
    meta_alfabetizacao).
    """

    meta_columns = [
        col for col in df.columns
        if col.startswith(META_COLUMN_PREFIX) and col[len(META_COLUMN_PREFIX):].isdigit()
    ]

    existing_id_vars = [col for col in id_vars if col in df.columns]

    melted = df.melt(
        id_vars = existing_id_vars,
        value_vars = meta_columns,
        var_name = "ano_meta",
        value_name = "meta_alfabetizacao",
    )

    melted["ano_meta"] = (
        melted["ano_meta"].str.removeprefix(META_COLUMN_PREFIX).astype("int16")
    )

    return melted.dropna(subset=["meta_alfabetizacao"])


def _comparativo_por_nivel(
        df: pd.DataFrame,
        nivel_geografico: str,
        location_columns: list[str],
        extra_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Gera o comparativo metas x resultados de um nível geográfico.

    Espera um DataFrame com a taxa realizada em `taxa_alfabetizacao` e as
    metas em formato largo (colunas meta_alfabetizacao_<ano>).
    """
    if extra_columns is None:
        extra_columns = []

    id_vars = ["ano", *location_columns, "rede", "taxa_alfabetizacao", *extra_columns,]

    comparativo = _melt_metas(df, id_vars=id_vars)
    comparativo.insert(0, "nivel_geografico", nivel_geografico)

    comparativo["gap_para_meta"] = (
        comparativo["meta_alfabetizacao"] - comparativo["taxa_alfabetizacao"]
    ).astype(float).round(4)

    comparativo["atingiu_meta"] = (
        comparativo["taxa_alfabetizacao"] >= comparativo["meta_alfabetizacao"]
    )

    return comparativo


def build_indicador_municipio(sources: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Indicador de alfabetização por município, rede e série.
    """

    df = sources["municipio"]

    columns = [
        "ano",
        "id_municipio",
        "id_municipio_nome",
        "serie",
        "rede",
        "taxa_alfabetizacao",
        "media_portugues",
        *[f"proporcao_aluno_nivel_{level}" for level in range(9)],
    ]

    df = df[[col for col in columns if col in df.columns]].copy()

    sort_columns = [
        col for col in ["id_municipio", "ano", "rede", "serie"] if col in df.columns
    ]

    return df.sort_values(sort_columns).reset_index(drop=True)


def build_comparativo_metas_resultados(
        sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Compara a taxa de alfabetização realizada com as metas por ano-alvo,
    consolidando os níveis município, UF e Brasil em formato longo.

    Nos níveis município e UF utiliza as tabelas integradas da Silver, nas
    quais as metas já estão associadas à localidade correspondente.
    """

    municipio = _comparativo_por_nivel(
        sources["municipio_integrado"],
        nivel_geografico = "municipio",
        location_columns = ["id_municipio", "id_municipio_nome"],
    )

    uf = _comparativo_por_nivel(
        sources["uf_integrado"],
        nivel_geografico = "uf",
        location_columns = ["sigla_uf", "sigla_uf_nome"],
        extra_columns = [
            "idhm",
            "idhm_educacao",
            "idhm_renda",
            "idhm_longevidade",
        ],
    )

    brasil = _comparativo_por_nivel(
        sources["meta_brasil"],
        nivel_geografico = "brasil",
        location_columns = [],
    )

    comparativo = pd.concat([municipio, uf, brasil], ignore_index=True)

    sort_columns = [
        col
        for col in ["nivel_geografico", "sigla_uf", "id_municipio", "ano", "ano_meta"]
        if col in comparativo.columns
    ]

    return comparativo.sort_values(sort_columns).reset_index(drop=True)


def build_evolucao_temporal(sources: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Evolução da taxa de alfabetização realizada ao longo dos anos, por nível
    geográfico (município, UF e Brasil).
    """

    levels = [
        ("municipio", sources["municipio"], ["id_municipio", "id_municipio_nome"]),
        ("uf", sources["uf"], ["sigla_uf", "sigla_uf_nome"]),
        ("brasil", sources["meta_brasil"], []),
    ]

    frames = []

    for nivel_geografico, df, location_columns in levels:
        columns = ["ano", *location_columns, "rede", "serie", "taxa_alfabetizacao"]

        frame = df[[col for col in columns if col in df.columns]].copy()
        frame = frame.dropna(subset=["taxa_alfabetizacao"]).drop_duplicates()
        frame.insert(0, "nivel_geografico", nivel_geografico)

        frames.append(frame)

    evolucao = pd.concat(frames, ignore_index=True)

    sort_columns = [
        col
        for col in ["nivel_geografico", "sigla_uf", "id_municipio", "rede", "ano"]
        if col in evolucao.columns
    ]

    return evolucao.sort_values(sort_columns).reset_index(drop=True)


def build_desempenho_alunos_municipio(
        sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Agrega o desempenho dos alunos por ano, município e rede a partir da
    tabela integrada de alunos: total de alunos avaliados, proficiência média
    ponderada pelo peso amostral e percentual de alfabetizados, junto da taxa
    de alfabetização municipal de referência.
    """

    df = sources["alunos_integrado"].copy()

    group_columns = [
        col
        for col in ["ano", "id_municipio", "id_municipio_nome", "rede"]
        if col in df.columns
    ]

    if "peso_aluno" in df.columns:
        df["_proficiencia_ponderada"] = df["proficiencia"] * df["peso_aluno"]
    else:
        df["peso_aluno"] = 1.0
        df["_proficiencia_ponderada"] = df["proficiencia"]

    df["_alfabetizado"] = df["alfabetizado"].astype("string").str.lower() == "sim"

    grouped = df.groupby(group_columns, observed=True, dropna=False)

    desempenho = grouped.agg(
        total_alunos = ("id_aluno", "count"),
        soma_proficiencia_ponderada = ("_proficiencia_ponderada", "sum"),
        soma_pesos = ("peso_aluno", "sum"),
        pct_alfabetizados = ("_alfabetizado", "mean"),
        taxa_alfabetizacao_municipio = ("taxa_alfabetizacao", "first"),
    ).reset_index()

    desempenho["proficiencia_media_ponderada"] = (
        desempenho["soma_proficiencia_ponderada"] / desempenho["soma_pesos"]
    ).astype(float).round(4)

    desempenho["pct_alfabetizados"] = (
        desempenho["pct_alfabetizados"].astype(float) * 100
    ).round(4)

    desempenho = desempenho.drop(
        columns = ["soma_proficiencia_ponderada", "soma_pesos"]
    )

    return desempenho.sort_values(group_columns).reset_index(drop = True)


GOLD_BUILDERS = {
    "build_indicador_municipio": build_indicador_municipio,
    "build_comparativo_metas_resultados": build_comparativo_metas_resultados,
    "build_evolucao_temporal": build_evolucao_temporal,
    "build_desempenho_alunos_municipio": build_desempenho_alunos_municipio,
}
