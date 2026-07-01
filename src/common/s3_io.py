"""
Entrada e saída de dados no S3 para as camadas Silver e Gold.

Concentra a leitura de Parquet do Data Lake (sempre a partição mais recente
de uma tabela) e a gravação de Parquet particionado por data de processamento.

A leitura é feita via boto3 + BytesIO (sem dependência de s3fs), lendo o
Parquet direto na memória com o pyarrow já utilizado no projeto.
"""
import io
from datetime import datetime, timezone
from pathlib import Path

import boto3
import pandas as pd

from src.common.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
)
from src.common.logger import get_logger

logger = get_logger(__name__)

TMP_DIR = Path("tmp")


def create_s3_client():
    """Cria o cliente S3 com as credenciais do .env (boto3)."""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def _list_parquet_keys(s3, prefix: str) -> list[str]:
    """Lista todas as chaves .parquet sob um prefixo, paginando os resultados."""
    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".parquet"):
                keys.append(obj["Key"])

    return keys


def _latest_partition_keys(keys: list[str]) -> list[str]:
    """
    Dada uma lista de chaves particionadas por `<coluna>=<valor>`, retorna
    apenas as chaves da partição de maior valor (data de processamento/ingestão
    mais recente).
    """
    partitions: dict[str, list[str]] = {}

    for key in keys:
        # Ex.: bronze/uf/ingestion_date=2026-07-01/uf.parquet
        partition_folder = None
        for part in key.split("/"):
            if "=" in part:
                partition_folder = part
        partition = partition_folder if partition_folder else ""
        partitions.setdefault(partition, []).append(key)

    if not partitions:
        return []

    latest = max(partitions.keys())
    return partitions[latest]


def read_table_latest_partition(layer: str, table_name: str) -> pd.DataFrame:
    """
    Lê a partição mais recente de uma tabela de uma camada do Data Lake.

    Ex.: read_table_latest_partition("bronze", "uf") lê
    s3://<bucket>/bronze/uf/ingestion_date=<mais_recente>/*.parquet
    """
    s3 = create_s3_client()
    prefix = f"{layer}/{table_name}/"

    all_keys = _list_parquet_keys(s3, prefix)
    if not all_keys:
        raise FileNotFoundError(
            f"Nenhum arquivo Parquet encontrado em s3://{S3_BUCKET_NAME}/{prefix}"
        )

    keys = _latest_partition_keys(all_keys)
    logger.info(
        "Lendo %s | camada=%s | partição com %d arquivo(s)",
        table_name,
        layer,
        len(keys),
    )

    frames: list[pd.DataFrame] = []
    for key in keys:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        buffer = io.BytesIO(response["Body"].read())
        frames.append(pd.read_parquet(buffer))

    return pd.concat(frames, ignore_index=True)


def write_table_partitioned(
    df: pd.DataFrame,
    layer: str,
    table_name: str,
    partition_column: str = "processing_date",
) -> str:
    """
    Salva um DataFrame como Parquet e envia para o S3 particionado por data.

    Segue o mesmo fluxo da Bronze: grava um arquivo temporário em tmp/,
    faz o upload e remove o arquivo local ao final.
    """
    s3 = create_s3_client()
    TMP_DIR.mkdir(exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    file_path = TMP_DIR / f"{layer}_{table_name}.parquet"
    df.to_parquet(file_path, index=False)

    s3_key = (
        f"{layer}/{table_name}/{partition_column}={today}/{table_name}.parquet"
    )

    try:
        s3.upload_file(str(file_path), S3_BUCKET_NAME, s3_key)
        logger.info("Gravado s3://%s/%s (%d linhas)", S3_BUCKET_NAME, s3_key, len(df))
    finally:
        if file_path.exists():
            file_path.unlink()

    return s3_key


def write_json_object(payload: str, s3_key: str) -> str:
    """Grava um conteúdo textual (ex.: relatório JSON) diretamente no S3."""
    s3 = create_s3_client()
    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        Body=payload.encode("utf-8"),
        ContentType="application/json",
    )
    logger.info("Gravado relatório em s3://%s/%s", S3_BUCKET_NAME, s3_key)
    return s3_key
