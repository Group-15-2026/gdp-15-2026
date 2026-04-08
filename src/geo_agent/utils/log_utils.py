import logging
from pathlib import Path

from paths import get_project_root

def _setup_logging():
    root_logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M")
    # 2026-04-08 12:25 - __main__ - INFO - This is a test

    to_console = logging.StreamHandler()
    to_console.setFormatter(formatter)

    logging.basicConfig(
        level = logging.DEBUG, # Most detailed info for development
        handlers = [to_console]
    )
    
    # Early logs created, caught by to_console only
    LOG_DIR = get_project_root() / "logs"

    to_latest = logging.FileHandler(LOG_DIR / "latest.log", mode="w")
    to_archive = logging.FileHandler(LOG_DIR / "archive.log", mode="a")

    to_latest.setFormatter(formatter)
    to_archive.setFormatter(formatter)
    
    root_logger.addHandler(to_latest)
    root_logger.addHandler(to_archive)

    return LOG_DIR

def clear_archive(LOG_DIR):
    ARCHIVE_PATH = LOG_DIR / "archive.log"
    ARCHIVE_PATH.write_text('')

if __name__ == "__main__":
    LOG_DIR = _setup_logging()
    logger = logging.getLogger(__name__)
    clear_archive(LOG_DIR)
    logger.info("This is a test")
