"""
Leitura das tabelas da camada Silver no S3 para uso na camada Gold.

Remove os metadados técnicos da Silver, deixando apenas as colunas de negócio
para a montagem dos datasets analíticos.
"""
import pandas as pd

from src.common.config import SILVER_PREFIX
from src.common.s3_io import read_table_latest_partition

_SILVER_METADATA = ["_silver_processing_ts", "_source_layer", "_table"]


def read_silver_table(table_name: str) -> pd.DataFrame:
    """Lê a partição mais recente de uma tabela Silver, sem metadados técnicos."""
    df = read_table_latest_partition(SILVER_PREFIX, table_name)
    return df.drop(columns=[c for c in _SILVER_METADATA if c in df.columns])
