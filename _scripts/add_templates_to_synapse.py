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
import synapseclient


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

    # generate templates
    os.system(f"schematic manifest --config {config['paths']['schematic']} get")

    # Upload templates
    # ./manifest-templates/*.xlsx or .csv
    manifest_folder = 'syn51232746'
    