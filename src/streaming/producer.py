"""
Producer Kafka: publica eventos simulados de avaliação de alunos.

Uso:
    python -m src.streaming.producer --total 100 --intervalo 0.2
"""
import argparse
import json
import logging
import time

from kafka import KafkaProducer

from src.streaming.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
from src.streaming.events import build_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def create_producer() -> KafkaProducer:
    """
    Cria o producer Kafka com serialização JSON.
    """

    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8"),
        acks="all",
    )


def run_producer(total_events: int, interval_seconds: float) -> None:
    """
    Publica eventos simulados no tópico Kafka.
    """

    producer = create_producer()

    logging.info(
        f"Iniciando producer | topico={KAFKA_TOPIC} | "
        f"bootstrap={KAFKA_BOOTSTRAP_SERVERS} | eventos={total_events}"
    )

    try:
        for sequence in range(1, total_events + 1):
            event = build_event()

            producer.send(
                KAFKA_TOPIC,
                key=event["id_municipio"],
                value=event,
            )

            logging.info(
                f"Evento {sequence}/{total_events} publicado | "
                f"id_evento={event['id_evento']} | "
                f"municipio={event['id_municipio_nome']} | "
                f"proficiencia={event['proficiencia']}"
            )

            time.sleep(interval_seconds)

        producer.flush()

    finally:
        producer.close()

    logging.info(f"Producer finalizado: {total_events} eventos publicados.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publica eventos simulados de avaliação de alunos no Kafka."
    )
    parser.add_argument(
        "--total",
        type=int,
        default=100,
        help="Quantidade de eventos a publicar (padrão: 100).",
    )
    parser.add_argument(
        "--intervalo",
        type=float,
        default=0.2,
        help="Intervalo em segundos entre eventos (padrão: 0.2).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_producer(total_events=args.total, interval_seconds=args.intervalo)
