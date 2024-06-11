""" Join the data model modules """

from glob import glob
from pathlib import Path
import subprocess
import logging.config
from datetime import datetime
import re
import yaml
import pandas as pd
from utils import utils
import os

cwd = Path(__file__)

ROOT_DIR_NAME = "data-models" # this is the repo root dir; works in GH codespace but may need to be edited in other dev envs
JSONLD_NAME = "EL.data.model.jsonld"  # can do this in dev environment

ROOT_DIR = utils.get_root_dir(ROOT_DIR_NAME)

timestamp = datetime.now().strftime("%Y-%m-%d")

# Create logger for reports
logger = utils.add_logger(
    ROOT_DIR_NAME = ROOT_DIR_NAME,
    logger_config_path="_logs/logging.yaml",
    log_file_path=f"{str(cwd.parent)}/_logs/{timestamp}_join_data_model.log",
)


def join_data_model_partitions(partition_path):
    """Join the partitions back together to form the data model used in DCA

    Args:
        partition_path (str): directory containing the partitions as CSVs

    Returns:
        object: pandas dataframe
    """
    modules = glob(partition_path)

    print(modules)

    data_model = (
        pd.concat([pd.read_csv(m) for m in modules])
        .sort_values(by=["module", "Attribute"])
        .reset_index(drop=True)
        .fillna("")
    )

    print("Data model shape BEFORE cleaning: ", data_model.shape)
    logger.debug(data_model[data_model.duplicated(keep=False)])
    data_model.drop_duplicates(subset=["Attribute"], inplace=True)

    # unnamed columns in csvs
    drop_cols = [
        s
        for s in data_model.columns
        if bool(re.search("unnamed", s, flags=re.IGNORECASE))
    ]

    data_model = data_model.drop(columns=drop_cols)
    data_model["Required"] = data_model["Required"].fillna(False).astype(bool)
    data_model["multivalue"] = data_model["multivalue"].fillna(False).astype(bool)
    data_model.reset_index(drop=True, inplace=True)

    print("Data model shape AFTER cleaning: ", data_model.shape)

    return data_model


if __name__ == "__main__":

    module_pattern = str(ROOT_DIR.resolve()) + "/modules/**/*.csv"

    file_path = Path(ROOT_DIR, "EL.data.model.csv")

    dm = join_data_model_partitions(module_pattern)

    dm.to_csv(file_path, index=False)

    # regenerate JSON-LD
    command = """schematic schema convert EL.data.model.csv"""

    logger.info(command)

    proc = subprocess.Popen(
        command,
        cwd=ROOT_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = proc.communicate()

    if proc.returncode == 0:
        test_result = True
        logger.info("PASSED")

    else:
        test_result = False
        logger.debug("FAILED")
        logger.debug(command)
