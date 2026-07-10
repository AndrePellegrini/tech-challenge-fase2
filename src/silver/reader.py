from io import BytesIO

import pandas as pd

from src.bronze.aws_client import create_s3_client
from src.common.config import S3_BUCKET_NAME


def get_latest_layer_key(layer: str, table_name: str) -> str:
    """
    Busca o arquivo Parquet mais recente de uma tabela em uma camada do Data Lake.
    """

    s3 = create_s3_client()
    prefix = f"{layer}/{table_name}/"

    response = s3.list_objects_v2(
        Bucket=S3_BUCKET_NAME,
        Prefix=prefix,
    )

    parquet_files = [
        obj
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".parquet")
    ]

    if not parquet_files:
        raise FileNotFoundError(
            f"Nenhum arquivo Parquet encontrado em s3://{S3_BUCKET_NAME}/{prefix}"
        )

    latest_file = max(
        parquet_files,
        key=lambda obj: obj["LastModified"],
    )

    return latest_file["Key"]


def read_layer_table(layer: str, table_name: str) -> pd.DataFrame:
    """
    Lê a versão mais recente de uma tabela de uma camada do Data Lake.
    """

    s3 = create_s3_client()

    s3_key = get_latest_layer_key(
        layer=layer,
        table_name=table_name,
    )

    obj = s3.get_object(
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
    )

    return pd.read_parquet(BytesIO(obj["Body"].read()))


def read_bronze_table(table_name: str) -> pd.DataFrame:
    """
    Lê a versão mais recente de uma tabela Bronze.
    """

    return read_layer_table(
        layer="bronze",
        table_name=table_name,
    )


def read_silver_table(table_name: str) -> pd.DataFrame:
    """
    Lê a versão mais recente de uma tabela Silver.
    """

    return read_layer_table(
        layer="silver",
        table_name=table_name,
    )