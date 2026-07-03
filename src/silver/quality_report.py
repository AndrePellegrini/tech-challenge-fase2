import json
from datetime import datetime, UTC
from pathlib import Path


REPORT_DIR = Path("reports") / "quality"


def define_quality_status(
    missing_columns: list[str],
    nulls: dict,
    duplicates: int,
    range_errors: dict,
    relationship_errors: dict,
) -> str:
    has_error = (
        bool(missing_columns)
        or any(count > 0 for count in nulls.values())
        or duplicates > 0
        or any(count > 0 for count in range_errors.values())
    )

    has_warning = any(count > 0 for count in relationship_errors.values())

    if has_error:
        return "ERROR"

    if has_warning:
        return "WARNING"

    return "OK"


def build_quality_report(
    table_name: str,
    missing_columns: list[str],
    nulls: dict,
    duplicates: int,
    range_errors: dict,
    relationship_errors: dict,
) -> dict:
    return {
        "table_name": table_name,
        "status": define_quality_status(
            missing_columns=missing_columns,
            nulls=nulls,
            duplicates=duplicates,
            range_errors=range_errors,
            relationship_errors=relationship_errors,
        ),
        "missing_columns": missing_columns,
        "nulls": nulls,
        "duplicates": duplicates,
        "range_errors": range_errors,
        "relationship_errors": relationship_errors,
        "generated_at": datetime.now(UTC).isoformat(),
    }


def save_quality_report(
    table_name: str,
    report: dict,
) -> Path:
    report_date = datetime.now(UTC).strftime("%Y-%m-%d")

    output_dir = REPORT_DIR / f"processing_date={report_date}"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{table_name}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4,
            default=str,
        )

    return output_path