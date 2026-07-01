"""
Orquestração da camada Silver.

Fluxo por tabela:
1. Lê a tabela Bronze mais recente no S3.
2. Executa o Data Profiling.
3. Aplica as transformações de limpeza/padronização.
4. Valida com as regras de qualidade (separa válidos de inválidos).
5. Grava a Silver, a quarentena e o relatório de qualidade no S3.

A tabela `metas` é um caso especial: consolida meta_brasil, meta_uf e
meta_municipio em uma única estrutura analítica.
"""
import json
from pathlib import Path

from src.common.logger import get_logger
from src.silver.profiling import log_profile, profile_dataframe
from src.silver.quality import apply_quality
from src.silver.reader import read_bronze_table
from src.silver.transform import (
    build_metas,
    transform_alfabetizacao_municipio,
    transform_alfabetizacao_uf,
    transform_alunos,
)
from src.silver.upload import (
    write_quality_report,
    write_quarantine,
    write_silver_table,
)

logger = get_logger("silver.pipeline")

REPORTS_DIR = Path("reports/silver")

# Tabelas Silver de origem única (bronze -> silver).
SIMPLE_TABLES = {
    "alunos": ("alunos", transform_alunos),
    "alfabetizacao_municipio": ("municipio", transform_alfabetizacao_municipio),
    "alfabetizacao_uf": ("uf", transform_alfabetizacao_uf),
}


def _persist_report_local(report: dict, table_name: str) -> None:
    """Salva uma cópia local do relatório de qualidade em reports/silver/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{table_name}.json"
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def process_silver_table(silver_name: str, bronze_df, transform_fn) -> dict:
    """Executa profiling, transformação, qualidade e gravação de uma tabela."""
    logger.info("Processando Silver: %s", silver_name)

    profile = profile_dataframe(bronze_df, silver_name)
    log_profile(profile, logger)

    transformed = transform_fn(bronze_df)
    result = apply_quality(transformed, silver_name)

    write_silver_table(result.valid, silver_name)
    write_quarantine(result.invalid, silver_name)

    report = {"profiling_bronze": profile, "qualidade": result.report}
    write_quality_report(report, silver_name)
    _persist_report_local(report, silver_name)

    logger.info(
        "Silver %s finalizada | válidos=%d | inválidos=%d",
        silver_name,
        result.report["registros_validos"],
        result.report["registros_invalidos"],
    )
    return report


def run_silver_pipeline() -> None:
    """Executa a pipeline completa da camada Silver."""
    success, failed = [], []

    # Tabelas de origem única.
    for silver_name, (bronze_name, transform_fn) in SIMPLE_TABLES.items():
        try:
            bronze_df = read_bronze_table(bronze_name)
            process_silver_table(silver_name, bronze_df, transform_fn)
            success.append(silver_name)
        except Exception as error:  # noqa: BLE001
            failed.append(silver_name)
            logger.exception("Erro ao processar Silver %s: %s", silver_name, error)

    # Tabela consolidada de metas (três origens).
    try:
        logger.info("Processando Silver: metas (consolidação)")
        meta_brasil = read_bronze_table("meta_brasil")
        meta_uf = read_bronze_table("meta_uf")
        meta_municipio = read_bronze_table("meta_municipio")

        metas = build_metas(meta_brasil, meta_uf, meta_municipio)
        profile = profile_dataframe(metas, "metas")
        log_profile(profile, logger)

        result = apply_quality(metas, "metas")
        write_silver_table(result.valid, "metas")
        write_quarantine(result.invalid, "metas")

        report = {"profiling_bronze": profile, "qualidade": result.report}
        write_quality_report(report, "metas")
        _persist_report_local(report, "metas")
        success.append("metas")
    except Exception as error:  # noqa: BLE001
        failed.append("metas")
        logger.exception("Erro ao processar Silver metas: %s", error)

    logger.info("Silver concluída com sucesso: %s", success)
    if failed:
        logger.error("Silver com falha: %s", failed)
        raise RuntimeError(f"Falha na camada Silver: {failed}")


if __name__ == "__main__":
    run_silver_pipeline()
