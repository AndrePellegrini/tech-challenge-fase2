import pandas as pd

def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    """
    Valida se as colunas obrigatórias existem no DataFrame.
    """

    return [col for col in required_columns if col not in df.columns]

def validate_not_null(df: pd.DataFrame, columns: list[str]) -> dict:
    """
    Conta nulos em colunas críticas.
    """

    return {
        col: int(df[col].isna().sum())
        for col in columns
        if col in df.columns
    }

def validate_range(df: pd.DataFrame, 
                   column: str, 
                   min_value: float | None, 
                   max_value: float | None,
                   ) -> int:
    """
    Conta valores fora de uma faixa esperada.
    Permite min_value ou max_value como None.
    """

    if column not in df.columns:
        return 0
    
    valid_mask = df[column].notna()

    if min_value is not None:
        valid_mask = valid_mask & (df[column] >= min_value)

    if max_value is not None:
        valid_mask = valid_mask & (df[column] <= max_value)

    invalid_mask = df[column].notna() & ~valid_mask

    return int(invalid_mask.sum())


def validate_duplicates(df: pd.DataFrame, key_columns: list[str]) -> int:
    """
    Conta duplicidades considerando uma chave
    """
    
    existing_columns = [col for col in key_columns if col in df.columns]

    if not existing_columns:
        return 0
    
    return int(df.duplicated(subset = existing_columns).sum())