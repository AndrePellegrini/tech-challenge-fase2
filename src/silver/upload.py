from datetime import datetime, UTC
from pathlib import Path

import pandas as pd

from src.bronze.aws_client import create_s3_client
from src.bronze.config import S3_BUCKET_NAME

TMP_DIR = Path("tmp")

def add_silver_metadata(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Adiciona metadados técnicos da camada Silver.
    """

    df = df.copy()

    df["_processed_ts"] = datetime.now(UTC)
    df["_layer"] = "silver"
    df["_table"] = table_name

    return df

def save_silver_dataframe_as_parquet(df: pd.DataFrame, table_name: str) -> Path:
    """
    Salva DataFrame Silver temporariamente como Parquet.
    """

    TMP_DIR.mkdir(exist_ok = True)

    file_path = TMP_DIR / f"{table_name}.parquet"
    df.to_parquet(file_path, index = False)

    return file_path

def upload_silver_file_to_s3(file_path: Path, table_name: str) -> str:
    """
    Envia arquivos Parquet da Silver para o S3.
    """

    s3 = create_s3_client()

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    s3_key = f"Silver/{table_name}/processing_date={today}/{file_path.name}"

    s3.upload_file(str(file_path), S3_BUCKET_NAME, s3_key)

    return s3_key

def cleanup_local_file(file_path: Path) -> None:
    """
    Remove arquivo temporário local.
    """

    if file_path.exists():
        file_path.unlink()

def upload_dataframe_to_silver_as_parquet(df: pd.DataFrame, table_name: str) -> str:
    """
    Adiciona metadados, salva Parquet e envia para a Silver no S3.
    """

    df = add_silver_metadata(df, table_name)
    file_path = save_silver_dataframe_as_parquet(df, table_name)

    try:
        s3_key = upload_silver_file_to_s3(file_path, table_name)
    finally:
        cleanup_local_file(file_path)

    return s3_key
