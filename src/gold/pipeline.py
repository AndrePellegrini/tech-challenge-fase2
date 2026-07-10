import logging

from src.gold.catalog import GOLD_CATALOG
from src.gold.reader import read_gold_source
from src.gold.transform import GOLD_BUILDERS
from src.gold.upload import upload_dataframe_to_gold_as_parquet
from src.silver.profiling import profile_dataframe
from src.silver.report import save_profile_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_gold_pipeline() -> None:
    """
    Gera todos os datasets analíticos definidos no GOLD_CATALOG a partir
    das tabelas Silver e grava o resultado na camada Gold do S3.
    """

    success_tables = []
    failed_tables = []

    for table_name, table_config in GOLD_CATALOG.items():

        try:
            logging.info(f"Iniciando Gold da tabela: {table_name}")

            # -------------------------
            # Leitura Silver
            # -------------------------

            sources = {
                source_table: read_gold_source(source_table)
                for source_table in table_config["sources"]
            }

            # -------------------------
            # Transformações
            # -------------------------

            builder = GOLD_BUILDERS[table_config["builder"]]
            df_gold = builder(sources)

            # -------------------------
            # Profiling Gold
            # -------------------------

            gold_profile = profile_dataframe(df_gold, table_name)
            gold_profile_path = save_profile_report(
                profile=gold_profile,
                layer="gold",
                table_name=table_name,
            )
            logging.info(f"Profile Gold salvo: {gold_profile_path}")

            # -------------------------
            # Upload
            # -------------------------

            s3_key = upload_dataframe_to_gold_as_parquet(df_gold, table_name)

            success_tables.append(table_name)
            logging.info(
                f"Gold finalizada: {table_name} | linhas={len(df_gold)} | s3_key={s3_key}"
            )

        except Exception as error:
            failed_tables.append(table_name)
            logging.exception(f"Erro na Gold da tabela {table_name}: {error}")

    logging.info(f"Tabelas Gold processadas com sucesso: {success_tables}")

    if failed_tables:
        logging.error(f"Tabelas Gold com erro: {failed_tables}")
        raise RuntimeError(f"Falha na Gold: {failed_tables}")


if __name__ == "__main__":
    run_gold_pipeline()
