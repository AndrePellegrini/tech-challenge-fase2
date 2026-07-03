import pandas as pd

def build_integrated_table(
        base_df: pd.DataFrame,
        reference_tables : dict[str, pd.DataFrame],
        joins: list[dict],
) -> pd.DataFrame:
    
    """
    Constrói uma tabela integrada a partir de uma tabela base e das regras
    definidas no integration_catalog.
    """

    df = base_df.copy()

    for join in joins:
        reference_df = reference_tables[join["reference_table"]]

        df = df.merge(
            reference_df,
            on = join["on"],
            how = join["how"],
            suffixes = ("", "_ref"),
        )
    
    return df
