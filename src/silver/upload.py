"""
Gravação da camada Silver no S3 (Passo 4 da estratégia).

Adiciona metadados técnicos da Silver e grava os dados tratados em Parquet,
particionados por data de processamento. Também grava a fatia de registros
inválidos (quarentena) e o relatório de qualidade.
"""
import json
from datetime import datetime, timezone

import pandas as pd

from src.common.config import QUALITY_PREFIX, SILVER_PREFIX
from src.common.s3_io import write_json_object, write_table_partitioned


def add_silver_metadata(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Adiciona metadados técnicos de processamento da camada Silver."""
    df = df.copy()
    df["_silver_processing_ts"] = datetime.now(timezone.utc)
    df["_source_layer"] = "bronze"
    df["_table"] = table_name
    return df


def write_silver_table(df: pd.DataFrame, table_name: str) -> str:
    """Grava uma tabela válida na camada Silver."""
    df = add_silver_metadata(df, table_name)
    return write_table_partitioned(df, SILVER_PREFIX, table_name)


def write_quarantine(df: pd.DataFrame, table_name: str) -> str | None:
    """Grava os registros reprovados nas regras de qualidade (quarentena)."""
    if df.empty:
        return None
    df = add_silver_metadata(df, f"{table_name}_quarentena")
    return write_table_partitioned(df, QUALITY_PREFIX, f"{table_name}_quarentena")


def write_quality_report(report: dict, table_name: str) -> str:
    """Grava o relatório de qualidade da tabela em JSON no prefixo quality/."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s3_key = f"{QUALITY_PREFIX}/reports/{table_name}/processing_date={today}/report.json"
    payload = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    return write_json_object(payload, s3_key)
