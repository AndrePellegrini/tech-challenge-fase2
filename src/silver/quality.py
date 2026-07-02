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

def validate_relationship(
        df: pd.DataFrame,
        reference_df: pd.DataFrame,
        columns: list[str],
        reference_columns: list[str],
) -> int:
    """
    Conta registros cuja chave não existe na tabela de referência.
    """

    if not all(col in df.columns for col in columns):
        return 0

    if not all(col in reference_df.columns for col in reference_columns):
        return 0
    
    left_keys = df[columns].dropna().drop_duplicates()
    right_keys = (
        reference_df[reference_columns]
        .dropna()
        .drop_duplicates()
    )

    right_keys.columns = columns

    validation = left_keys.merge(
        right_keys,
        on = columns,
        how = "left",
        indicator = True,
    )

    invalid_count = (validation["_merge"] == "left_only").sum()

    return int(invalid_count)

def raise_if_quality_errors(
        table_name: str,
        missing_columns: list[str],
        nulls: dict,
        duplicates: int,
        range_errors: dict,
        relationship_errors: dict,
) -> None:
    """
    Interrompe a pipeline quando existirem erros críticos de qualidade.
    """

    errors = []

    if missing_columns:
        errors.append(f"colunas obrigatórias ausentes: {missing_columns}")

    null_columns = {col: count for col, count in nulls.items() if count > 0}
    if null_columns:
        errors.append(f"colunas obrigatórias com valores nulos: {null_columns}")

    if duplicates > 0:
        errors.append(f"duplicidades na chave natural: {duplicates}")

    invalid_ranges = {col: count for col, count in range_errors.items() if count > 0}
    if invalid_ranges:
        errors.append(f"valores fora do intervalo esperado: {invalid_ranges}")
    
    if errors:
        raise ValueError(f"Falha de qualidade na tabela {table_name}: " + " | ".join(errors))