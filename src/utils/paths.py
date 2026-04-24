from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# XX Note: Never reference directly, as it may not be initialised
# Instead, use get_project_root()
_project_root = None

def _find_root():
    def in_gdp(path):
        return "gdp-15-2026" in path.parts
    current = Path.cwd()
    if not in_gdp(current):
        logger.error("paths.py exists outside project scope")
        raise
    if (current / "pyproject.toml").exists():
        return current
    for parent in current.parents:
        if not in_gdp(parent):
            logger.error("Couldn't find project root")
            raise
        if (parent / "pyproject.toml").exists():
            return parent
    logger.error("Couldn't find project root")
    raise


# Use this to get the path to project root directory
def get_project_root():
    global _project_root
    if _project_root is None:
        _project_root = _find_root()
        logger.info(f"Project root = {_project_root}")
    return _project_root

def get_data_dir():
    return get_project_root() / "data"

def get_top_dir():
    return get_data_dir() / "daily"

def get_weekly_dir():
    return get_data_dir() / "weekly"

def get_monthly_dir():
    return get_data_dir() / "montly"

def get_range_dir():
    return get_data_dir() / "range"

def get_logs_dir():
    return get_project_root() / "logs"

# Checks if path is within project
# Use this to check if a path is safe to use
def is_internal(path):
    return path.is_relative_to(get_projet_root())

# Makes directories if they don't already exist
def setup_dirs():
    LOGS_DIR = get_logs_dir()
    TOP_DIR = get_top_dir()
    WEEKLY_DIR = get_weekly_dir()
    MONTHLY_DIR = get_monthly_dir()
    RANGE_DIR = get_range_dir()
    DIRS = [
        LOGS_DIR,
        TOP_DIR,
        WEEKLY_DIR,
        MONTHLY_DIR,
        RANGE_DIR
    ]
    for d in DIRS:
        d.mkdir(parents=True, exist_ok=True)
