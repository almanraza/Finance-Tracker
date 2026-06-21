import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console output
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.APP_ENV == "development" else "INFO",
        colorize=True,
    )

    # File output — rotates daily, keeps 7 days
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="INFO",
        rotation="00:00",
        retention="7 days",
        compression="zip",
    )

    logger.info(f"Logging initialized | ENV={settings.APP_ENV}")
