""" 
Functions used to help generate manifests to test against the data model

USAGE: python create_test_manifests.py -d EL.data.model.csv -m 'scripts/tests/test_manifests/' -t Proteomics -id syn58863921

"""

import re
from pathlib import Path
from glob import glob
import os
import argparse
import string
import random
import lorem
import numpy as np
import pandas as pd
import synapseclient as sc
import subprocess
import logging.config
import yaml
from datetime import datetime
from utils import add_logger, get_root_dir

syn = sc.login()

timestamp = datetime.now().strftime("%Y-%m-%d")

ROOT_DIR_NAME = "ELITE-data-models"
ROOT_DIR = get_root_dir(ROOT_DIR_NAME)

logger_config_path = "_logs/logging.yaml"
log_file_path = Path(
    "scripts", "tests", "_logs", timestamp + "_create_test_manifests.log"
)
logger = add_logger(ROOT_DIR_NAME, logger_config_path, log_file_path)


def valid_values_to_list(df, attribute):
    """Get list of valid values from the data model"""
    valid_values = (
        df.query(f'Attribute == "{attribute}"')["Valid Values"].str.split(",").values[0]
    )
    return valid_values


def get_random_value(list_of_vv):
    """ """
    return random.choice(list_of_vv)


def get_rand_integer(min=0, max=100):
    """ """
    return random.randint(min, max)


def get_rand_float(min=0, max=100):
    """ """
    return round(random.uniform(0.0, 100.0), 2)


def get_random_string():
    """ """
    t = lorem.sentence().split(" ")[0]
    return t


def introduce_random_NAs(df, N=5):
    """Another test to see if columns can handle empty values or if they will flag the empty value"""

    rows, cols = df.shape
    row_index = [get_rand_integer(max=rows - 1) for _ in range(N)]
    col_index = [get_rand_integer(max=cols - 1) for _ in range(N)]
    indexes = list(zip(row_index, col_index))

    # Print indexes to check where values got replaced
    print(indexes)
    df.iloc[row_index, col_index] = np.NaN

    return df


def fill_in_attribute(df, index, attribute, value):
    """find attribute column, fill in with value"""
    df.loc[index, attribute] = value
    return df


def gen_mixed_string_with_length(N=12):
    """initializing size of string. generating random strings"""

    res = "".join(random.choices(string.ascii_uppercase + string.digits, k=N))
    return res


def random_change():
    """list of functions to choose from"""
    choices = [
        introduce_random_NAs,
        gen_mixed_string_with_length,
        get_rand_integer,
        get_random_string,
        get_rand_float,
    ]
    choice = random.choice(choices)
    print(choice.__name__)

    return choice()


def partition(list_in, n):
    """..."""

    random.shuffle(list_in)

    return [list_in[i::n] for i in range(n)]


def generate_values(value):
    value = value.lower()
    if value == "string":
        # generate string
        return get_random_string()
    elif value == "number":
        # generate random number
        return get_rand_integer()
    elif value == "mixed":
        # split string into regex expressions i.e. numbers and valid values
        choices = ["string", "number"]
        # chose random to fill in cell


def create_manifest(
    template_name, manifest_path, config_path="config.yml", dataset_id=None
):

    if dataset_id:
        command = f""" schematic manifest --config {config_path} get -dt {template_name} -d {dataset_id} -oxlsx {manifest_path} """
    else:
        command = f""" schematic manifest --config {config_path} get -dt {template_name} -s -oxlsx {manifest_path} """

    logger.info("Running command for %s: %s", template_name, command)

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
        logger.info("%s has PASSED", template_name)

    else:
        logger.debug("%s has FAILED", template_name)
        logger.debug(command)


def create_ind_spec_ids(ind_num: int = 10, spec_num: int = 10):
    # Create individaul IDs and specimenIDs
    individaulIds = [gen_mixed_string_with_length(N=10) for _ in range(1, ind_num)]
    specimenIds = [gen_mixed_string_with_length(N=5) for _ in range(1, spec_num)]
    specimenIds_partitioned = partition(specimenIds, 100)

    ind_bio_map = []
    for i, v in enumerate(individaulIds):
        for s in specimenIds_partitioned[i]:
            ind_bio_map.append({"individualID": v, "specimenID": s})
    ind_bio_map = pd.DataFrame(ind_bio_map)

    return ind_bio_map


def append_empty_rows(df, n):
    for _ in range(n):
        df.loc[len(df)] = pd.Series(dtype="str")

    return df


def main(template_name, manifest_dir, data_model_path, dataset_id):

    nrows = 10  # number of rows to fill in
    random.seed = 27
    chaos = False  # last minute chaos in manifest file, to check for errors
    new_manifest = True
    manifest_path = Path(manifest_dir, f"EL_template_{template_name}.xlsx")
    # template_name = args.templateName
    # manifest_dir = args.manifestPath
    # data_model_path = args.datamodel  # handle missing

    if dataset_id:
        create_manifest(
            template_name,
            manifest_path,
            config_path="config.yml",
            dataset_id=dataset_id,
        )
    elif not manifest_path.exists():
        create_manifest(template_name, manifest_path, config_path="config.yml")
    else:
        raise ValueError("Manifest was not generated or path was not valid")

    # load manifest
    if bool(re.search("csv", str(manifest_path.suffix))):
        df = pd.read_csv(manifest_path).dropna(how="all", axis=0).fillna("")
    elif bool(re.search("xlsx", str(manifest_path.suffix))):
        df = pd.read_excel(manifest_path).dropna(how="all", axis=0).fillna("")
    else:
        raise ValueError("Unable to read manifest file")

    df = df.replace("", None)

    # Function to append n empty rows to a DataFrame
    df = append_empty_rows(df, nrows)

    # Attributes to fill in from data model
    attrs_to_fill = df.columns.tolist()

    # load data model
    dm = pd.read_csv(data_model_path)

    # get data model attributes to fill in
    dm_attrs = (
        dm[(dm["Attribute"].isin(attrs_to_fill))]
        .drop_duplicates(subset=["Attribute"])
        .copy()
    )

    # find values in dm_attrrs with valid values filled in
    vv_attrs = dm_attrs[~dm_attrs["Valid Values"].isna()]["Attribute"].tolist()

    # fill in values for the mainfest with the data model
    for attribute in vv_attrs:
        for i in range(nrows):
            index = i
            temp_vv = valid_values_to_list(dm_attrs, attribute)
            new_val = get_random_value(temp_vv)
            df = fill_in_attribute(df, index, attribute, new_val)

    # fill in other columns without valid values
    free_form_attrs = dm_attrs[
        (~dm_attrs["Attribute"].isin(["individualID", "specimenID"]))
        & (dm_attrs["Valid Values"].isna())
    ]

    for attribute in free_form_attrs["Attribute"].tolist():
        for i in range(nrows):
            index = i
            test = dm.query(f'Attribute == "{attribute}"')
            new_val = test["columnType"].apply(generate_values).values[0]
            df = fill_in_attribute(df, index, attribute, new_val)

    # update df with sample of individual and biospecimen sample ids
    ind_bio_map = create_ind_spec_ids()
    ind_sample = ind_bio_map.sample(nrows, replace=True)[
        ["individualID", "specimenID"]
    ].reset_index(drop=True)

    df.update(ind_sample)

    # fill in file name if empty
    if all(df["Filename"].isna()):
        fake_file_names = pd.Series(["file_" + str(i) + ".csv" for i in range(nrows)])
        df["Filename"] = df["Filename"].fillna(fake_file_names)

    if chaos:
        df = introduce_random_NAs(df)

    # fill in component
    df["Component"] = template_name
    df = df.dropna(subset=["Filename"])

    # Write out manifest for validation
    csv_path = manifest_path.with_suffix(".csv")

    logger.info("Creating CSV at: %s", csv_path)
    df.to_csv(csv_path, index=False)

    return csv_path


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Create test manifests",
        description="Generates test manifests filled in with the data model values",
        epilog="Text at the bottom of help",
        usage="%(prog)s [options]",
    )

    parser.add_argument("-d", "--datamodel", help="path to the data model", type=str)

    # or create new manifest from model using schematic
    parser.add_argument(
        "-m", "--manifestPath", help="Directory to store the manifest", type=str
    )
    parser.add_argument(
        "-t", "--templateName", help="name of template in data model", type=str
    )

    parser.add_argument("-id", "--datasetid", help="Synapse ID", type=str)

    args = parser.parse_args()

    # print(args.__dict__)

    main(args)
