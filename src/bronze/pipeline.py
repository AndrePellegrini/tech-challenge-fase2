import logging

from src.bronze.extract import extract_from_basedosdados
from src.bronze.upload import upload_dataframe_to_s3_as_parquet

from src.bronze.queries import (
    QUERY_ALUNOS,
    QUERY_UF,
    QUERY_MUNICIPIO,
    QUERY_META_MUNICIPIO,
    QUERY_META_UF,
    QUERY_META_BRASIL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

TABLES_TO_INGEST = {
    "alunos": QUERY_ALUNOS,
    "uf": QUERY_UF,
    "municipio": QUERY_MUNICIPIO,
    "meta_municipio": QUERY_META_MUNICIPIO,
    "meta_uf": QUERY_META_UF,
    "meta_brasil": QUERY_META_BRASIL,
}


def run_bronze_pipeline() -> None:
    success_tables = []
    failed_tables = []

    for table_name, query in TABLES_TO_INGEST.items():
        try:
            logging.info(f"Iniciando ingestão da tabela: {table_name}")

            df = extract_from_basedosdados(query)
            s3_key = upload_dataframe_to_s3_as_parquet(df, table_name)

            success_tables.append(table_name)
            logging.info(f"Ingestão finalizada: {table_name} | s3_key={s3_key}")

        except Exception as error:
            failed_tables.append(table_name)
            logging.exception(f"Erro na ingestão da tabela {table_name}: {error}")

    logging.info(f"Tabelas processadas com sucesso: {success_tables}")

    if failed_tables:
        logging.error(f"Tabelas com erro: {failed_tables}")
        raise RuntimeError(f"Falha na ingestão de tabelas: {failed_tables}")


if __name__ == "__main__":
    run_bronze_pipeline()