""" 
Functions used to help generate manifests to test against the data model
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

syn = sc.login()

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

def create_manifest(manifest_name, data_model_path): 
    subprocess.Popen(
        command = "schematic manifest --config ./config.yml get -dt {manifest_name} -s -oxlsx "EL.Manifest.{}.xlsx""
    )

def main(args):

    nrows = 10  # number of rows to fill in
    random.seed = 27
    chaos = False  # last minute chaos in manifest file, to check for errors

    manifest_path = args["manifestPath"]
    manifest_name = Path(manifest_path).stem
    data_model_path = args["datamodel"]

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

    # Manifests
    # manifest_paths = glob("../manifests/*.csv")

    dm = pd.read_csv(data_model_path)  # load data model

    # load example manifest
    # manifest_path = "../example-scRNAseq.csv"
    df = pd.read_csv(manifest_path).dropna(how="all", axis=0).fillna("")
    parent_name = df["Component"].unique()[0]
    df["Component"] = manifest_name

    attrs_to_fill = df.columns.tolist()  # Attributes from data model

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

    # update df with sample of individual and biospecimen sample ids
    ind_sample = ind_bio_map.sample(nrows, replace=True)[
        ["individualID", "specimenID"]
    ].reset_index(drop=True)

    df.update(ind_sample)

    swap_validation_coder = {v: k for k, v in validation_coder.items()}

    # column coding for values
    dm_attrs["swapper"] = (
        dm_attrs["Validation Rules"].fillna("number").replace(swap_validation_coder)
    )

    dm_attrs["swapper"] = dm_attrs["swapper"].apply(
        lambda x: re.sub("^\d*?\.?\d$", "number", x)
    )

    # need a better regex later
    dm_attrs["swapper"] = dm_attrs["swapper"].apply(
        lambda x: re.sub(
            "number numbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumbernumber",
            "number",
            x,
        )
    )
    print(dm_attrs["swapper"].unique())

    free_form_attrs = dm_attrs[
        (dm_attrs["Valid Values"] == "")
        & (~dm_attrs["Attribute"].isin(["individualID", "specimenID"]))
    ]

    test = "([0-9]+\\.[0-9]*.)|([0-9]+)"
    test2 = "^\\d*?\\.?\\d$|Other|Unknown|Not collected|Not applicable"

    # def match_pattern(rule):

    pattern_checker = {
        "strip_patterns": "regex|search|match",
        "number": "(?![a-zA-Z]+)(\[0-9\])",
        "string": "([a-zA-Z]+)(?!\[0-9\])",
        "mixed": "(?:[a-zA-Z]+\d+)",
    }

    result = False

    while result == False:
        for k, v in pattern_checker.items():
            result = bool(re.search(pattern=v, string=test))
            print(v)
            print(result)

    # pattern = '(?![a-zA-Z]+)(\[0-9\])'
    # results = bool(re.search(pattern = pattern, string = test))
    # results

    # for attribute in free_form_attrs["Attribute"].tolist():
    for i in range(nrows):
        index = i
        test = free_form_attrs.query(f'Attribute == "{attribute}"')
        new_val = test["swapper"].apply(generate_values).values[0]
        df = fill_in_attribute(df, index, attribute, new_val)

    # write out test manifest to file for testing in DCA
    df["Component"] = manifest_name

    if chaos:
        df = introduce_random_NAs(df)

    # Write out manifest
    csv_path = os.path.join(
        "../testing/test_manifests",
        manifest_name + "-test.csv",
    )

    df.to_csv(csv_path)

    def validate_manifest(schematic_config_path, csv_path, manifest_name):
        print(
            f"schematic model --config {schematic_config_path} validate --manifest_path {csv_path} --data_type {manifest_name}"
        )
        subprocess.Popen(
            f"schematic model --config {schematic_config_path} validate --manifest_path {csv_path} --data_type {manifest_name}"
        )

        print(csv_path)
        print(schematic_config)
        print(manifest_name)

    def submit_manifest(manifest_path, dataset_id, manifest_name):
        subprocess.Popen(
            f"schematic model --config ./config.yml submit -mp {manifest_path} -d {dataset_id} -vc {manifest_name} -mrt both"
        )

    search_df(dm2, "valueReported")

    def store_manifest(): 
        csv_entity = sc.File(
            csv_path,
            description=f"Test manifest for {manifest_name}",
            parent=data_folder,
            annotations={"resourceType": "manifest", "manifestType": manifest_name},
        )

        csv_entity = syn.store(csv_entity)
    # s = syn.getColumns("syn51748558")
    # for i in s:
    #     print(i)


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
        "-m", "--manifestPath", help="Path to the mainfest(s)", type=str
    )
    
    parser.add_argument("-id", "--datasetid", help="Synapse ID", type=str)

    # manifest_path = "../example-scRNAseq.csv"
    # ['data_model_path'] = "../EL.data.model.csv"
    # dataset_id = "syn51753850"
    # dataset_id = "syn51753844"
    # manifest_folder_id = "syn51728840" # to store mainfests

    args = parser.parse_args()

    print(*args)

    main(args)
