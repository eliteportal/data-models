""" 

"""

import re
from pathlib import Path
import pandas as pd


def get_template_labels(jsonld: dict):
    """get template labels from the JSON-LD model

    Templates need to have component as the parent value in the CSV

    Could update to search for based on parent dynamically
    """

    templates = []

    for i in jsonld["@graph"]:
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


def get_root_dir(root_dir_name: str):
    """Find the root directory for a file to get the base of the repo"""
    cwd = Path(__file__).resolve()

    ROOT_DIR = None

    for p in cwd.parents:
        if bool(re.search(root_dir_name + "$", str(p))):
            print(p)
            ROOT_DIR = p
            return ROOT_DIR

    if ROOT_DIR is None:
        raise ValueError("No root directory found")


def compare_dfs(df1, df2, index_keys: list, keys: list) -> pd.DataFrame:

    df1 = df1.dropna(how="all", axis=1)
    df2 = df2.dropna(how="all", axis=1)

    df = pd.concat(
        [df1.set_index(index_keys), df2.set_index(index_keys)],
        keys=keys,
        axis=1,
    ).sort_index(level=1, axis=1)

    # print(df.stack())

    return df.stack()


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
