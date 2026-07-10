GOLD_CATALOG = {
    "indicador_alfabetizacao_municipio": {
        "description": (
            "Indicador de alfabetização por município, rede e série, "
            "pronto para dashboards e análises."
        ),
        "sources": ["municipio_integrado"],
        "builder": "build_indicador_municipio",
    },

    "comparativo_metas_resultados": {
        "description": (
            "Comparação entre a taxa de alfabetização realizada e as metas "
            "por ano-alvo (2024-2030), nos níveis município, UF e Brasil, "
            "com gap e indicador de atingimento."
        ),
        "sources": ["municipio_integrado", "uf_integrado", "meta_brasil"],
        "builder": "build_comparativo_metas_resultados",
    },

    "evolucao_temporal_indicador": {
        "description": (
            "Evolução da taxa de alfabetização ao longo dos anos, "
            "por nível geográfico (município, UF e Brasil)."
        ),
        "sources": ["municipio_integrado", "uf_integrado", "meta_brasil"],
        "builder": "build_evolucao_temporal",
    },

    "desempenho_alunos_municipio": {
        "description": (
            "Desempenho agregado dos alunos por município e rede: volume, "
            "proficiência média ponderada e percentual de alfabetizados."
        ),
        "sources": ["alunos_integrado"],
        "builder": "build_desempenho_alunos_municipio",
    },
}
