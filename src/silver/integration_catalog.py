INTEGRATION_CATALOG = {
    "alunos_integrado": {
        "base_table": "alunos",
        "joins": [
            {
                "reference_table": "municipio",
                "on": ["ano", "id_municipio"],
                "how": "left",
            }
        ],
    },

    "municipio_integrado": {
        "base_table": "municipio",
        "joins": [
            {
                "reference_table": "meta_municipio",
                "on": ["ano", "id_municipio"],
                "how": "left",
            }
        ],
    },

    "uf_integrado": {
        "base_table": "uf",
        "joins": [
            {
                "reference_table": "meta_uf",
                "on": ["ano", "sigla_uf"],
                "how": "left",
            }
        ],
    },
}