#! usr/bin python

"""
Description: Test if the manifests generate appropriately
Process: 
1. Get the template names from the JSON-LD model
2. Generate google sheet links to each of the templates

TODO: 
- [ ] add args
"""

from datetime import datetime
import subprocess
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from utils.data_model_tools import get_templates
from utils.utils import get_root_dir, add_logger

ROOT_DIR_NAME = "ELITE-data-models"
JSONLD_NAME = "EL.data.model.jsonld"  # can do this in dev environment

ROOT_DIR = get_root_dir(ROOT_DIR_NAME)

timestamp = datetime.now().strftime("%Y-%m-%d")

# Create logger for reports
logger = add_logger(
    ROOT_DIR_NAME,
    logger_config_path=Path("_logs", "logging.yaml"),
    log_file_path=Path("tests", "logs", timestamp + "_manifest_generation.log"),
)

def manifest_generation_test(templates_df):
    """Make sure all templates are properly generated"""
    
    manifest_generation_results = []

    for t in tqdm(templates_df["schema_name"], total=len(templates_df["schema_name"]), miniters=1, desc="Creating Templates"):
        result_temp = {"template_name": t}

        command = f""" schematic manifest --config config.yml get -dt {t} -s -oxlsx data/manifest-templates/EL_template_{t}.xlsx"""  # could make dynamic by inputing where to store files

        # logger.info(f"Running command for {t}")
        # logger.info(command)

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
            logger.info("%s has PASSED", t)

        else:
            test_result = False
            logger.debug("%s has FAILED", t)
            logger.debug(command)

        result_temp["generation_test"] = test_result

        manifest_generation_results += [result_temp]

    return pd.DataFrame(manifest_generation_results)


if __name__ == "__main__":

    # Templates ------------------------------------------------------------------------------------
    manifest_schemas, templates_df = get_templates(ROOT_DIR, JSONLD_NAME)

    # Generate Manifests ------------------------------------------------------------------------------------
    manifest_generation_results = manifest_generation_test(templates_df)

    print(manifest_generation_results)

    manifest_generation_results.to_csv(
        Path(
            ROOT_DIR,
            "tests",
            "logs",
            timestamp + "_manifest_generation_results.csv",
            index=False,
        ),
        index=False,
    )

    # if everything passes then remake DCA config
    if manifest_generation_results["generation_test"].all():
        proc = subprocess.Popen(
            "python data_model_creation/update_dca_template_config.py",
            shell=True,
            cwd=ROOT_DIR,
        )

        print(proc.communicate())

        if proc.returncode == 0:
            logger.info("PASS: DCA configuration template updated")
        else:
            logger.debug("FAILED: DCA configuration template update")
