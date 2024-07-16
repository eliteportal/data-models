"""
Name: create_CSVs.py
definition: A script to create the csvs that populate the metadata dictionary website
Contributors: Nicholas Lee
"""

# import packages
import os
import yaml
import pandas as pd

import term_file_manager as tfm
import term_page_manager as tpm
import update_template_page as utp

with open("./_config.yml", "r") as f:
    config = yaml.safe_load(f)


def create_module_csv(data_model, module):
    # filter data model for modules

    OUTPUT_PATH_BASE = "_data"

    data_model.query(f'Module == "{module}"').to_csv(
        os.path.join(OUTPUT_PATH_BASE, module + ".csv")
    )


def main():
    data_model = pd.read_csv(config["data_model"])

    data_model = data_model[["Attribute", "Description", "Type", "Source", "Module"]]

    # rename columns
    data_model = data_model.rename(
        {"Attribute": "Key", "Description": "Key Description"}
    )

    # Create Module CSVs
    modules = data_model["Module"].dropna().unique()

    for m in modules:
        create_module_csv(data_model, m)


if __name__ == "__main__":
    main()
