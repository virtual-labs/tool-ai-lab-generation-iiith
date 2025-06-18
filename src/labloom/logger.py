import os
import atexit
import logging.config

logger = logging.getLogger("labloom")

log_dir = os.environ.get("LABLOOM_LOG_DIR", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "labloom.jsonl")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s [%(levelname)s|%(module)s|L%(lineno)d]: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 format
        },
        "simple": {
            "format": "%(name)s - %(levelname)s - %(message)s",
        },
        "jsonl": {
            "()": "labloom.utils.JsonlFormatter",
            "fmt_keys": {
                "level": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "logger": "name",
                "module": "module",
                "function": "funcName",
                "line": "lineno",
                "thread": "threadName",
            },
        },
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
            "filename": log_file,
            "formatter": "jsonl",
        },
        "queue_handler": {  # This handler is used to send log records to a queue
            "class": "logging.handlers.QueueHandler",
            "handlers": ["stderr", "file"],
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "labloom": {
            "level": "DEBUG",
            "handlers": ["queue_handler"],
            "propagate": False,
        },
    },
}


def setup_logging():
    """
    Set up logging configuration.
    """
    logging.config.dictConfig(logging_config)

    if queue_handler := logging.getHandlerByName("queue_handler"):
        queue_handler.listener.start()  # type: ignore
        atexit.register(queue_handler.listener.stop)  # type: ignore


setup_logging()
