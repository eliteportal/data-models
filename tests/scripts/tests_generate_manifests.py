#! usr/bin python

"""
Description: Test if the manifests generate appropriately
Process: 
1. Get the template names from the JSON-LD model
2. Generate google sheet links to each of the templates
"""

from datetime import datetime
import json
import subprocess
from pathlib import Path
import re
import logging.config
from tqdm import tqdm
import pandas as pd
import yaml


cwd = Path(__file__)

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
    filename=Path(ROOT_DIR, "tests", "logs", timestamp + "_manifest_generation.log")
)
fh.setFormatter(logger.handlers[0].__dict__["formatter"])
logger.addHandler(fh)

# Get manifest names to generate manifests
with open(Path(ROOT_DIR, "EL.data.model.jsonld"), "r", encoding="UTF-8") as jf:
    jo = json.load(jf)

# Manifest template names in data model

templates = []

for i in jo["@graph"]:
    try:
        for subclasses in i["rdfs:subClassOf"]:
            if bool(
                re.search(
                    "Component", ",".join(subclasses.values()), flags=re.IGNORECASE
                )
            ):
                templates += [
                    {"label": i["rdfs:label"], "displayName": i["sms:displayName"]}
                ]

    except KeyError:
        pass

templates_df = pd.DataFrame.from_records(templates)

# Generate Manifests ------------------------------------------------------------------------------------

manifest_generation_results = []

for t in tqdm(templates_df["label"], total=len(templates_df["label"]), miniters=1):
    result_temp = {"template_name": t}

    command = f""" schematic manifest --config config.yml get -dt {t} -s -oxlsx data/manifest-templates/EL_template_{t}.xlsx"""

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
        logger.info(f"{t} has PASSED")

    else:
        test_result = False
        logger.debug(f"{t} has FAILED")

    result_temp["generation_test"] = test_result

    manifest_generation_results += [result_temp]

manifest_generation_results = pd.DataFrame(manifest_generation_results)

print(manifest_generation_results)

manifest_generation_results.to_csv(
    Path(
        ROOT_DIR,
        "tests",
        "logs",
        timestamp + "_manifest_generation_results.csv",
        index=False,
    )
)

# if everything passes then remake DCA config
