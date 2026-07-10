from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ATLAS_EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"

ATLAS_BASE_FILE = ATLAS_EXTERNAL_DIR / "atlas_uf.parquet"

ATLAS_TABLE_NAME = "atlas_uf"