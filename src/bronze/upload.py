from datetime import datetime
from pathlib  import Path
import pandas as pd

from src.bronze.aws_client import create_s3_client
from src.bronze.config import S3_BUCKET_NAME

TMP_DIR = Path("tmp")

def add_ingestion_metadata(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Adiciona metadados técnicos de ingestão na camada Bronze.
    """
    df["_ingestion_ts"] = datetime.utcnow()
    df["_source"] = "basedosdados_inep"
    df["_table"] = table_name

    return df

def save_dataframe_as_parquet(df: pd.DataFrame, table_name: str) -> Path:
    TMP_DIR.mkdir(exist_ok=True)

    """ salva os arquivos localmente """

    file_path = TMP_DIR / f"{table_name}.parquet"

    df.to_parquet(file_path, index=False)

    return file_path

def upload_file_to_s3(file_path: Path, table_name: str) -> str:
    s3 = create_s3_client()

    """ envia os arquivos para o s3 """

    today = datetime.utcnow().strftime("%Y-%m-%d")
    s3_key = f"bronze/{table_name}/ingestion_date={today}/{file_path.name}"

    s3.upload_file(str(file_path), S3_BUCKET_NAME, s3_key)

    return s3_key


def cleanup_local_file(file_path: Path) -> None:
    if file_path.exists():
        file_path.unlink()

""" apaga os arquivos temporários """

def upload_dataframe_to_s3_as_parquet(df: pd.DataFrame, table_name: str) -> str:
    df = add_ingestion_metadata(df, table_name)

    file_path = save_dataframe_as_parquet(df, table_name)

    try:
        s3_key = upload_file_to_s3(file_path, table_name)
    finally:
        cleanup_local_file(file_path)

    return s3_key