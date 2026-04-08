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

# Checks if path is within project
# Use this to check if a path is safe to use
def is_internal(path):
    return path.is_relative_to(get_projet_root())
