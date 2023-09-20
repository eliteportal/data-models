#!/usr/bin/env python

"""
Module Docstring

__author__ = "Nicholas"
__version__ = "0.1.0"
__license__ = "MIT"
__description__ = "Script for turning the csv model into a jsonld model. WARNING: this can take a while to run."

"""

import yaml
import os
import pathlib


def main():
    """Main entry point of the app"""

    with open(
        pathlib.Path("dev/local_configs/notebook_config.yaml").resolve(), "r"
    ) as f:
        config = yaml.safe_load(f)

    # paths to import files
    root_path = os.getcwd()
    schematic_config = config["paths"]["schematic"]
    csv_model = os.path.join(root_path, config["file_names"]["csv_model"])
    json_model = os.path.join(root_path, config["file_names"]["json_model"])

    print(
        "Schematic config: ",
        schematic_config,
        "/n",
        "CSV model: ",
        csv_model,
        "/n",
        "JSON LD Model: ",
        json_model,
    )

    print(f"schematic schema convert {csv_model} --output_jsonld {json_model}")
    os.system(f"schematic schema convert {csv_model} --output_jsonld {json_model}")


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
