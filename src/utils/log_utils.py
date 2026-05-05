import logging

from .paths import get_logs_dir

_root_logger = None
_logger = None

FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATEFMT = "%Y-%m-%d %H:%M"
RESET = "\033[0m"
COLOURS = {
    "red":     "\033[31m",
    "green":   "\033[32m",
    "yellow":  "\033[33m",
    "blue":    "\033[34m",
    "magenta": "\033[35m",
    "cyan":    "\033[36m",
}

class _ColourFormatter(logging.Formatter):
    def __init__(self, colour):
        super().__init__(fmt=FMT, datefmt=DATEFMT)
        self._prefix = COLOURS.get(colour, "")
        self._reset = RESET if self._prefix else ""

    def format(self, record):
        if record.levelname == "CRITICAL" or record.levelname == "ERROR":
            return f"{COLOURS.get("red", "")}{super().format(record)}{RESET}"
        else:
            return f"{self._prefix}{super().format(record)}{self._reset}"

def setup_logging_local(local_path):
    setup_logging_basic(colour="")
    to_latest = logging.FileHandler(local_path / "latest.log", mode="w", encoding="utf-8")
    to_archive = logging.FileHandler(local_path / "archive.log", mode="a", encoding="utf-8")


    to_latest.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATEFMT))
    to_archive.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATEFMT))
    _root_logger.addHandler(to_latest)
    _root_logger.addHandler(to_archive)

def setup_logging_basic(colour="yellow"):
    global _root_logger, _logger
    _root_logger = logging.getLogger()
    _logger = logging.getLogger(__name__)

    # 2026-04-08 12:25 - __main__ - INFO - This is a test

    to_console = logging.StreamHandler()
    to_console.setFormatter(_ColourFormatter(colour))

    logging.basicConfig(
        level = logging.DEBUG, # Most detailed info for development
        handlers = [to_console]
    )
    _logger.info("Set up basic logging successfully.")

def setup_logging_to_files():
    # Early logs created, caught by to_console only
    LOGS_DIR = get_logs_dir()

    to_latest = logging.FileHandler(LOGS_DIR / "latest.orchestrator.log", mode="w", encoding="utf-8")
    to_archive = logging.FileHandler(LOGS_DIR / "archive.orchestrator.log", mode="a", encoding="utf-8")

    to_latest.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATEFMT))
    to_archive.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATEFMT))
    
    _root_logger.addHandler(to_latest)
    _root_logger.addHandler(to_archive)

    _logger.info("Set up logging to files successfully.")

def setup_server_logging(server_name):
    LOGS_DIR = get_logs_dir()

    colour = ""
    match server_name:
        case "collector":
            colour = "blue"
        case "summariser":
            colour = "green"
        case "analyst":
            colour = "magenta"

    setup_logging_basic(colour)

    to_latest = logging.FileHandler(LOGS_DIR / f"latest.{server_name}.log", mode="w", encoding="utf-8")
    to_archive = logging.FileHandler(LOGS_DIR / f"archive.{server_name}.log", mode="a", encoding="utf-8")

    to_latest.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATEFMT))
    to_archive.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATEFMT))

    _root_logger.addHandler(to_latest)
    _root_logger.addHandler(to_archive)

def clear_archive():
    LOGS_DIR = get_logs_dir()
    ARCHIVE_PATH = LOGS_DIR / "archive.log"
    ARCHIVE_PATH.write_text('')
