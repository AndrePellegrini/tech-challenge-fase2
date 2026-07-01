"""
Leitura das tabelas da camada Bronze no S3.

Cada função retorna o DataFrame da partição mais recente da tabela Bronze
correspondente, servindo de entrada para o profiling e as transformações Silver.
"""
import pandas as pd

from src.common.config import BRONZE_PREFIX
from src.common.s3_io import read_table_latest_partition


def read_bronze_table(table_name: str) -> pd.DataFrame:
    """Lê a partição mais recente de uma tabela da camada Bronze."""
    return read_table_latest_partition(BRONZE_PREFIX, table_name)
