"""
Eventos de avaliação de alunos usados no streaming.

Define a geração de eventos simulados (producer) e a validação de qualidade
aplicada na chegada (consumer), espelhando as regras da tabela `alunos`
definidas no catálogo da camada Silver.
"""
import random
import uuid
from datetime import datetime, UTC

MUNICIPIOS = [
    {"id_municipio": "3550308", "id_municipio_nome": "São Paulo", "sigla_uf": "SP"},
    {"id_municipio": "3304557", "id_municipio_nome": "Rio de Janeiro", "sigla_uf": "RJ"},
    {"id_municipio": "3106200", "id_municipio_nome": "Belo Horizonte", "sigla_uf": "MG"},
    {"id_municipio": "2927408", "id_municipio_nome": "Salvador", "sigla_uf": "BA"},
    {"id_municipio": "4106902", "id_municipio_nome": "Curitiba", "sigla_uf": "PR"},
    {"id_municipio": "2304400", "id_municipio_nome": "Fortaleza", "sigla_uf": "CE"},
]

REDES = ["Municipal", "Estadual", "Federal", "Privada"]
PRESENCAS = ["Presente", "Ausente"]

# Proficiência a partir da qual o aluno é considerado alfabetizado (INEP: 743).
PROFICIENCIA_ALFABETIZACAO = 743.0

REQUIRED_FIELDS = ["id_evento", "ts_evento", "ano", "id_aluno", "id_municipio"]


def build_event() -> dict:
    """
    Gera um evento simulado de avaliação de alfabetização de um aluno.
    """

    municipio = random.choice(MUNICIPIOS)
    proficiencia = round(max(random.gauss(750, 100), 0), 2)

    return {
        "id_evento": str(uuid.uuid4()),
        "ts_evento": datetime.now(UTC).isoformat(),
        "ano": datetime.now(UTC).year,
        "id_municipio": municipio["id_municipio"],
        "id_municipio_nome": municipio["id_municipio_nome"],
        "sigla_uf": municipio["sigla_uf"],
        "id_escola": str(random.randint(11000000, 53999999)),
        "id_aluno": str(uuid.uuid4()),
        "serie": "2º ano",
        "rede": random.choice(REDES),
        "presenca": random.choices(PRESENCAS, weights=[95, 5])[0],
        "preenchimento_caderno": "Sim",
        "alfabetizado": "Sim" if proficiencia >= PROFICIENCIA_ALFABETIZACAO else "Não",
        "proficiencia": proficiencia,
        "peso_aluno": round(random.uniform(0.5, 2.0), 4),
    }


def validate_event(event: dict) -> list[str]:
    """
    Valida um evento recebido do Kafka e retorna a lista de erros
    encontrados (vazia quando o evento é válido).
    """

    errors = []

    for field in REQUIRED_FIELDS:
        if event.get(field) in (None, ""):
            errors.append(f"campo_obrigatorio_ausente:{field}")

    proficiencia = event.get("proficiencia")
    if proficiencia is not None and proficiencia < 0:
        errors.append("proficiencia_negativa")

    peso_aluno = event.get("peso_aluno")
    if peso_aluno is not None and peso_aluno < 0:
        errors.append("peso_aluno_negativo")

    return errors
