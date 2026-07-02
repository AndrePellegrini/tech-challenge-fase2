import pandas as pd

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza o nome das colunas para snake_case simples.
    """

    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex = False)
        .str.replace("-", "_", regex = False)
    )

    return df

def convert_year_column(df: pd.DataFrame, column: str = "ano") -> pd.DataFrame:
    """
    Converte coluna de ano para inteiro otimizado, quando não houver nulos.
    """

    df = df.copy()

    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors = "coerce")

        if df[column].isna().sum() == 0:
            df[column] = df[column].astype('int16')
        else:
            df[column] = df[column].astype('Int64')

    return df

def remove_duplicates(df: pd.DataFrame, key_columns: list[str]) -> pd.DataFrame:
    """
    Remove duplicidades usando colunas-chave.
    """

    existing_columns = [col for col in key_columns if col in df.columns]

    if not existing_columns:
        return df.copy()

    return df.drop_duplicates(subset = existing_columns).copy()

def transform_base_table(df: pd.DataFrame, 
                         key_columns: list[str],
                         categorical_columns: list[str],
                         ) -> pd.DataFrame:
    """
    Aplica transformações padrão da Silver.
    """

    df = normalize_column_names(df)
    df = convert_year_column(df)
    df = remove_duplicates(df, key_columns)
    df = optimize_dtypes(df, categorical_columns)

    return df


def optimize_dtypes(df: pd.DataFrame,
                    categorical_columns: list[str],
                    ) -> pd.DataFrame:
    """
    Otimiza tipos de dados para reduzir uso de memória na camada Silver.
    """

    df = df.copy()

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype('category')

    float_columns = df.select_dtypes(include=['float64']).columns

    for col in float_columns:
        df[col] = df[col].astype('float32')

    return df