"""
Testes de lógica das camadas Silver, Gold e do streaming com dados sintéticos.

Não dependem de AWS/S3 nem de Kafka: exercitam apenas as transformações,
as regras de qualidade e a validação de eventos (pandas puro). Podem ser
executados com:

    python -m tests.test_silver_gold
"""
import pandas as pd

from src.gold.transform import (
    build_comparativo_metas_resultados,
    build_desempenho_alunos_municipio,
    build_evolucao_temporal,
    build_indicador_municipio,
)
from src.silver.profiling import profile_dataframe
from src.silver.quality import (
    validate_duplicates,
    validate_range,
    validate_relationship,
)
from src.silver.transform import transform_base_table
from src.streaming.events import build_event, validate_event


# ---------------------------------------------------------------------------
# Dados sintéticos no formato produzido pela camada Silver
# ---------------------------------------------------------------------------

def _silver_municipio() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023, 2023, 2024],
            "id_municipio": ["3550308", "3304557", "3550308"],
            "id_municipio_nome": ["São Paulo", "Rio de Janeiro", "São Paulo"],
            "serie": ["2º ano"] * 3,
            "rede": ["Municipal"] * 3,
            "taxa_alfabetizacao": [55.0, 70.0, 65.0],
            "media_portugues": [700.0, 710.0, 720.0],
        }
    )


def _silver_uf() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023, 2024],
            "sigla_uf": ["SP", "SP"],
            "sigla_uf_nome": ["São Paulo", "São Paulo"],
            "serie": ["2º ano"] * 2,
            "rede": ["Total"] * 2,
            "taxa_alfabetizacao": [58.0, 62.0],
            "media_portugues": [705.0, 715.0],
        }
    )


def _silver_meta_brasil() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023],
            "rede": ["Total"],
            "taxa_alfabetizacao": [56.0],
            "meta_alfabetizacao_2024": [60.0],
            "meta_alfabetizacao_2030": [80.0],
            "percentual_participacao": [95.0],
        }
    )


def _silver_municipio_integrado() -> pd.DataFrame:
    """
    Formato da tabela integrada: municipio + meta_municipio, com sufixo
    "_ref" nas colunas conflitantes vindas da tabela de metas.
    """

    return pd.DataFrame(
        {
            "ano": [2023, 2023],
            "id_municipio": ["3550308", "3304557"],
            "id_municipio_nome": ["São Paulo", "Rio de Janeiro"],
            "serie": ["2º ano"] * 2,
            "rede": ["Municipal"] * 2,
            "taxa_alfabetizacao": [55.0, 70.0],
            "media_portugues": [700.0, 710.0],
            "id_municipio_nome_ref": ["São Paulo", "Rio de Janeiro"],
            "rede_ref": ["Total", "Total"],
            "taxa_alfabetizacao_ref": [55.0, 70.0],
            "meta_alfabetizacao_2024": [60.0, 65.0],
            "meta_alfabetizacao_2025": [64.0, None],
            "nivel_alfabetizacao": ["Intermediário", "Adequado"],
            "percentual_participacao": [94.0, 95.0],
        }
    )


def _silver_uf_integrado() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023],
            "sigla_uf": ["SP"],
            "sigla_uf_nome": ["São Paulo"],
            "serie": ["2º ano"],
            "rede": ["Total"],
            "taxa_alfabetizacao": [58.0],
            "media_portugues": [705.0],
            "sigla_uf_nome_ref": ["São Paulo"],
            "rede_ref": ["Total"],
            "taxa_alfabetizacao_ref": [58.0],
            "meta_alfabetizacao_2024": [62.0],
            "meta_alfabetizacao_2030": [82.0],
            "percentual_participacao": [96.0],
        }
    )


def _silver_alunos_integrado() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023, 2023, 2023],
            "id_municipio": ["3550308", "3550308", "3304557"],
            "id_municipio_nome": ["São Paulo", "São Paulo", "Rio de Janeiro"],
            "id_escola": ["1", "1", "2"],
            "id_aluno": ["a1", "a2", "a3"],
            "serie": ["2º ano"] * 3,
            "rede": ["Municipal"] * 3,
            "presenca": ["Presente"] * 3,
            "alfabetizado": ["Não", "Sim", "Sim"],
            "proficiencia": [700.0, 800.0, 750.0],
            "peso_aluno": [1.0, 3.0, 2.0],
            "taxa_alfabetizacao": [55.0, 55.0, 70.0],
            "media_portugues": [700.0, 700.0, 710.0],
        }
    )


# ---------------------------------------------------------------------------
# Silver
# ---------------------------------------------------------------------------

def test_transform_base_table_padroniza_e_remove_duplicatas():
    df = pd.DataFrame(
        {
            "Ano ": ["2023", "2023", "2023"],
            "ID-Municipio": ["3550308", "3550308", "3304557"],
            "rede": ["Municipal", "Municipal", "Estadual"],
        }
    )

    result = transform_base_table(
        df,
        key_columns=["ano", "id_municipio"],
        categorical_columns=["rede"],
    )

    # colunas normalizadas para snake_case
    assert "ano" in result.columns
    assert "id_municipio" in result.columns
    # duplicata (ano, id_municipio) removida
    assert len(result) == 2
    # ano convertido para inteiro e rede para categoria
    assert str(result["ano"].dtype) in ("int16", "Int64")
    assert str(result["rede"].dtype) == "category"


def test_validate_range_conta_valores_fora_da_faixa():
    df = pd.DataFrame({"taxa_alfabetizacao": [50.0, 150.0, -1.0, None]})
    assert validate_range(df, "taxa_alfabetizacao", 0, 100) == 2


def test_validate_duplicates_conta_chaves_repetidas():
    df = pd.DataFrame(
        {
            "ano": [2023, 2023, 2023],
            "id_aluno": ["a1", "a1", "a2"],
        }
    )
    assert validate_duplicates(df, ["ano", "id_aluno"]) == 1


def test_validate_relationship_detecta_chave_sem_referencia():
    df = pd.DataFrame(
        {
            "ano": [2023, 2023],
            "id_municipio": ["3550308", "9999999"],
        }
    )
    reference = pd.DataFrame(
        {
            "ano": [2023],
            "id_municipio": ["3550308"],
        }
    )
    assert validate_relationship(
        df,
        reference,
        columns=["ano", "id_municipio"],
        reference_columns=["ano", "id_municipio"],
    ) == 1


def test_profile_dataframe_estrutura():
    profile = profile_dataframe(_silver_municipio(), "municipio")
    assert profile["table_name"] == "municipio"
    assert profile["rows"] == 3
    assert "taxa_alfabetizacao" in profile["schema"]
    assert "taxa_alfabetizacao" in profile["numeric_summary"]


# ---------------------------------------------------------------------------
# Gold
# ---------------------------------------------------------------------------

def test_build_indicador_municipio():
    indicador = build_indicador_municipio({"municipio": _silver_municipio()})

    assert "taxa_alfabetizacao" in indicador.columns
    assert len(indicador) == 3
    # ordenado por município e ano
    assert indicador.iloc[0]["id_municipio"] == "3304557"


def test_build_comparativo_metas_resultados():
    comparativo = build_comparativo_metas_resultados(
        {
            "municipio_integrado": _silver_municipio_integrado(),
            "uf_integrado": _silver_uf_integrado(),
            "meta_brasil": _silver_meta_brasil(),
        }
    )

    assert set(comparativo["nivel_geografico"].unique()) == {
        "municipio",
        "uf",
        "brasil",
    }

    # município: 2 metas 2024 + 1 meta 2025 (a nula é descartada) = 3 linhas
    assert (comparativo["nivel_geografico"] == "municipio").sum() == 3
    # brasil: metas 2024 e 2030 = 2 linhas
    assert (comparativo["nivel_geografico"] == "brasil").sum() == 2

    rio_2024 = comparativo[
        (comparativo["id_municipio"] == "3304557")
        & (comparativo["ano_meta"] == 2024)
    ].iloc[0]

    # taxa 70 x meta 65: gap negativo e meta atingida
    assert rio_2024["gap_para_meta"] == -5.0
    assert bool(rio_2024["atingiu_meta"]) is True

    sp_2024 = comparativo[
        (comparativo["id_municipio"] == "3550308")
        & (comparativo["ano_meta"] == 2024)
    ].iloc[0]

    # taxa 55 x meta 60: falta 5 pontos e meta não atingida
    assert sp_2024["gap_para_meta"] == 5.0
    assert bool(sp_2024["atingiu_meta"]) is False


def test_build_evolucao_temporal():
    evolucao = build_evolucao_temporal(
        {
            "municipio": _silver_municipio(),
            "uf": _silver_uf(),
            "meta_brasil": _silver_meta_brasil(),
        }
    )

    # 3 linhas de município + 2 de UF + 1 do Brasil
    assert len(evolucao) == 6
    assert set(evolucao["nivel_geografico"].unique()) == {
        "municipio",
        "uf",
        "brasil",
    }

    sp = evolucao[
        (evolucao["nivel_geografico"] == "municipio")
        & (evolucao["id_municipio"] == "3550308")
    ]

    # série temporal ordenada por ano
    assert sp["ano"].tolist() == [2023, 2024]
    assert sp["taxa_alfabetizacao"].tolist() == [55.0, 65.0]


def test_build_desempenho_alunos_municipio():
    desempenho = build_desempenho_alunos_municipio(
        {"alunos_integrado": _silver_alunos_integrado()}
    )

    assert len(desempenho) == 2

    sao_paulo = desempenho[desempenho["id_municipio"] == "3550308"].iloc[0]

    assert sao_paulo["total_alunos"] == 2
    # média ponderada: (700*1 + 800*3) / (1 + 3) = 775
    assert sao_paulo["proficiencia_media_ponderada"] == 775.0
    # 1 alfabetizado entre 2 alunos
    assert sao_paulo["pct_alfabetizados"] == 50.0
    assert sao_paulo["taxa_alfabetizacao_municipio"] == 55.0


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

def test_build_event_gera_evento_valido():
    event = build_event()
    assert validate_event(event) == []
    assert event["alfabetizado"] in ("Sim", "Não")
    assert event["proficiencia"] >= 0


def test_validate_event_detecta_erros():
    event = build_event()
    event["id_aluno"] = None
    event["proficiencia"] = -10.0

    errors = validate_event(event)

    assert "campo_obrigatorio_ausente:id_aluno" in errors
    assert "proficiencia_negativa" in errors


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    passed = 0
    for test in tests:
        test()
        print(f"OK - {test.__name__}")
        passed += 1
    print(f"\n{passed}/{len(tests)} testes passaram.")


if __name__ == "__main__":
    _run_all()
