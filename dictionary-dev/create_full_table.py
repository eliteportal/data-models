"""
Name: update_template_page.py
definition: a script to update template page when new term page is created
Contributors: Dan Lu
"""

# load modules
import os
import pdb
import pandas as pd

import yaml

with open("./_config.yml", "r") as f:
    config = yaml.safe_load(f)


def generate_full_table():
    df = pd.read_csv("EL.data.model.csv")

    df.rename(
        {"Attribute": "Key", "Description": "Key Description"}, axis=1, inplace=True
    )

    df = df[["Key", "Key Description", "Type", "Source", "Module"]]

    df.to_csv("docs/Full Table/FullTable.csv", index=False)


if __name__ == "__main__":
    main()
