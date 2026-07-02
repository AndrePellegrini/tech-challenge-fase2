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
    },
    "municipio": {
        "description": "Indicadores agregados por município.",
        "primary_key": ["ano", "id_municipio", "rede"],
        "required_columns": ["ano", "id_municipio", "rede"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
        },
        "categorical_columns": ["serie", "rede"],
    },
    "uf": {
        "description": "Indicadores agregados por unidade da federação.",
        "primary_key": ["ano", "sigla_uf", "rede"],
        "required_columns": ["ano", "sigla_uf", "rede"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
        },
        "categorical_columns": ["serie", "rede"],
    },
    "meta_municipio": {
        "description": "Metas de alfabetização por município.",
        "primary_key": ["ano", "id_municipio"],
        "required_columns": ["ano", "id_municipio"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
            "percentual_participacao": {"min": 0, "max": 100},
        },
        "categorical_columns": ["rede"],
    },
    "meta_uf": {
        "description": "Metas de alfabetização por unidade da federação.",
        "primary_key": ["ano", "sigla_uf"],
        "required_columns": ["ano", "sigla_uf"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
            "percentual_participacao": {"min": 0, "max": 100},
        },
        "categorical_columns": ["rede"],
    },
    "meta_brasil": {
        "description": "Metas nacionais de alfabetização.",
        "primary_key": ["ano"],
        "required_columns": ["ano"],
        "range_rules": {
            "taxa_alfabetizacao": {"min": 0, "max": 100},
            "percentual_participacao": {"min": 0, "max": 100},
        },
        "categorical_columns": ["rede"],
    },
}