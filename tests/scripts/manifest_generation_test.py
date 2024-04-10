#!usr/bin python

import os
import subprocess
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
# csv_model = Path(root_dir, config["csv_path"])
# json_model = Path(root_dir, csv_model.stem + ".jsonld")
manifest_base_dir = Path(root_dir, "./tests/manifest-templates/").resolve()

manifests_to_generate = ["Biospecimenhuman"]

print(">>> Creating manifest template(s)")

command = f"schematic manifest --config {schematic_config} get"

if manifests_to_generate is None:
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=root_dir,
    )

    while proc.poll() is None:
        print(
            proc.stdout.readline()
        )  # give output from your execution/your own message

    commandResult = proc.wait()  # catch return code

    print(commandResult)

elif isinstance(manifests_to_generate, list):
    for m in manifests_to_generate:
        new_command = (
            command
            + f" -dt {m} --output_xlsx {Path(manifest_base_dir, 'EL.manifest.'+ m)}"
        )
        print("Creating manifest for: ", m)
        print(new_command)

        proc = subprocess.Popen(
            new_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=root_dir,
        )

        while proc.poll() is None:
            print(
                proc.stdout.readline()
            )  # give output from your execution/your own message

        commandResult = proc.wait()  # catch return code
        print(commandResult)

else:
    new_command = (
        command
        + f" -dt {manifests_to_generate} --output_xlsx {Path(manifest_base_dir, 'EL.manifest.'+ manifests_to_generate)}.xlsx "
    )
    print("Creating manifest for: ", m)
    proc = subprocess.Popen(
        new_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=root_dir,
    )

    while proc.poll() is None:
        print(
            proc.stdout.readline()
        )  # give output from your execution/your own message
    commandResult = proc.wait()  # catch return code

    print(commandResult)
