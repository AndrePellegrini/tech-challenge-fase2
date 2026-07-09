import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger configurado para o módulo informado.
    """

    return logging.getLogger(name)

