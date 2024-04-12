"""
Name: utils.py
definition: Useful functions
Contributors: Nicholas Lee

Notes:
- Using for general work
"""

import datetime
import os
import pathlib
import logging.config
from pathlib import Path
from datetime import datetime
import re
import yaml
import pandas as pd
import numpy as np


def display_full_table(df: object):
    """Show data table without width restrictions

    Args:
        df (dataFrame): _description_
    """
    with pd.option_context("display.max_colwidth", None):
        print(df)


def get_time():
    """Create time stamp with format YYYY-MM-DD.Hr-Min

    Returns:
        string: current date and time
    """
    time_stamp = datetime.datetime.now()
    time_stamp = time_stamp.strftime("%Y-%m-%d.%H-%M")
    return time_stamp


def load_and_backup_dm(file_path: str, output_dir: str):
    """Create backup of data model with time stamp.

    Args:
        file_path (string):  path to CSV
    Returns:
        object: Data frame object
    """

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    dm = pd.read_csv(file_path, index_col=False)

    # write out old data model before changes
    file_path = pathlib.Path(file_path).stem + "-" + get_time() + ".csv"

    output_path = pathlib.Path(output_dir, file_path)

    dm.to_csv(output_path, index=False)

    return dm


def clean_list(string):
    """Takes a list represented as a string and returns only unique values found

    Args:
        string (str): list represented as string

    Returns:
        string: list as string of unique values
    """

    new_list = string.split(",")
    new_list = [n.strip() for n in new_list if n != "nan"]
    new_list = ",".join(sorted(list(np.unique(new_list)))).strip(",")
    return new_list


def display_full_table(df: object):
    """Show data table without width restrictions

    Args:
        df (dataFrame): _description_
    """
    with pd.option_context("display.max_colwidth", None):
        display(df)


def get_time():
    """Create time stamp with format YYYY-MM-DD.Hr-Min

    Returns:
        string: current date and time
    """
    time_stamp = datetime.datetime.now()
    time_stamp = time_stamp.strftime("%Y-%m-%d.%H-%M")
    return time_stamp


def add_logger(logger_file_path: str):
    """Create a logger object to store information to a file"""
    cwd = Path(__file__).resolve()

    ROOT_DIR_NAME = "ELITE-data-models"

    for p in cwd.parents:
        if bool(re.search(ROOT_DIR_NAME + "$", str(p))):
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


# def compare_dfs(df1, df2, index_keys:list, keys: list) -> pd.DataFrame:

#     # index_keys = ['Attribute']
#     # keys = ['dm', 'new_term']

#     # df1 = dm[dm["Attribute"].isin(new_term_df["Attribute"])].dropna(how="all", axis=1)
#     # df2 = new_term_df[new_term_df["Attribute"].isin(dm["Attribute"])].dropna(how = 'all', axis = 1)

#     df1 = df1..dropna(how="all", axis=1)
#     df2 = .dropna(how="all", axis=1)

#     df = pd.concat(
#         [df1.set_index(index_keys), df2.set_index(index_keys)],
#         keys=keys,
#         axis=1,
#     ).sort_index(level=1, axis=1)

#     print(df.stack())

#     return df.stack()
