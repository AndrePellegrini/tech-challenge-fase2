import pandas as pd

from src.atlas.config import ATLAS_TABLE_NAME
from src.common.s3_io import write_table_with_metadata


def upload_atlas_to_bronze(df: pd.DataFrame) -> str:
    """
    Envia a base do Atlas para a camada Bronze no S3.
    """

    return write_table_with_metadata(
        df=df,
        layer="bronze",
        table_name=ATLAS_TABLE_NAME,
        source="Atlas do Desenvolvimento Humano",
    )