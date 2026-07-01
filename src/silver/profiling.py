"""
Data Profiling da camada Bronze (Passo 1 da estratégia Silver).

Gera um diagnóstico das tabelas antes de qualquer transformação: quantidade de
linhas/colunas, schema, contagem e percentual de nulos, duplicidades e
estatísticas numéricas. O resultado é um dicionário serializável em JSON,
usado tanto em log quanto no relatório de qualidade.
"""
import pandas as pd


def profile_dataframe(df: pd.DataFrame, table_name: str) -> dict:
    """Retorna um perfil estatístico do DataFrame informado."""
    n_rows = int(len(df))

    columns = []
    for column in df.columns:
        null_count = int(df[column].isna().sum())
        columns.append(
            {
                "coluna": column,
                "tipo": str(df[column].dtype),
                "nulos": null_count,
                "nulos_pct": round((null_count / n_rows * 100), 2) if n_rows else 0.0,
                "valores_unicos": int(df[column].nunique(dropna=True)),
            }
        )

    numeric_stats = {}
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        described = numeric_df.describe().round(4)
        numeric_stats = {
            col: described[col].to_dict() for col in described.columns
        }

    return {
        "tabela": table_name,
        "linhas": n_rows,
        "colunas": int(df.shape[1]),
        "duplicatas_linha_completa": int(df.duplicated().sum()),
        "schema": columns,
        "estatisticas_numericas": numeric_stats,
    }


def log_profile(profile: dict, logger) -> None:
    """Emite um resumo do profiling no log da pipeline."""
    logger.info(
        "Profiling %s | linhas=%d | colunas=%d | duplicatas=%d",
        profile["tabela"],
        profile["linhas"],
        profile["colunas"],
        profile["duplicatas_linha_completa"],
    )
    for coluna in profile["schema"]:
        if coluna["nulos"] > 0:
            logger.info(
                "  nulos em %s: %d (%.2f%%)",
                coluna["coluna"],
                coluna["nulos"],
                coluna["nulos_pct"],
            )
