import logging

from .paths import get_logs_dir

_root_logger = None
_logger = None
_formatter = None
LOGGING_LEVEL_MAP = logging.getLevelNamesMapping()

def setup_logging_basic():
    global _root_logger, _logger, _formatter
    _root_logger = logging.getLogger()
    _logger = logging.getLogger(__name__)

    _formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M")
    # 2026-04-08 12:25 - __main__ - INFO - This is a test

    to_console = logging.StreamHandler()
    to_console.setFormatter(_formatter)

    logging.basicConfig(
        level = logging.DEBUG, # Most detailed info for development
        handlers = [to_console]
    )
    _logger.info("Set up basic logging successfully.")

def setup_logging_to_files():
    # Early logs created, caught by to_console only
    LOGS_DIR = get_logs_dir()

    to_latest = logging.FileHandler(LOGS_DIR / "latest.log", mode="w", encoding="utf-8")
    to_archive = logging.FileHandler(LOGS_DIR / "archive.log", mode="a", encoding="utf-8")

    to_latest.setFormatter(_formatter)
    to_archive.setFormatter(_formatter)
    
    _root_logger.addHandler(to_latest)
    _root_logger.addHandler(to_archive)

    _logger.info("Set up logging to files successfully.")

def add_server_handlers(logger, name):
    LOGS_DIR = get_logs_dir()
    to_server_file = logging.FileHandler(LOGS_DIR / "server.log", mode="w", encoding="utf-8")
    to_name_file = logging.FileHandler(LOGS_DIR / f"{name}.log", mode="w", encoding="utf-8")
    logger.addHandler(to_server_file)
    logger.addHandler(to_server_file)

async def MCP_logging_callback(message):
    # Forward MCP Server logs to Python's logging system.
    msg = message.data.get('msg')
    extra = message.data.get('extra')
    
    level = LOGGING_LEVEL_MAP.get(message.level.upper(), logging.INFO) # defaults to logging.INFO if level fetch fails
    server_logger = logging.getLogger("server_logger")
    logger.log(level=level, msg="this is a message")

def clear_archive():
    LOGS_DIR = get_logs_dir()
    ARCHIVE_PATH = LOGS_DIR / "archive.log"
    ARCHIVE_PATH.write_text('')
