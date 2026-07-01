"""
Gravação da camada Gold no S3.

Adiciona metadados técnicos da Gold e grava os datasets analíticos em Parquet,
particionados por data de processamento.
"""
from datetime import datetime, timezone

import pandas as pd

from src.common.config import GOLD_PREFIX
from src.common.s3_io import write_table_partitioned


def add_gold_metadata(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Adiciona metadados técnicos de processamento da camada Gold."""
    df = df.copy()
    df["_gold_processing_ts"] = datetime.now(timezone.utc)
    df["_source_layer"] = "silver"
    df["_table"] = table_name
    return df


def write_gold_table(df: pd.DataFrame, table_name: str) -> str:
    """Grava um dataset analítico na camada Gold."""
    df = add_gold_metadata(df, table_name)
    return write_table_partitioned(df, GOLD_PREFIX, table_name)
