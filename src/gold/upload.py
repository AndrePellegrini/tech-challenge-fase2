from datetime import datetime, UTC
from pathlib import Path

import pandas as pd

from src.bronze.aws_client import create_s3_client
from src.common.config import S3_BUCKET_NAME

TMP_DIR = Path("tmp")


def add_gold_metadata(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Adiciona metadados técnicos da camada Gold.
    """

    df = df.copy()

    df["_processed_ts"] = datetime.now(UTC)
    df["_layer"] = "gold"
    df["_table"] = table_name

    return df


def save_gold_dataframe_as_parquet(df: pd.DataFrame, table_name: str) -> Path:
    """
    Salva DataFrame Gold temporariamente como Parquet.
    """

    TMP_DIR.mkdir(exist_ok=True)

    file_path = TMP_DIR / f"{table_name}.parquet"
    df.to_parquet(file_path, index=False)

    return file_path


def upload_gold_file_to_s3(file_path: Path, table_name: str) -> str:
    """
    Envia arquivos Parquet da Gold para o S3.
    """

    s3 = create_s3_client()

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    s3_key = f"gold/{table_name}/processing_date={today}/{file_path.name}"

    s3.upload_file(str(file_path), S3_BUCKET_NAME, s3_key)

    return s3_key


def cleanup_local_file(file_path: Path) -> None:
    """
    Remove arquivo temporário local.
    """

    if file_path.exists():
        file_path.unlink()


def upload_dataframe_to_gold_as_parquet(df: pd.DataFrame, table_name: str) -> str:
    """
    Adiciona metadados, salva Parquet e envia para a Gold no S3.
    """

    df = add_gold_metadata(df, table_name)
    file_path = save_gold_dataframe_as_parquet(df, table_name)

    try:
        s3_key = upload_gold_file_to_s3(file_path, table_name)
    finally:
        cleanup_local_file(file_path)

    return s3_key
