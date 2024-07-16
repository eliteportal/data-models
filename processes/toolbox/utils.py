""" 
Utility functions to help with creating data dictionary

"""

from pathlib import Path
import re
import logging.config
from datetime import datetime
import yaml


def get_root_dir(root_dir_name: str):
    """Find the root directory for a file to get the base of the repo"""
    cwd = Path(__file__).resolve()

    ROOT_DIR = None

    for p in cwd.parents:
        if bool(re.search(root_dir_name + "$", str(p))):
            print(p)
            ROOT_DIR = p
            return ROOT_DIR

    if ROOT_DIR is None:
        raise ValueError("No root directory found")


def add_logger(root_dir_name: str, logger_file_path: str):
    """Create a logger object to store information to a file"""
    cwd = Path(__file__).resolve()

    for p in cwd.parents:
        if bool(re.search(str(root_dir_name) + "$", str(p))):
            print(p)
            ROOT_DIR = p

    timestamp = datetime.now().strftime("%Y-%m-%d")

    # Create logger for reports
    with open(Path(ROOT_DIR, "_logs", "logging.yaml"), "r", encoding="UTF-8") as f:
        yaml_config = yaml.safe_load(f)
        logging.config.dictConfig(yaml_config)

    logger = logging.getLogger("default")

    fh = logging.FileHandler(
        filename=Path(ROOT_DIR, "_logs", "_".join([timestamp, logger_file_path]))
    )
    fh.setFormatter(logger.handlers[0].__dict__["formatter"])

    logger.addHandler(fh)

    return logger
