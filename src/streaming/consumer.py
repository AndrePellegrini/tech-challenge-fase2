"""
Consumer Kafka: consome eventos de avaliação de alunos, valida a qualidade
e grava micro-batches Parquet no Data Lake (S3 ou diretório local).

Eventos válidos vão para `streaming/alunos_eventos/` e eventos reprovados na
validação vão para `streaming/alunos_eventos_invalidos/`, ambos particionados
por data de ingestão.

Uso:
    python -m src.streaming.consumer                # grava no S3
    python -m src.streaming.consumer --sink local   # grava em tmp/ (sem AWS)
"""
import argparse
import json
import logging
from datetime import datetime, UTC
from pathlib import Path

import pandas as pd
from kafka import KafkaConsumer

from src.streaming.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_CONSUMER_GROUP,
    KAFKA_TOPIC,
    STREAMING_BATCH_SIZE,
    STREAMING_IDLE_TIMEOUT_MS,
    STREAMING_INVALID_PREFIX,
    STREAMING_PREFIX,
)
from src.streaming.events import validate_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

TMP_DIR = Path("tmp")


def create_consumer() -> KafkaConsumer:
    """
    Cria o consumer Kafka com desserialização JSON.

    O `consumer_timeout_ms` encerra o loop quando não chegam novos eventos,
    permitindo gravar o que restou no buffer e finalizar o processo.
    """

    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_CONSUMER_GROUP,
        value_deserializer=lambda message: json.loads(message.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        consumer_timeout_ms=STREAMING_IDLE_TIMEOUT_MS,
    )


def add_streaming_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona metadados técnicos de ingestão streaming.
    """

    df = df.copy()

    df["_ingestion_ts"] = datetime.now(UTC)
    df["_source"] = "kafka_stream"
    df["_table"] = "alunos_eventos"

    return df


def write_batch(events: list[dict], prefix: str, sink: str) -> str:
    """
    Grava um micro-batch de eventos como Parquet no destino escolhido.
    """

    df = add_streaming_metadata(pd.DataFrame(events))

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    file_name = f"eventos_{datetime.now(UTC).strftime('%H%M%S_%f')}.parquet"
    relative_key = f"{prefix}/ingestion_date={today}/{file_name}"

    if sink == "local":
        file_path = TMP_DIR / relative_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(file_path, index=False)
        return str(file_path)

    # Importação tardia: o sink local funciona sem credenciais AWS no .env.
    from src.bronze.aws_client import create_s3_client
    from src.bronze.config import S3_BUCKET_NAME

    TMP_DIR.mkdir(exist_ok=True)
    file_path = TMP_DIR / file_name

    df.to_parquet(file_path, index=False)

    try:
        s3 = create_s3_client()
        s3.upload_file(str(file_path), S3_BUCKET_NAME, relative_key)
    finally:
        if file_path.exists():
            file_path.unlink()

    return f"s3://{S3_BUCKET_NAME}/{relative_key}"


def flush_buffers(
        valid_events: list[dict],
        invalid_events: list[dict],
        sink: str,
) -> None:
    """
    Grava e esvazia os buffers de eventos válidos e inválidos.
    """

    if valid_events:
        destination = write_batch(valid_events, STREAMING_PREFIX, sink)
        logging.info(
            f"Micro-batch gravado: {len(valid_events)} eventos validos | {destination}"
        )
        valid_events.clear()

    if invalid_events:
        destination = write_batch(invalid_events, STREAMING_INVALID_PREFIX, sink)
        logging.warning(
            f"Micro-batch de invalidos gravado: {len(invalid_events)} eventos | {destination}"
        )
        invalid_events.clear()


def run_consumer(sink: str) -> None:
    """
    Consome eventos do Kafka, valida e grava micro-batches Parquet.
    """

    consumer = create_consumer()

    logging.info(
        f"Iniciando consumer | topico={KAFKA_TOPIC} | "
        f"bootstrap={KAFKA_BOOTSTRAP_SERVERS} | grupo={KAFKA_CONSUMER_GROUP} | "
        f"batch={STREAMING_BATCH_SIZE} | sink={sink}"
    )

    valid_events: list[dict] = []
    invalid_events: list[dict] = []
    total_valid = 0
    total_invalid = 0

    try:
        for message in consumer:
            event = message.value
            errors = validate_event(event)

            if errors:
                event["_quality_errors"] = ";".join(errors)
                invalid_events.append(event)
                total_invalid += 1
                logging.warning(
                    f"Evento invalido | id_evento={event.get('id_evento')} | erros={errors}"
                )
            else:
                valid_events.append(event)
                total_valid += 1

            if len(valid_events) + len(invalid_events) >= STREAMING_BATCH_SIZE:
                flush_buffers(valid_events, invalid_events, sink)

        logging.info("Sem novos eventos; gravando buffers restantes.")

    finally:
        flush_buffers(valid_events, invalid_events, sink)
        consumer.close()

    logging.info(
        f"Consumer finalizado | validos={total_valid} | invalidos={total_invalid}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consome eventos de avaliação de alunos do Kafka e grava no Data Lake."
    )
    parser.add_argument(
        "--sink",
        choices=["s3", "local"],
        default="s3",
        help="Destino dos micro-batches: s3 (padrão) ou local (tmp/).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_consumer(sink=args.sink)
