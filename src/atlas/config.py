from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ATLAS_EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"

ATLAS_BASE_FILE = ATLAS_EXTERNAL_DIR / "adh_radar_base_2012_2024.xlsx"

ATLAS_TABLE_NAME = "atlas_uf"