"""
Testes de lógica das camadas Silver e Gold com dados sintéticos.

Não dependem de AWS/S3: exercitam apenas as transformações e as regras de
qualidade (pandas puro). Podem ser executados com:

    python -m tests.test_silver_gold
"""
from datetime import datetime, timezone

import pandas as pd

from src.gold.transform import (
    build_comparativo_metas_resultados,
    build_evolucao_temporal,
    build_indicador_municipio,
)
from src.silver.profiling import profile_dataframe
from src.silver.quality import apply_quality
from src.silver.transform import (
    build_metas,
    transform_alfabetizacao_municipio,
    transform_alfabetizacao_uf,
    transform_alunos,
)


def _bronze_alunos() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023, 2023, 2023, None],           # última linha: ano nulo (inválida)
            "id_municipio": ["3550308", "3550308", "3304557.0", "3304557"],
            "id_municipio_nome": ["São Paulo", "São Paulo", "Rio", "Rio"],
            "id_escola": ["1", "1", "2", "3"],
            "id_aluno": ["a1", "a1", "a2", "a3"],       # a1 duplicado (remoção controlada)
            "caderno": ["A", "A", "B", "B"],
            "serie": ["2º ano", "2º ano", "2º ano", "2º ano"],
            "rede": ["Federal", "Federal", "Estadual", "Estadual"],
            "presenca": ["Presente"] * 4,
            "preenchimento_caderno": ["Sim"] * 4,
            "alfabetizado": ["Sim", "Sim", "Não", "Sim"],
            "proficiencia": [750.0, 750.0, -5.0, 800.0],  # -5 inválida (negativa)
            "peso_aluno": [1.0, 1.0, 1.2, 1.1],
            "_ingestion_ts": [datetime.now(timezone.utc)] * 4,
            "_source": ["basedosdados_inep"] * 4,
            "_table": ["alunos"] * 4,
        }
    )


def _bronze_municipio() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2021, 2022, 2023],
            "id_municipio": ["3550308", "3550308", "355030"],  # último com 6 dígitos (inválido)
            "id_municipio_nome": ["São Paulo", "São Paulo", "Errado"],
            "serie": ["2º ano"] * 3,
            "rede": ["Total"] * 3,
            "taxa_alfabetizacao": [55.0, 60.0, 150.0],  # 150 fora da faixa (inválida)
            "media_portugues": [700.0, 710.0, 720.0],
            **{f"proporcao_aluno_nivel_{i}": [0.1, 0.1, 0.1] for i in range(9)},
            "_ingestion_ts": [datetime.now(timezone.utc)] * 3,
            "_source": ["basedosdados_inep"] * 3,
            "_table": ["municipio"] * 3,
        }
    )


def _bronze_uf() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2021, 2022],
            "sigla_uf": ["sp", "SPP"],  # SPP tem 3 caracteres (inválido)
            "sigla_uf_nome": ["São Paulo", "São Paulo"],
            "serie": ["2º ano"] * 2,
            "rede": ["Total"] * 2,
            "taxa_alfabetizacao": [58.0, 62.0],
            "media_portugues": [705.0, 715.0],
            **{f"proporcao_aluno_nivel_{i}": [0.1, 0.1] for i in range(9)},
        }
    )


def _bronze_meta_brasil() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023],
            "rede": ["Total"],
            "taxa_alfabetizacao": [56.0],
            "meta_alfabetizacao_2024": [60.0],
            "meta_alfabetizacao_2025": [64.0],
            "meta_alfabetizacao_2030": [80.0],
            "percentual_participacao": [95.0],
        }
    )


def _bronze_meta_uf() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023],
            "sigla_uf": ["SP"],
            "sigla_uf_nome": ["São Paulo"],
            "rede": ["Total"],
            "taxa_alfabetizacao": [58.0],
            "meta_alfabetizacao_2024": [62.0],
            "meta_alfabetizacao_2030": [82.0],
            "percentual_participacao": [96.0],
        }
    )


def _bronze_meta_municipio() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano": [2023],
            "id_municipio": ["3550308"],
            "id_municipio_nome": ["São Paulo"],
            "rede": ["Total"],
            "taxa_alfabetizacao": [55.0],
            "meta_alfabetizacao_2024": [61.0],
            "meta_alfabetizacao_2030": [81.0],
            "nivel_alfabetizacao": ["Intermediário"],
            "percentual_participacao": [94.0],
        }
    )


def test_transform_alunos_remove_duplicatas_e_padroniza():
    df = transform_alunos(_bronze_alunos())
    # id_municipio "3304557.0" deve virar "3304557"
    assert (df["id_municipio"].str.len() == 7).all()
    # duplicata (ano, id_aluno=a1, ...) removida -> 3 linhas
    assert len(df) == 3
    # metadados bronze removidos
    assert "_ingestion_ts" not in df.columns


def test_quality_alunos_separa_invalidos():
    df = transform_alunos(_bronze_alunos())
    result = apply_quality(df, "alunos")
    # proficiencia -5 é inválida
    assert result.report["falhas_por_regra"]["proficiencia_nao_negativa"] >= 1
    assert result.report["registros_invalidos"] >= 1
    assert "_quality_errors" in result.invalid.columns


def test_quality_municipio_faixa_e_ibge():
    df = transform_alfabetizacao_municipio(_bronze_municipio())
    result = apply_quality(df, "alfabetizacao_municipio")
    falhas = result.report["falhas_por_regra"]
    assert falhas["taxa_entre_0_100"] >= 1          # taxa 150
    assert falhas["id_municipio_ibge_7_digitos"] >= 1  # id de 6 dígitos


def test_quality_uf_sigla():
    df = transform_alfabetizacao_uf(_bronze_uf())
    result = apply_quality(df, "alfabetizacao_uf")
    assert result.report["falhas_por_regra"]["sigla_uf_2_caracteres"] >= 1  # SPP
    # 'sp' deve ter sido padronizado para 'SP'
    assert "SP" in df["sigla_uf"].tolist()


def test_build_metas_consolida_niveis():
    metas = build_metas(
        _bronze_meta_brasil(), _bronze_meta_uf(), _bronze_meta_municipio()
    )
    assert set(metas["nivel_geografico"].unique()) == {"brasil", "uf", "municipio"}
    assert "ano_meta" in metas.columns
    assert "meta_alfabetizacao" in metas.columns
    # formato longo: mais de uma linha por nível (vários anos-alvo)
    assert (metas["nivel_geografico"] == "brasil").sum() == 3


def test_gold_comparativo_e_evolucao():
    metas = build_metas(
        _bronze_meta_brasil(), _bronze_meta_uf(), _bronze_meta_municipio()
    )
    silver_metas = apply_quality(metas, "metas").valid

    comparativo = build_comparativo_metas_resultados(silver_metas)
    assert "gap_para_meta" in comparativo.columns
    assert "atingiu_meta" in comparativo.columns

    evolucao = build_evolucao_temporal(silver_metas)
    # evolução deve ter uma linha por nível/localidade/ano (sem duplicar por ano_meta)
    assert len(evolucao) == 3  # brasil, uf, municipio (1 ano cada)


def test_gold_indicador_municipio():
    df = transform_alfabetizacao_municipio(_bronze_municipio())
    silver = apply_quality(df, "alfabetizacao_municipio").valid
    indicador = build_indicador_municipio(silver)
    assert "taxa_alfabetizacao" in indicador.columns
    assert len(indicador) >= 1


def test_profiling_estrutura():
    profile = profile_dataframe(_bronze_municipio(), "alfabetizacao_municipio")
    assert profile["linhas"] == 3
    assert "estatisticas_numericas" in profile
    assert any(c["coluna"] == "taxa_alfabetizacao" for c in profile["schema"])


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
