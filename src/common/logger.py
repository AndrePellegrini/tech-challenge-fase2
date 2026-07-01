"""
Logger padronizado para as pipelines.

Mantém o mesmo formato de log já adotado na camada Bronze, permitindo
observabilidade básica (início, fim e falhas de cada etapa da pipeline).
"""
import logging

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado com o formato padrão do projeto."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger
