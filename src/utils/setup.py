from .paths import setup_dirs
from .log_utils import setup_logging_basic, setup_logging_to_files

def setup():
    setup_logging_basic()
    setup_dirs()
    setup_logging_to_files()
