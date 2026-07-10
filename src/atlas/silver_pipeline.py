import logging

from src.common.s3_io import read_table_latest_partition, write_table_with_metadata
from src.atlas.config import ATLAS_TABLE_NAME
from src.atlas.transform import transform_atlas_uf


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s",
)


def run_atlas_silver_pipeline() -> None:
    """
    Lê a Bronze do Atlas, trata os dados e grava na Silver.
    """

    logging.info("Iniciando Silver do Atlas")

    df_bronze = read_table_latest_partition(
        layer = "bronze",
        table_name = ATLAS_TABLE_NAME,
    )

    logging.info(f"Atlas Bronze lido com {len(df_bronze)} linhas")

    df_silver = transform_atlas_uf(df_bronze)

    logging.info(f"Atlas Silver gerado com {len(df_silver)} linhas")

    s3_key = write_table_with_metadata(
        df = df_silver,
        layer = "silver",
        table_name = ATLAS_TABLE_NAME,
        source = "Atlas do Desenvolvimento Humano",
    )

    logging.info(f"Atlas enviado para Silver | s3_key={s3_key}")


if __name__ == "__main__":
    run_atlas_silver_pipeline()