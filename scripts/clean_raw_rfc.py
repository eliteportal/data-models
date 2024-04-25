"""
Transform raw rfc into a csv to add to the data model

USAGE: clean_raw_rfc.py -d EL.data.model.csv -n "data/rfc_tables_raw/EL Assay_ bsSeq (bisulfite-seq_WGBS_methylseq_methylomics) data model.xlsx"
"""

from pathlib import Path
import re
import argparse
import logging.config
from datetime import datetime
import yaml
import pandas as pd
import numpy as np


cwd = Path(__file__).resolve()

ROOT_DIR_NAME = "ELITE-data-models"

for p in cwd.parents:
    if bool(re.search(ROOT_DIR_NAME + "$", str(p))):
        print(p)
        ROOT_DIR = p

timestamp = datetime.now().strftime("%Y-%m-%d")

# Create logger for reports
with open(Path(ROOT_DIR, "_logs", "logging.yaml"), "r", encoding="UTF-8") as f:
    yaml_config = yaml.safe_load(f)
    logging.config.dictConfig(yaml_config)

logger = logging.getLogger("default")

fh = logging.FileHandler(
    filename=Path(ROOT_DIR, "tests", "logs", timestamp + "_new_term_addition.log")
)
fh.setFormatter(logger.handlers[0].__dict__["formatter"])
logger.addHandler(fh)

# glob("data/RFC Tables/*.xlsx", root_dir=ROOT_DIR) # could use as options later
# new_template_path = "data/rfc_tables_raw/EL RFC genotyping_assay.xlsx"


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
        r"EL|RFC|assay|data model|_|\(.*?\)",
        "",
        Path(rfc_path).stem,
        flags=re.IGNORECASE,
    ).strip()

    logging.info(f"Extracted template name: {template_name}")

    try:
        rfc_df = pd.read_excel(rfc_path)
    except FileNotFoundError:
        logging.error(f"RFC file not found: {rfc_path}")
        return None, None

    logging.info(f"Dataframe information:\n{rfc_df.info()}")
    logging.info(f"Summary of missing values:\n{rfc_df.isna().sum()}")

    return rfc_df, template_name


def cleanup_rfc(rfc_df: pd.DataFrame) -> pd.DataFrame:
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

    return rfc_df


def create_other_attrs(rfc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts and creates new attributes ("specify" attributes) from existing attributes
    with a specific module format (containing "=" signs).

    Args:
        rfc_df: A pandas DataFrame containing RFC data (pd.DataFrame).

    Returns:
        A DataFrame containing the newly created "specify" attributes (pd.DataFrame).
    """

    # Filter DataFrame for modules containing "=" signs
    rfc_df_others = rfc_df.loc[rfc_df["Module"].str.contains("=", na=False)].copy(
        deep=True
    )

    # Extract "specify" attribute names and parent attributes
    rfc_df_others["others"] = (
        rfc_df_others["Module"]
        .str.split(",")
        .apply(lambda x: "".join([y.strip() for y in x if bool(re.search("=", y))]))
    )

    # if there are no others then break out of function
    if sum(~rfc_df_others["others"].isna()) == 0:
        raise ValueError("No others to create")

    # remove illegal characters from others
    rfc_df_others["others"] = rfc_df_others["others"].apply(remove_illegal_chars)

    # if there are mulitple in the data frame
    rfc_df_others = rfc_df_others.explode("others")

    # assign new parent values. So if the value is selected in the parent attr, then specify will be required
    rfc_df_others[["Parent", "OtherValue"]] = rfc_df_others["others"].str.split(
        "=", expand=True
    )

    # Create new "specify" attribute names with proper capitalization
    rfc_df_others["others"] = (
        rfc_df_others["others"]
        .str.split("=")
        .apply(lambda x: x[1].strip().capitalize() + x[0][0].upper() + x[0][1:])
    )

    # Swap others -> Attribute and Attribute -> DependsOn. Links others to specify column so they can enter a value
    rfc_df_others = rfc_df_others.rename(
        columns={"Attribute": "DependsOn", "others": "Attribute"}
    )

    # Define remaining attributes for the new DataFrame
    specify_attrs = {
        "DependsOn": rfc_df_others["Parent"],
        "Required": False,
        "Module": "Other",
        "Valid Values": "",
        "columnType": "string",
        "Ontology": "Sage Bionetworks",
        "Properties": "ValidValue",
    }

    rfc_df_others = rfc_df_others.assign(**specify_attrs)

    # Generate descriptions for "specify" attributes
    for i in rfc_df_others.index:
        rfc_df_others.loc[i, "Description"] = (
            f"""When column = `{rfc_df_others.loc[i, "OtherValue"]}`, add your custom value to the cell"""
        )

    # Remove illegal characters
    rfc_df_others[["Attribute", "Parent"]] = rfc_df_others[["Attribute", "Parent"]].map(
        remove_illegal_chars
    )

    return rfc_df_others


def add_other_attrs(
    rfc_df: pd.DataFrame, rfc_df_others: pd.DataFrame, template_name: str
) -> pd.DataFrame:
    """
    Merges "specify" attributes from rfc_df_others into the valid values of relevant
    attributes in rfc_df, and creates a final cleaned DataFrame.

    Args:
        rfc_df: A pandas DataFrame containing RFC data (pd.DataFrame).
        rfc_df_others: A DataFrame containing newly created "specify" attributes (pd.DataFrame).
        template_name: The name of the template being processed (str).

    Returns:
        A cleaned and finalized DataFrame (pd.DataFrame).
    """

    # Add "other" attributes to valid values (avoiding duplicates)
    # not_na = rfc_df["Valid Values"].notna()  # Efficiently identify non-missing values

    rfc_df.loc[
        ~rfc_df.replace("", np.nan)["Valid Values"].isna(), "Valid Values"
    ] = rfc_df.loc[~rfc_df.replace("", np.nan)["Valid Values"].isna()].apply(
        lambda x: re.sub(
            ",+",
            ",",
            ",".join(
                [
                    (
                        p
                        if p
                        not in rfc_df_others.loc[
                            rfc_df_others["Parent"] == x["Attribute"], "OtherValue"
                        ].values
                        else ""
                    )
                    for p in x["Valid Values"].split(",")
                ]
                + list(
                    rfc_df_others.loc[
                        rfc_df_others["Parent"] == x["Attribute"], "Attribute"
                    ].values
                )
            ),
        ),
        axis=1,
    )

    # Clean valid values
    rfc_df["Valid Values"] = (
        rfc_df["Valid Values"]
        .fillna("")
        .str.split(",")
        .apply(lambda x: ",".join(np.unique([s.strip() for s in x])))
        .replace("", np.nan)
    )

    # Assign remaining attributes
    rfc_df["Properties"] = "ManifestColumn"
    rfc_df["Module"] = np.where(
        rfc_df["Attribute"].str.contains("specify"), "Other", "Metadata"
    )

    # Print data frame information
    print(f"Original data frame shape: {rfc_df.shape}")
    print(f"Others data frame shape: {rfc_df_others.shape}")

    # Concatenate and clean DataFrame
    rfc_df_final = pd.concat([rfc_df, rfc_df_others]).reset_index(drop=True)

    rfc_df_final["columnType"] = rfc_df_final["columnType"].str.upper()
    rfc_df_final = rfc_df_final.drop(columns=["OtherValue"]).fillna("").astype(str)

    # Combine duplicate rows with unique values
    rfc_df_final = rfc_df_final.groupby("Attribute").apply(
        lambda x: x.apply(lambda y: ",".join(np.unique(y)).strip(", ").strip()),
        include_groups=False,
    )

    # Create new template attribute row
    new_temp_attr = {
        "Attribute": template_name,
        "Description": f"Template for {template_name}",
        "DependsOn": ",".join(
            ["Component", "Filename"]
            + list(rfc_df_final[rfc_df_final["Properties"] == "ManifestColumn"].index)
        ),
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
        len(
            ["Component", "Filename"]
            + list(rfc_df_final[rfc_df_final["Properties"] == "ManifestColumn"].index)
        ),
    )

    # Add "UsedIn" and template attribute row
    rfc_df_final["UsedIn"] = template_name
    rfc_df_final = pd.concat(
        [rfc_df_final, pd.DataFrame([new_temp_attr]).set_index("Attribute")]
    ).replace("", np.nan)

    # Ensure unique index and sort
    rfc_df_final = rfc_df_final.sort_index(key=lambda x: x.str.lower())

    # Print information and write to CSV
    print(rfc_df_final.info())

    csv_path = Path(
        ROOT_DIR, "data", "rfc_tables_cleaned", template_name + "_cleaned_rfc.csv"
    )
    logger.info("Creating CSV at: %s", csv_path)

    rfc_df_final.to_csv(csv_path)

    return rfc_df_final


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
    rfc_df = cleanup_rfc(rfc_df)

    # Create "specify" attributes for attributes with specific module format
    rfc_df_others = create_other_attrs(rfc_df)

    # Merge "specify" attributes and create the final cleaned DataFrame
    add_other_attrs(rfc_df, rfc_df_others, template_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Update data model with new term")

    parser.add_argument(
        "-d",
        "--data_model_path",
        help="path to data model relative to the root directory",
    )

    parser.add_argument(
        "-n",
        "--new_template_path",
        help="path to new term csv relative to the root directory",
    )

    args = parser.parse_args()

    main(args)
