import os

from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "alfabetizacao.alunos.eventos")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "alfabetizacao-consumer")

# Quantidade de eventos acumulados antes de gravar um micro-batch Parquet.
STREAMING_BATCH_SIZE = int(os.getenv("STREAMING_BATCH_SIZE", "50"))

# Tempo (ms) sem novos eventos até o consumer gravar o que tiver e encerrar.
STREAMING_IDLE_TIMEOUT_MS = int(os.getenv("STREAMING_IDLE_TIMEOUT_MS", "30000"))

# Prefixos de gravação no Data Lake.
STREAMING_PREFIX = "streaming/alunos_eventos"
STREAMING_INVALID_PREFIX = "streaming/alunos_eventos_invalidos"
