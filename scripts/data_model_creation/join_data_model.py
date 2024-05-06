""" Join the data model modules """

from glob import glob
from pathlib import Path
import subprocess
import logging.config
from datetime import datetime
import re
import yaml
import pandas as pd
from toolbox import utils

cwd = Path(__file__)

ROOT_DIR_NAME = "ELITE-data-models"
JSONLD_NAME = "EL.data.model.jsonld"  # can do this in dev environment

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
    filename=Path(ROOT_DIR, "tests", "logs", timestamp + "_create_jsonld.log")
)
fh.setFormatter(logger.handlers[0].__dict__["formatter"])
logger.addHandler(fh)


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
        .sort_values(by=["Module", "Attribute"])
        .reset_index(drop=True)
        .fillna("")
    )

    print("Data model shape BEFORE cleaning: ", data_model.shape)
    data_model.drop_duplicates(subset=["Attribute"], inplace=True)
    data_model.reset_index(drop=True, inplace=True)
    print("Data model shape AFTER cleaning: ", data_model.shape)

    return data_model


if __name__ == "__main__":

    root_dir_name = "ELITE-data-models"

    root_dir = utils.get_root_dir(root_dir_name)

    module_pattern = root_dir.resolve()._str + "/modules/*.csv"

    file_path = Path(root_dir, "EL.data.model.csv")

    dm = join_data_model_partitions(module_pattern)

    dm.to_csv(file_path, index=False)

    # regenerate JSON-LD
    command = """ schematic schema convert EL.data.model.csv"""

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
