from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "cblob-image-sync",
    level: str | None = None,
) -> logging.Logger:
    """
    Configura y devuelve un logger con:
    - consola
    - fichero rotativo
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # evita duplicados

    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(log_level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Consola ---
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # --- Fichero ---
    log_dir = Path(os.getenv("LOG_DIR", "./logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / os.getenv("LOG_FILE", "cblob-image-sync.log")

    fh = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.propagate = False
    return logger