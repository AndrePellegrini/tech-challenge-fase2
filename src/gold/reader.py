"""
Leitura das tabelas da camada Silver para uso na camada Gold.

Reutiliza o reader da Silver e remove os metadados técnicos (colunas
iniciadas por "_"), deixando apenas as colunas de negócio.
"""
import pandas as pd

from src.silver.reader import read_silver_table


def read_gold_source(table_name: str) -> pd.DataFrame:
    """
    Lê a versão mais recente de uma tabela Silver, sem metadados técnicos.
    """

    df = read_silver_table(table_name)

    metadata_columns = [col for col in df.columns if col.startswith("_")]

    return df.drop(columns=metadata_columns)
