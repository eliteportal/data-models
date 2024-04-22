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
    filename=Path(ROOT_DIR, "tests", "logs", timestamp + "_manifest_generation.log")
)
fh.setFormatter(logger.handlers[0].__dict__["formatter"])
logger.addHandler(fh)


def get_templates(jsonld_name):

    # Get manifest names to generate manifests
    with open(Path(ROOT_DIR, JSONLD_NAME), "r", encoding="UTF-8") as jf:
        jsonld_model = json.load(jf)

    # Manifest template names in data model

    templates = []

    for i in jsonld_model["@graph"]:
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

    return templates_df


def manifest_generation_test(templates_df):

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
    templates_df = get_templates(JSONLD_NAME)

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
        proc = subprocess.Popen("python ./tests/update_dca_config.py", shell=True, cwd=ROOT_DIR)

        print(proc.communicate())
        if proc.returncode == 0:
            logger.info("PASS: DCA configuration template updated")
        else:
            logger.debug("FAILED: DCA configuration template update")
