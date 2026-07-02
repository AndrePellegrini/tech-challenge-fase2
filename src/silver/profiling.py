import pandas as pd

def profile_dataframe(df: pd.DataFrame, table_name: str) -> dict:
    """
    Gera um diagnóstico báscio de uma tabela Bronze
    """

    profile = {
        "table_name": table_name,
        "rows": len(df),
        "columns": len(df.columns),
        "schema": df.dtypes.astype(str).to_dict(),
        "nulls": df.isna().sum().to_dict(),
        "duplicated_rows": int(df.duplicated().sum()),
    }

    numeric_columns = df.select_dtypes(include = "number").columns

    if len(numeric_columns) > 0:
        profile['numeric_summary'] = (
            df[numeric_columns]
            .describe()
            .to_dict()
        )
    else:
        profile['numeric_summary'] = {}

    return profile