from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.silver.reader import read_layer_table

# ========================================
# Configuração da página
# ========================================

st.set_page_config(
    page_title="Pipeline de Alfabetização",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Pipeline de Dados para Análise da Alfabetização no Brasil")

st.markdown(
    """
    Dashboard desenvolvido para o Tech Challenge.

    Os dados exibidos são provenientes da camada **Gold** do Data Lake.
    """
)

# ========================================
# Leitura dos dados
# ========================================

with st.spinner("Carregando dados..."):

    evolucao = read_layer_table(
        layer="gold",
        table_name="evolucao_temporal_indicador",
    )

st.success(
    f"{len(evolucao):,} registros carregados."
)

# ========================================
# KPIs
# ========================================

st.subheader("Visão Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Registros",
        f"{len(evolucao):,}"
    )

with col2:
    st.metric(
        "UFs",
        evolucao["sigla_uf"].dropna().nunique()
    )

with col3:
    st.metric(
        "Municípios",
        evolucao["id_municipio"].dropna().nunique()
    )

with col4:
    st.metric(
        "IDHM médio",
        f"{evolucao['idhm'].dropna().mean():.3f}"
    )

st.divider()

# ========================================
# Filtros
# ========================================

st.subheader("Filtros")

anos = sorted(
    evolucao.loc[
        evolucao['taxa_alfabetizacao'].notna(),
        'ano'
    ].unique()
)

ano_selecionado = st.selectbox(
    "Ano",
    anos,
    index = len(anos) - 1,
)

df = evolucao[
    evolucao["ano"] == ano_selecionado
].copy()

redes = sorted(
    df.loc[
        df['nivel_geografico'] != 'brasil',
        'rede'
    ].unique()
)

rede = st.selectbox(
    'Rede',
    redes,
)

df = df[
    df["rede"] == rede
]

st.divider()

# ========================================
# Taxa por UF
# ========================================

st.subheader("Taxa de Alfabetização por UF")

uf_df = (
    df[
        df["nivel_geografico"] == "uf"
    ]
    .sort_values(
        "taxa_alfabetizacao",
        ascending=False,
    )
)

fig = px.bar(
    uf_df,
    x = "sigla_uf",
    y = "taxa_alfabetizacao",
    color = "taxa_alfabetizacao",
    labels = {
        "sigla_uf": "UF",
        "taxa_alfabetizacao": "Taxa de Alfabetização (%)",
    },
    title=f"Taxa de Alfabetização por UF ({ano_selecionado})",
)

st.plotly_chart(
    fig,
    width="stretch",
)

st.divider()

# ========================================
# IDHM x Taxa
# ========================================

st.subheader("IDHM × Taxa de Alfabetização")

fig = px.scatter(
    uf_df,
    x="idhm",
    y="taxa_alfabetizacao",
    hover_name="sigla_uf_nome",
    color="taxa_alfabetizacao",
    labels={
        "idhm": "IDHM",
        "taxa_alfabetizacao": "Taxa de Alfabetização (%)",
    },
    title=f"IDHM x Taxa de Alfabetização ({ano_selecionado})",
    trendline = 'ols',
)

st.plotly_chart(
    fig,
    width="stretch",
)

st.divider()

# ========================================
# Dados
# ========================================

st.subheader("Dados utilizados")

st.dataframe(
    uf_df[
        [
            "sigla_uf",
            "sigla_uf_nome",
            "rede",
            "taxa_alfabetizacao",
            "idhm",
            "idhm_educacao",
            "idhm_renda",
            "idhm_longevidade",
        ]
    ],
    width="stretch",
)