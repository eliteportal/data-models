""" Join the data model modules and convert to JSON-LD """

from pathlib import Path
import subprocess
from datetime import datetime
from utils import utils
from join_csvs import join_data_model_partitions

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
        logger.debug(stderr)

