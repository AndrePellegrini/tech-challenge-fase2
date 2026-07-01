"""
Construção dos datasets analíticos da camada Gold.

Gera tabelas prontas para dashboards, análises estatísticas e modelos de ML:
- indicador de alfabetização por município;
- comparação entre metas e resultados (distância até a meta);
- evolução temporal do indicador.
"""
import pandas as pd


def build_indicador_municipio(silver_municipio: pd.DataFrame) -> pd.DataFrame:
    """
    Indicador de alfabetização por município, pronto para consumo analítico.

    Seleciona as colunas de negócio e ordena por localidade e ano.
    """
    colunas = [
        "ano",
        "id_municipio",
        "id_municipio_nome",
        "rede",
        "serie",
        "taxa_alfabetizacao",
        "media_portugues",
    ]
    df = silver_municipio[[c for c in colunas if c in silver_municipio.columns]].copy()
    ordenar = [c for c in ["id_municipio", "ano", "rede", "serie"] if c in df.columns]
    return df.sort_values(ordenar).reset_index(drop=True)


def build_comparativo_metas_resultados(silver_metas: pd.DataFrame) -> pd.DataFrame:
    """
    Compara a taxa de alfabetização realizada com as metas definidas.

    Para cada registro de meta (nível, localidade, rede e ano-alvo), calcula a
    distância entre a taxa realizada no ano-base e a meta, além de um indicador
    booleano de atingimento.
    """
    df = silver_metas.copy()
    df = df.dropna(subset=["meta_alfabetizacao"])

    df["gap_para_meta"] = (df["meta_alfabetizacao"] - df["taxa_alfabetizacao"]).round(4)
    df["atingiu_meta"] = df["taxa_alfabetizacao"] >= df["meta_alfabetizacao"]

    colunas = [
        "nivel_geografico",
        "ano",
        "ano_meta",
        "id_municipio",
        "id_municipio_nome",
        "sigla_uf",
        "sigla_uf_nome",
        "rede",
        "taxa_alfabetizacao",
        "meta_alfabetizacao",
        "gap_para_meta",
        "atingiu_meta",
    ]
    df = df[[c for c in colunas if c in df.columns]]
    ordenar = [c for c in ["nivel_geografico", "ano", "ano_meta"] if c in df.columns]
    return df.sort_values(ordenar).reset_index(drop=True)


def build_evolucao_temporal(silver_metas: pd.DataFrame) -> pd.DataFrame:
    """
    Evolução temporal da taxa de alfabetização realizada, por nível geográfico.

    A taxa realizada se repete entre os diferentes anos-alvo de meta; portanto,
    remove-se a duplicidade para obter uma linha por localidade/rede/ano.
    """
    colunas = [
        "nivel_geografico",
        "ano",
        "id_municipio",
        "id_municipio_nome",
        "sigla_uf",
        "sigla_uf_nome",
        "rede",
        "taxa_alfabetizacao",
    ]
    df = silver_metas[[c for c in colunas if c in silver_metas.columns]].copy()
    df = df.dropna(subset=["taxa_alfabetizacao"]).drop_duplicates()
    ordenar = [c for c in ["nivel_geografico", "id_municipio", "sigla_uf", "ano"] if c in df.columns]
    return df.sort_values(ordenar).reset_index(drop=True)
