import json
from datetime import datetime, UTC
from pathlib import Path

REPORT_DIR = Path('reports') / 'profiling'

def save_profile_report(profile: dict, layer: str, table_name: str) -> Path:
    """
    Salva relatório de profiling em JSON.
    """

    report_date = datetime.now(UTC).strftime("%Y-%m-%d")

    output_dir = REPORT_DIR / layer / f"processing_date={report_date}"
    output_dir.mkdir(parents = True, exist_ok = True)

    output_path = output_dir / f'{table_name}.json'

    with output_path.open('w', encoding = 'utf-8') as file:
        json.dump(profile, file, ensure_ascii = False, indent = 4, default = str)

    return output_path