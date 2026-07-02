import logging

from src.silver.reader import read_bronze_table
from src.silver.profiling import profile_dataframe
from src.silver.quality import(
    validate_not_null,
    validate_range,
    validate_duplicates,
    validate_required_columns,
)
from src.silver.transform import transform_base_table
from src.silver.upload import upload_dataframe_to_silver_as_parquet
from src.silver.report import save_profile_report
from src.silver.catalog import TABLE_CATALOG

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"
)




def run_silver_pipeline() -> None:
    success_tables = []
    failed_tables = []

    for table_name, table_config in TABLE_CATALOG.items():

        primary_key = table_config['primary_key']
        required_columns = table_config['required_columns']
        range_rules = table_config['range_rules']
        categorical_columns = table_config['categorical_columns']

        try:
            logging.info(f"Iniciando Silver da tabela: {table_name}")

            df_bronze = read_bronze_table(table_name)

            profile = profile_dataframe(df_bronze, table_name)
            profile_path = save_profile_report(
                profile = profile,
                layer = 'bronze',
                table_name = table_name,
            )
            logging.info(f'Profile salvo: {profile_path}')

            missing_columns = validate_required_columns(df_bronze, required_columns)
            if missing_columns:
                raise ValueError(
                    f"Colunas obrigatórias ausentes em {table_name}: {missing_columns}"
                )

            nulls = validate_not_null(df_bronze, required_columns)
            duplicates = validate_duplicates(df_bronze, primary_key)

            logging.info(f"Nulos em chaves {table_name}: {nulls}")
            logging.info(f"Duplicados {table_name}: {duplicates}")

            for column, rule in range_rules.items():
                out_of_range = validate_range(
                    df_bronze,
                    column,
                    rule['min'],
                    rule['max'],
                )
                logging.info(f'Valores fora da faixa {table_name}.{column}: {out_of_range}')
            
            df_silver = transform_base_table(
                df_bronze,
                key_columns = primary_key,
                categorical_columns = categorical_columns,
            )

            silver_profile = profile_dataframe(df_silver, table_name)
            silver_profile_path = save_profile_report(
                profile = silver_profile,
                layer = 'silver',
                table_name = table_name,
            )
            logging.info(f'Profile Silver salvo: {silver_profile_path}')

            s3_key = upload_dataframe_to_silver_as_parquet(df_silver, table_name)

            success_tables.append(table_name)
            logging.info(f'Silver finalizada: {table_name} | s3_key={s3_key}')

        except Exception as error:
            failed_tables.append(table_name)
            logging.exception(f"Erro na Silver da tabela {table_name}: {error}")

    logging.info(f"Tabelas Silver processadas com sucesso: {success_tables}")

    if failed_tables:
        logging.error(f"Tabelas Silver com erro: {failed_tables}")
        raise RuntimeError(f"Falha na Silver: {failed_tables}")

if __name__ == "__main__":
    run_silver_pipeline()