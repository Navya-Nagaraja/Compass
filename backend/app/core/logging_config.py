import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Structured, single-line logging so it's easy to ship to any
    log aggregator (CloudWatch, Loki, Stackdriver, etc.)."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Quiet down noisy third-party loggers.
    for noisy in ("httpx", "sentence_transformers", "faiss"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
