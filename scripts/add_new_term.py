#! usr/bin python

""" 
# MERGE NEW TERM WITH DM
rules to merge?
- if exisiting value exists, and no new value keep
- if exisiting value exists and new value adds information, combine
- if no exisiting value preseent, update with new value
process:
- describe na before changes
- make changes
- commit changes?
"""


import subprocess
from pathlib import Path
import re
import argparse
import numpy as np
import pandas as pd
from toolbox import utils

pd.set_option("future.no_silent_downcasting", True)

ROOT_DIR_NAME = "ELITE-data-models"
ROOT_DIR = utils.get_root_dir(ROOT_DIR_NAME)

logger = utils.add_logger("add_new_term.log")


def combine_str_cols(df, combo_col):
    """Join list cols in the dataframe"""
    df.loc[df.index.get_level_values("column") == combo_col, "dm"] = df.loc[
        df.index.get_level_values("column") == combo_col, :
    ].agg(",".join, axis=1)

    df.loc[df.index.get_level_values("column") == combo_col, "dm"] = df.loc[
        df.index.get_level_values("column") == combo_col, "dm"
    ].apply(lambda x: ",".join(list(np.unique([s.strip() for s in x.split(",")]))))

    return df


def combine_dataframes(
    data_model_df: pd.DataFrame, new_term_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Combine the two data fames into a new data model

    Assumes valid values, ontology and usedIn will expand with the addition of the new term
    """
    index_keys = ["Attribute"]
    keys = ["dm", "new_term"]

    df1 = (
        data_model_df[data_model_df["Attribute"].isin(new_term_df["Attribute"])]
        .set_index(index_keys)
        .sort_index()
    )
    df2 = (
        new_term_df[new_term_df["Attribute"].isin(data_model_df["Attribute"])]
        .set_index(index_keys)
        .sort_index()
    )

    df = pd.concat(
        [df1, df2],
        keys=keys,
        axis=1,
    ).sort_index(level=1, axis=1)

    # easier to process for looking at duplicate values
    df = df.stack(future_stack=True).dropna(how="all", axis=0)

    # if new term does not have value then also drop since it provides no info
    df = df[~df["new_term"].isna()]

    # if dm is empty, then fill with new term
    df["dm"] = df["dm"].fillna(df["new_term"])

    # remove duplicates
    df = df[df["dm"] != df["new_term"]]

    df.index = df.index.set_names(["Attribute", "column"])

    print("--- Differences between data model and new term ---")
    print(df)

    df = combine_str_cols(df, "Valid Values")
    df = combine_str_cols(df, "Ontology")
    df = combine_str_cols(df, "UsedIn")

    df = df.drop(columns=["new_term"])

    dm_stacked = data_model_df.set_index("Attribute").stack(future_stack=True)

    # add dynamic way to update changes to data model
    dm_stacked.update(df["dm"])

    dm_unstacked = dm_stacked.unstack()

    dm_unstacked = dm_unstacked.reset_index()

    logger.info("Combined data model with new term")

    return dm_unstacked


def update_data_model(new_dm: pd.DataFrame, output_path: str) -> None:
    """
    Writes out the new data model if users wants, otherwise it writes a staging data model
    """
    update_dm = str(input("Update data model? y/[n]: ") or "n")

    if update_dm == "y":
        csv_path = Path(ROOT_DIR, output_path)
        logger.info("Updating data model. New data model at: %s", csv_path)
        new_dm.to_csv(csv_path)

        # create the updated data model
        proc = subprocess.Popen(
            f""" schematic schema convert {output_path} """, cwd=ROOT_DIR, shell=True
        )

        proc.communicate()

        if proc.returncode == 0:
            print("Success!")
        else:
            print("FAIL")

    else:
        # create temp data model
        staging_path = Path(ROOT_DIR, "staging." + output_path)
        logger.info("Creating staging data model at: %s", staging_path)
        new_dm.to_csv(staging_path, index=False)


def main(arguments):
    """
    1. Load data model and new term
    2. Create updated data model
    3. Write out data model if checks pass
    """
    new_term_df = pd.read_csv(arguments.new_term_path)

    print("--- New Term ---")
    print(new_term_df.head())

    dm = pd.read_csv(Path(ROOT_DIR, arguments.data_model_path))

    print("--- Exisiting Data Model ---")
    print(dm.head())

    new_term_df["exists"] = new_term_df["Attribute"].isin(dm["Attribute"])

    new_terms_to_add = new_term_df[~new_term_df["exists"]]

    dm_updated = combine_dataframes(dm, new_term_df)

    dm_updated = pd.concat([dm_updated, new_terms_to_add])

    update_data_model(dm_updated, arguments.data_model_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Update data model with new term")

    parser.add_argument(
        "-d",
        "--data_model_path",
        help="path to data model relative to the root directory",
    )

    parser.add_argument(
        "-n",
        "--new_term_path",
        help="path to new term csv relative to the root directory",
    )

    args = parser.parse_args()

    main(args)
