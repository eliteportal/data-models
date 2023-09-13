#!/usr/bin/env python

"""
Module Docstring

__author__ = "Nicholas"
__version__ = "0.1.0"
__license__ = "MIT"

"""

def main():
    """Main entry point of the app"""
    print("hello world")


if __name__ == "__main__":
    """This is executed when run from the command line"""

    import yaml
    import os

    with open(
        "C:/Users/nlee/Documents/Projects/ELITE-DCC/configs/notebook_config.yaml", "r"
    ) as f:
        config = yaml.safe_load(f)

    # paths to import files
    root_path = config["paths"]["root"]
    schematic_config = config["paths"]["schematic"]
    csv_model = config["file_names"]["csv_model"]
    json_model = config["file_names"]["json_model"]

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

    os.system(f"schematic schema convert {csv_model} --output_jsonld {json_model}")
