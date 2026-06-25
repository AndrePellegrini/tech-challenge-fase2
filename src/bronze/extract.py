import basedosdados as bd
import pandas as pd

from src.bronze.config import BILLING_PROJECT_ID


def extract_from_basedosdados(query: str) -> pd.DataFrame:
    """    Executa uma query na Base dos Dados/BigQuery e retorna um DataFrame   """
    """    Responsável por extrair os dados   """
    
    df = bd.read_sql(
        query=query,
        billing_project_id= 'projeto-fiap-grupo-x'
    )

    return df