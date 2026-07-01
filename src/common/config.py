"""
Configuração compartilhada entre as camadas Silver e Gold.

Lê as mesmas variáveis do .env já utilizadas pela camada Bronze,
centralizando o acesso à conta AWS e ao bucket do Data Lake.
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
