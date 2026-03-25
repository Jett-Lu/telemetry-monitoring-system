import logging
import os

import psycopg2


LOG_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "sentinel.log",
)
logger = logging.getLogger(__name__)


def configure_logging():
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH),
        ],
    )


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set.")
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    try:
        return psycopg2.connect(database_url)
    except Exception:
        logger.exception("Failed to connect to PostgreSQL.")
        raise
