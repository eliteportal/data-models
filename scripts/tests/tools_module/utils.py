"""
Name: utils.py
definition: Useful functions
Contributors: Nicholas Lee

Notes:
- Using for general work
"""

from datetime import datetime
import os
from pathlib import Path
import re
import logging.config
import yaml
import pandas as pd
import numpy as np


def code_equals_values(df, regex_dict, attribute):
    print("attribute: ", attribute)

    indexes = find_row(df, attribute)

    print("Index: ", indexes)

    if indexes is None:
        return df
    else:
        df = replace_valid_value(df, indexes, regex_dict, attribute)
        return df


def rewrite_df_value(df, col_name, search_term, col_value, new_value):
    try:
        df.loc[df[df[col_name] == search_term].index[0], col_value] = new_value
        return df
    except:
        return df


def join_strings(string):
    try:
        return ",".join(string)
    except:
        return ""


def clean_list(string):
    """Takes a list represented as a string and returns only unique values found

    Args:
        string (str): list represented as string

    Returns:
        string: list as string of unique values
    """

    new_list = string.split(",")
    new_list = [n.strip() for n in new_list if n != "nan"]
    new_list = ",".join(sorted(list(np.unique(new_list)))).strip(",")
    return new_list


def search_df(df, pattern):
    mask = np.column_stack(
        [df[col].str.contains(pattern, na=False, flags=re.IGNORECASE) for col in df]
    )

    df = df.loc[mask.any(axis=1)]

    print(df)

    return df


def find_row(df, attribute):
    """Get indexes of the dataframe"""
    indexes = df.index[
        df["Attribute"].str.contains(
            "(^" + re.escape(attribute) + "$)", flags=re.IGNORECASE
        )
    ].tolist()
    if len(indexes) != 0:
        return indexes
    else:
        print(attribute)
        return None


def replace_valid_value(df, indexes, regex_dict, attribute):
    """Alter the dataframe valid values with the replacement value"""
    if indexes == None:
        return df

    elif len(indexes) > 0:
        regex_dict = regex_dict[attribute]

        for index in indexes:
            df.loc[index, "Valid Values"] = re.sub(
                **regex_dict, string=df.loc[index, "Valid Values"]
            )

            # print(df.loc[index, 'Valid Values'])
        return df
    else:
        return df


def create_new_value(old_value):
    new_vals = old_value.split("=")
    new_vals = [nv.strip() for nv in new_vals]
    # convert to camel case
    nv = new_vals[1].capitalize() + new_vals[0][0].upper() + new_vals[0][1:]
    return nv


def recode_yes_no(v):
    if v.lower() == "yes":
        return "TRUE"
    elif v.lower() == "no":
        return "FALSE"
    else:
        return v


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

    root_dir = None

    for p in cwd.parents:
        if bool(re.search(root_dir_name + "$", str(p))):
            print(p)
            root_dir = p
            return root_dir

    if root_dir is None:
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


def display_full_table(df: object):
    """Show data table without width restrictions

    Args:
        df (dataFrame): _description_
    """

    print(df)


def get_time():
    """Create time stamp with format YYYY-MM-DD.Hr-Min

    Returns:
        string: current date and time
    """
    time_stamp = datetime.datetime.now()
    time_stamp = time_stamp.strftime("%Y-%m-%d.%H-%M")
    return time_stamp


def load_and_backup_dm(file_path: str, output_dir: str):
    """Create backup of data model with time stamp.

    Args:
        file_path (string):  path to CSV
    Returns:
        object: Data frame object
    """

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    dm = pd.read_csv(file_path, index_col=False)

    # write out old data model before changes
    file_path = Path(file_path).stem + "-" + get_time() + ".csv"

    output_path = Path(output_dir, file_path)

    dm.to_csv(output_path, index=False)

    return dm


def add_logger(ROOT_DIR_NAME: str, logger_config_path: str, log_file_path: str):
    """Create a logger object to store information to a file"""

    # ROOT_DIR_NAME = "ELITE-data-models"

    ROOT_DIR = get_root_dir(ROOT_DIR_NAME)

    # timestamp = datetime.now().strftime("%Y-%m-%d")

    logger_config_path = Path(ROOT_DIR, logger_config_path)

    # Create logger for reports
    with open(logger_config_path, "r", encoding="UTF-8") as f:
        yaml_config = yaml.safe_load(f)
        logging.config.dictConfig(yaml_config)

    logger = logging.getLogger("default")

    log_file_path = Path(ROOT_DIR, log_file_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    fh = logging.FileHandler(filename=log_file_path)

    fh.setFormatter(logger.handlers[0].__dict__["formatter"])

    logger.addHandler(fh)

    return logger
