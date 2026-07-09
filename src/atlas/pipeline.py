import logging

from src.atlas.extract import extract_atlas_base
from src.atlas.upload import upload_atlas_to_bronze

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s",
)

def run_atlas_pipeline() -> None:
    """
    Executa a ingestão da base do Atlas para a camada Bronze.
    """

    logging.info("Iniciando ingestão do Atlas")

    df_atlas = extract_atlas_base()

    logging.info(f"Atlas extraído com {len(df_atlas)} linhas")

    s3_key = upload_atlas_to_bronze(df_atlas)

    logging.info(f"Atlas enviado para a Bronze | s3_key = {s3_key}")

if __name__ == "__main__":
    run_atlas_pipeline()