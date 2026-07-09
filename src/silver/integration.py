import pandas as pd

def drop_technical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas técnicas antes das integrações.
    """

    technical_columns = [
        column for column in df.columns
        if column.startswith("_")
    ]

    return df.drop(columns=technical_columns, errors="ignore").copy()

def build_integrated_table(
        base_df: pd.DataFrame,
        reference_tables : dict[str, pd.DataFrame],
        joins: list[dict],
) -> pd.DataFrame:
    
    """
    Constrói uma tabela integrada a partir de uma tabela base e das regras
    definidas no integration_catalog.py.
    """

    df = base_df.copy()

    for join in joins:
        reference_df = reference_tables[join["reference_table"]]

        df = df.merge(
            reference_df,
            on = join["on"],
            how = join["how"],
            suffixes = ("", f"_{join['reference_table']}"),
        )
    
    return df
