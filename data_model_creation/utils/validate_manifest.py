import pandas as pd
import subprocess
from pathlib import Path
import logging.config
import argparse
import re
import sys
from datetime import datetime
import synapseclient as sc
from utils import add_logger, get_root_dir

timestamp = datetime.now().strftime("%Y-%m-%d")

ROOT_DIR_NAME = "ELITE-data-models"
ROOT_DIR = get_root_dir(ROOT_DIR_NAME)

logger_config_path = "_logs/logging.yaml"
log_file_path = Path("scripts", "tests", "_logs", timestamp + "_validate_manifests.log")
logger = add_logger(ROOT_DIR_NAME, logger_config_path, log_file_path)

syn = sc.login()


def store_manifest(csv_path, manifest_name, syn_folder):
    csv_entity = sc.File(
        csv_path,
        description=f"Test manifest for {manifest_name}",
        parent=syn_folder,
        annotations={"resourceType": "manifest", "manifestType": manifest_name},
    )

    csv_entity = syn.store(csv_entity)


def validate_manifest(schematic_config_path, csv_path, manifest_name):
    command = f"schematic model --config {schematic_config_path} validate --manifest_path {csv_path} --data_type {manifest_name}"

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
        logger.info("Validation has PASSED")

    else:
        logger.debug("Validation has FAILED")
        raise ValueError("Unable to validate manifest")
        # sys.exit(2)

    return proc.returncode


def submit_manifest(manifest_path, dataset_id, template_name):
    command = f"schematic model --config config.yml submit -mp {manifest_path} -d {dataset_id} -vc {template_name} -mrt file_only"
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
        logger.info("submission has PASSED")

    else:
        logger.debug("submission has FAILED")
        raise ValueError("Unable to submit manifest")

    return proc.returncode


def main(schematic_config_path, manifest_path, template_name, dataset_id):
    # schematic_config_path = args.config
    # manifest_path = args.manifestPath
    # template_name = args.templateName
    # dataset_id = args.datasetid

    validate_results = validate_manifest(
        schematic_config_path, manifest_path, template_name
    )
    # if not validate_results:
    submit_manifest(manifest_path, dataset_id, template_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Validate manifests",
        description="validate the manifests",
        epilog="Text at the bottom of help",
        usage="%(prog)s [options]",
    )

    parser.add_argument("-c", "--config", help="path to the data model", type=str)

    # or create new manifest from model using schematic
    parser.add_argument(
        "-m", "--manifestPath", help="Directory to store the manifest", type=str
    )
    parser.add_argument(
        "-t", "--templateName", help="name of template in data model", type=str
    )

    parser.add_argument("-id", "--datasetid", help="Synapse ID", type=str)

    args = parser.parse_args()

    # print(args.__dict__)

    main(args)
