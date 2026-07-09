import pandas as pd

from src.atlas.config import ATLAS_BASE_FILE

def extract_atlas_base() -> pd.DataFrame:
    """
    Lê a planilha base do Atlas do Desenvolvimento Humano.
    """

    if not ATLAS_BASE_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo do Atlas não encontrado em: {ATLAS_BASE_FILE}"
        )

    return pd.read_excel(ATLAS_BASE_FILE)

