"""
Configuração central do projeto.

Todas as variáveis de ambiente utilizadas pelas pipelines são carregadas
neste módulo.
"""

import os

from dotenv import load_dotenv

load_dotenv()


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

BILLING_PROJECT_ID = os.getenv("BILLING_PROJECT_ID")

# Prefixos (camadas) do Data Lake dentro do bucket.

BRONZE_PREFIX = "bronze"
SILVER_PREFIX = "silver"
GOLD_PREFIX = "gold"
QUALITY_PREFIX = "quality"


def validate_config() -> None:
    required = {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "S3_BUCKET_NAME": S3_BUCKET_NAME,
        "BILLING_PROJECT_ID": BILLING_PROJECT_ID,
    }

    missing = [
        key
        for key, value in required.items()
        if not value
    ]

    if missing:
        raise ValueError(
            f"Variáveis não configuradas no .env: {', '.join(missing)}"
        )


validate_config()