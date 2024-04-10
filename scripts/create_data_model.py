#!usr/bin python

import os
from pathlib import Path
from dotenv import dotenv_values
import re

# paths to import files
# Find ELITE-data-models root directory from anywhere
ROOT_DIR_NAME = "ELITE-data-models"

for p in Path(__file__).parents:
    if bool(re.search(ROOT_DIR_NAME + "$", str(p))):
        print(p)
        root_dir = p

print(">>> Changing root path to: ", root_dir)
os.chdir(root_dir)

config = dotenv_values(Path(root_dir, ".env"))
schematic_config = str(Path(root_dir, config["schematic_config_path"]).resolve())
csv_model = Path(root_dir, config["csv_path"])
json_model = Path(root_dir, csv_model.stem + ".jsonld")

manifests_to_generate = ["Biospecimenhuman"]

# Initialize schematic
# print(">>> Initializing Schematic")
# os.system(f"schematic init --config {schematic_config.resolve()}")

# Convert Schema if schema differs (todo)
# print(">>> Converting CSV to JSONLD")
# os.system(f"schematic schema convert {csv_model} --output_jsonld {json_model}")

# Get an empty manifest as a CSV using model
# &> tests/logs/manifest_generation.txt

print(">>> Creating manifest template(s)")
if isinstance(manifests_to_generate, list):
    for m in manifests_to_generate:
        print("Creating manifest for: ", m)
        os.system(
            f"schematic manifest --config {schematic_config} get -dt {m} --output_xlsx ./tests/manifest-templates/EL.manifest.{m}.xlsx "
        )
else:
    os.system(
        f"schematic manifest --config {schematic_config} get -dt {manifests_to_generate} --output_xlsx ./tests/manifest-templates/EL.manifest.{manifests_to_generate}.xlsx "
    )
