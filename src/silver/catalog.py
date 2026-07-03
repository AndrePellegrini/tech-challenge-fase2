TABLE_CATALOG = {
    "alunos": {
        "description": "Dados individuais dos alunos participantes da avaliação.",
        "primary_key": ["ano", "id_aluno"],
        "required_columns": ["ano", "id_aluno"],
        "range_rules": {
            "proficiencia": {"min": 0, "max": None},
            "peso_aluno": {"min": 0, "max": None},
        },
        "categorical_columns": [
            "serie",
            "rede",
            "presenca",
            "preenchimento_caderno",
            "alfabetizado",
        ],
        "relationship_rules": [
            {
                "columns": ["ano", "id_municipio"],
                "reference_table": "municipio",
                "reference_columns": ["ano", "id_municipio"],
            }
        ],
    },

    "municipio": {
        "description": "Indicadores agregados por município.",
        "primary_key": ["ano", "id_municipio", "rede"],
        "required_columns": ["ano", "id_municipio", "rede"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
        },
        "categorical_columns": [
            "serie",
            "rede",
        ],
        "relationship_rules": [
            {
                "columns": ["ano", "id_municipio"],
                "reference_table": "meta_municipio",
                "reference_columns": ["ano", "id_municipio"],
            }
        ],
    },

    "uf": {
        "description": "Indicadores agregados por unidade da federação.",
        "primary_key": ["ano", "sigla_uf", "rede"],
        "required_columns": ["ano", "sigla_uf", "rede"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
        },
        "categorical_columns": [
            "serie",
            "rede",
        ],
        "relationship_rules": [
            {
                "columns": ["ano", "sigla_uf"],
                "reference_table": "meta_uf",
                "reference_columns": ["ano", "sigla_uf"],
            }
        ],
    },

    "meta_municipio": {
        "description": "Metas de alfabetização por município.",
        "primary_key": ["ano", "id_municipio"],
        "required_columns": ["ano", "id_municipio"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
            "percentual_participacao": {"min": 0, "max": 100},
        },
        "categorical_columns": [
            "rede",
        ],
        "relationship_rules": [],
    },

    "meta_uf": {
        "description": "Metas de alfabetização por unidade da federação.",
        "primary_key": ["ano", "sigla_uf"],
        "required_columns": ["ano", "sigla_uf"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
            "percentual_participacao": {"min": 0, "max": 100},
        },
        "categorical_columns": [
            "rede",
        ],
        "relationship_rules": [],
    },

    "meta_brasil": {
        "description": "Metas nacionais de alfabetização.",
        "primary_key": ["ano"],
        "required_columns": ["ano"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
            "percentual_participacao": {"min": 0, "max": 100},
        },
        "categorical_columns": [
            "rede",
        ],
        "relationship_rules": [],
    },
}