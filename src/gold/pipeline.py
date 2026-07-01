"""
Orquestração da camada Gold.

Lê as tabelas Silver tratadas e monta os datasets analíticos finais,
gravando-os no S3 na camada Gold.
"""
from src.common.logger import get_logger
from src.gold.reader import read_silver_table
from src.gold.transform import (
    build_comparativo_metas_resultados,
    build_evolucao_temporal,
    build_indicador_municipio,
)
from src.gold.upload import write_gold_table

logger = get_logger("gold.pipeline")


def run_gold_pipeline() -> None:
    """Executa a pipeline completa da camada Gold."""
    success, failed = [], []

    try:
        silver_municipio = read_silver_table("alfabetizacao_municipio")
        silver_metas = read_silver_table("metas")
    except Exception as error:  # noqa: BLE001
        logger.exception("Erro ao ler a camada Silver: %s", error)
        raise

    datasets = {
        "indicador_alfabetizacao_municipio": lambda: build_indicador_municipio(
            silver_municipio
        ),
        "comparativo_metas_resultados": lambda: build_comparativo_metas_resultados(
            silver_metas
        ),
        "evolucao_temporal_indicador": lambda: build_evolucao_temporal(silver_metas),
    }

    for name, builder in datasets.items():
        try:
            logger.info("Construindo Gold: %s", name)
            df = builder()
            s3_key = write_gold_table(df, name)
            logger.info("Gold %s finalizada | linhas=%d | %s", name, len(df), s3_key)
            success.append(name)
        except Exception as error:  # noqa: BLE001
            failed.append(name)
            logger.exception("Erro ao construir Gold %s: %s", name, error)

    logger.info("Gold concluída com sucesso: %s", success)
    if failed:
        logger.error("Gold com falha: %s", failed)
        raise RuntimeError(f"Falha na camada Gold: {failed}")


if __name__ == "__main__":
    run_gold_pipeline()
