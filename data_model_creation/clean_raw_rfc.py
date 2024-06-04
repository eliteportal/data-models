"""
Transform raw rfc into a csv to add to the data model

USAGE: clean_raw_rfc.py -n "data/rfc_tables_raw/EL Assay_ bsSeq (bisulfite-seq_WGBS_methylseq_methylomics) data model.xlsx"
"""

from pathlib import Path
import re
import argparse
import logging.config
from datetime import datetime
import yaml
import pandas as pd
import numpy as np
from utils import utils

cwd = Path(__file__).resolve()

pd.set_option("future.no_silent_downcasting", True)

ROOT_DIR_NAME = "ELITE-data-models"
ROOT_DIR = utils.get_root_dir(ROOT_DIR_NAME)

# Create logger for reports
logger = utils.add_logger(Path("_logs", "logging.yaml"))

timestamp = datetime.now().strftime("%Y-%m-%d")

def remove_illegal_chars(x: str) -> str:
    """Removes illegal characters (parentheses and question marks) from a string.

    Args:
        x: The string to remove characters from (str).

    Returns:
        The string with illegal characters removed (str).
    """
    return re.sub(r"[()]\?", "", x)


def load_raw_rfc(rfc_path: Path) -> tuple[pd.DataFrame, str]:
    """Loads an RFC data file as a pandas DataFrame and extracts the template name.

    Args:
        rfc_path: The path to the RFC data file (Path).

    Returns:
        A tuple containing the loaded DataFrame and the extracted template name (tuple[pd.DataFrame, str]).
    """

    template_name = re.sub(
        r"EL|RFC|DRAFT|assay|data model|attribute[s]|\(.*?\)",
        "",
        Path(rfc_path).stem,
        flags=re.IGNORECASE,
    ).strip()

    template_name = re.sub(r"\s+|_+", " ", template_name).strip()
    template_name = re.sub(r"\s", "_", template_name).strip()
    # template_name = re.sub(r"_+", "_", template_name)

    logging.info(f"Extracted template name: {template_name}")

    try:
        rfc_df = pd.read_csv(rfc_path)
    except FileNotFoundError:
        logging.error(f"RFC file not found: {rfc_path}")
        return None, None

    logging.info(f"Dataframe information:\n{rfc_df.info()}")
    logging.info(f"Summary of missing values:\n{rfc_df.isna().sum()}")

    return rfc_df, template_name


def cleanup_rfc(rfc_df: pd.DataFrame, template_name: str) -> pd.DataFrame:
    """
    Cleans and preprocesses data in an RFC DataFrame.

    Args:
        rfc_df: A pandas DataFrame containing RFC data (pd.DataFrame).

    Returns:
        A cleaned and preprocessed DataFrame (pd.DataFrame).
    """

    column_map = {
        "key": "Attribute",
        "description": "Description",
        "required": "Required",
        "requires": "Module",
        "concept source ontology": "Ontology",
        "valid values": "Valid Values",
        "type": "columnType",
        "note": "Notes",
    }
    rfc_df = rfc_df.rename(columns=column_map, errors="ignore")
    rfc_df.fillna("", inplace=True)
    original_order = rfc_df["Attribute"].tolist()

    # Clean "Valid Values"
    def clean_func(x):
        return ",".join(
            y.strip() for y in x.split(",") if not "Possible values" in y
        ).strip(",")

    rfc_df["Valid Values"] = rfc_df["Valid Values"].apply(clean_func)

    # Combine cleaning steps
    rfc_df["Valid Values"] = (
        rfc_df["Valid Values"]
        .str.replace(
            r"n/a \(unique to each data contributor\)|Other|Unknown|Not collected|Not applicable|Not specified",
            "",
            regex=True,
        )
        .str.strip(",")
    )

    # Replace newlines with commas and remove duplicates
    rfc_df.replace(r"\n", ",", regex=True, inplace=True)
    rfc_df["Valid Values"] = (
        rfc_df["Valid Values"].str.rstrip(",").explode().str.strip().drop_duplicates()
    )

    # Remove illegal characters from attributes
    rfc_df["Attribute"] = rfc_df["Attribute"].apply(remove_illegal_chars)

    # Convert "Required" to boolean (consider using is_numeric_dtype)
    rfc_df["Required"] = pd.to_numeric(rfc_df["Required"], errors="coerce").fillna(
        False
    )

    rfc_df["columnType"] = rfc_df["columnType"].str.upper()
    rfc_df = rfc_df.drop(columns=["OtherValue"], errors="ignore").fillna("").astype(str)

    # Combine duplicate rows with unique values
    rfc_df = rfc_df.groupby("Attribute").apply(
        lambda x: x.apply(lambda y: ",".join(np.unique(y)).strip(", ").strip()),
        include_groups=False,
    )

    # Clean valid values
    # rfc_df["Valid Values"] = (
    #     rfc_df["Valid Values"]
    #     .fillna("")
    #     .str.split(",")
    #     .apply(lambda x: ",".join(np.unique([s.strip() for s in x])))
    #     .replace("", np.nan)
    # )

    # Assign remaining attributes
    rfc_df["Properties"] = "ManifestColumn"

    # Print data frame information
    print(f"Original data frame shape: {rfc_df.shape}")

    dependson = ["Filename"] + original_order + ["Component"]

    # Create new template attribute row
    new_temp_attr = {
        "Attribute": template_name,
        "Description": f"Template for {template_name}",
        "DependsOn": ",".join(dependson),
        "Valid Values": "",
        "Required": False,
        "Module": "Template",
        "columnType": "",
        "Ontology": "Sage Bionetworks",
        "Notes": "",
        "Properties": "",
        "Parent": "Component",
    }

    print(
        "Number of columns in new template: ",
        len(dependson),
    )

    # Add "UsedIn" and template attribute row
    rfc_df["UsedIn"] = template_name
    rfc_df = pd.concat(
        [rfc_df, pd.DataFrame([new_temp_attr]).set_index("Attribute")]
    ).replace("", np.nan)

    if len(set(original_order) - set(list(rfc_df.index))) == 0:
        # Ensure unique index and sort
        rfc_df = rfc_df.sort_index(key=lambda x: x.str.lower())

        return rfc_df

    else:
        raise RuntimeError("not all of the original values are found in the new rfc")


def main(arguments):
    """
    The main function that coordinates the processing of a new RFC data file.

    Args:
        arguments: Namespace object containing command-line arguments (argparse.Namespace).
    """

    # Load the RFC data and extract the template name
    rfc_df, template_name = load_raw_rfc(arguments.new_template_path)
    # if not rfc_df:
    #     return  # Handle potential errors during loading

    # Clean and pre-process the RFC data
    rfc_df = cleanup_rfc(rfc_df, template_name)

    # Print information and write to CSV
    print(rfc_df.info())

    csv_path = Path(
        ROOT_DIR, "data", "rfc_tables_cleaned", template_name + "_cleaned_rfc.csv"
    )

    logger.info("Creating CSV at: %s", csv_path)

    rfc_df.to_csv(csv_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Update data model with new term")

    # parser.add_argument(
    #     "-d",
    #     "--data_model_path",
    #     help="path to data model relative to the root directory",
    # )

    parser.add_argument(
        "-n",
        "--new_template_path",
        help="path to new term csv relative to the root directory",
    )

    args = parser.parse_args()

    main(args)
