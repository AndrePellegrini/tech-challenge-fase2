import pandas as pd

from src.common.mappings import UF_IBGE_CODE_TO_SIGLA


def transform_atlas_uf(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trata a base do Atlas para granularidade de UF.
    """

    df = df.copy()

    df = df[df["AGREGACAO"] == "Unidade da Federação"].copy()

    df = df[
        [
            "ANO",
            "CODIGO",
            "NOME",
            "IDHM",
            "IDHM_E",
            "IDHM_R",
            "IDHM_L",
        ]
    ].copy()

    df.columns = [
        "ano",
        "codigo_uf",
        "nome_uf_atlas",
        "idhm",
        "idhm_educacao",
        "idhm_renda",
        "idhm_longevidade",
    ]

    df["codigo_uf"] = df["codigo_uf"].astype("Int64")
    df["sigla_uf"] = df["codigo_uf"].map(UF_IBGE_CODE_TO_SIGLA)

    df["ano"] = df["ano"].astype("Int64")

    return df