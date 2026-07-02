import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
BILLING_PROJECT_ID = os.getenv("BILLING_PROJECT_ID")

def validate_config():
    required = {
        "AWS_ACCESS_KEY_ID":AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "S3_BUCKET_NAME": S3_BUCKET_NAME,
        "BILLING_PROJECT_ID": BILLING_PROJECT_ID,
    }

    missing = [k for k, v in required.items() if not v]

    if missing:
        raise ValueError(
            f"Variáveis não configuradas no .env: {', '.join(missing)}"
        )

validate_config()