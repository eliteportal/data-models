#!/usr/bin/env python

"""
This script generates or updates term CSVs.

Args:
    term (str, optional): The term name to process. If not provided, all terms are processed.

Returns:
    None

Raises:
    ValueError: If a CSV filename contains spaces.

Authors:
    Dan Lu
    Nicholas Lee
"""

# load Parents
import os
import argparse
import re
from glob import glob
from pathlib import Path
import logging
import pandas as pd
from dotenv import dotenv_values

from toolbox import utils


root_dir_name = "data-models"

ROOT_DIR = utils.get_root_dir(root_dir_name)

logger = utils.add_logger(ROOT_DIR, "data_manager.log")

config = dotenv_values(Path(str(Path(__file__).parent), ".env"))


def get_template_keys(data_model: pd.DataFrame, template: str) -> list[str]:
    """
    Extracts all dependent terms (attributes) associated with a template in the data model,
    including dependencies from valid values of required attributes.

    Args:
        data_model: A pandas DataFrame representing the full data model (pd.DataFrame).
        template: The name of the template attribute (str).

    Returns:
        A list of dependent terms (attributes) as strings (list[str]).
    """

    # Get initial dependencies from the template's "DependsOn" attribute
    initial_depends_on = data_model.loc[
        data_model["Attribute"] == template, "DependsOn"
    ]
    depends_on = (
        initial_depends_on.dropna().explode().str.strip().tolist()
    )  # Flatten and clean

    # Extract dependencies from valid values of required attributes within the initial dependencies
    required_attributes = data_model.loc[
        data_model["Attribute"].isin(depends_on), "Attribute"
    ]
    valid_value_deps = (
        data_model[data_model["Attribute"].isin(required_attributes)]
        .loc[:, "Valid Values"]
        .dropna()
        .explode()
        .str.strip()
        .tolist()
    )

    # Combine initial dependencies with dependencies from valid values (remove duplicates)
    depends_on.extend(set(valid_value_deps))

    depends_on = [d.strip() for d in depends_on[0].split(",")]

    return depends_on


def create_module_csv(data_model: pd.DataFrame, module: str) -> None:
    """
    Generates a CSV file containing all attributes belonging to a specific module in the data model.

    Args:
        data_model: A pandas DataFrame representing the full data model (pd.DataFrame).
        module: The name of the module to generate a CSV for (str).
    """

    # Filter data for the specified module and fill missing values
    df = data_model.fillna("").copy(deep=True)
    df = df.loc[
        data_model["module"] == module,
        ["Attribute", "Description", "Valid Values", "columnType", "Parent", "module"],
    ]

    # Prepare output format (consistent with create_term_df)
    df.rename(
        columns={"Attribute": "Key", "Description": "Key Description"}, inplace=True
    )

    # Generate CSV filename with consistent formatting
    module_csv_name = re.sub(r"\s|/", "_", module)

    df.to_csv(Path(ROOT_DIR, "_data", module_csv_name + ".csv"), index=False)

    logging.info(f"Added {module_csv_name}.csv")
    print(f"Added {module_csv_name}.csv")


def create_term_df(data_model: pd.DataFrame, term: str) -> pd.DataFrame:
    """
    Generates a DataFrame for a specific term from the data model, suitable for populating website tables.

    Args:
        data_model: A pandas DataFrame representing the full data model (pd.DataFrame).
        term: The name of the term to generate a DataFrame for (str).

    Returns:
        A pandas DataFrame containing information about the term (pd.DataFrame).
    """

    if (
        bool(re.search('template', ','.join(data_model.query("`Attribute` == @term")["module"].values)))
        and term != "countryCode"
    ):
        logging.info("Generate CSV for template: %s", term)
        depends_on = get_template_keys(data_model, term)
        df = data_model[data_model["Attribute"].isin(depends_on)].copy(deep=True)
        df = df[
            [
                "Attribute",
                "Description",
                "Required",
                "columnType",
                "DependsOn",
                "Source",
                "Parent",
                "Valid Values",
            ]
        ].reset_index(drop=True)

    elif term == "countryCode":
        # Download and process World Bank country code data
        url = "http://wits.worldbank.org/data/public/WITSCountryProfile-Country_Indicator_ProductMetada-en.xlsx"
        df = pd.read_excel(io=url, sheet_name="Country-Metadata")
        df = df[
            [
                "Country Code",
                "Country Name",
                "Country ISO3",
                "Long Name",
                "Region",
            ]
        ].rename(columns={"Country Code": "Key", "Country Name": "Key Description"})
        df["Source"] = (
            "https://wits.worldbank.org/countryprofile/metadata/en/country/all"
        )
        df["Parent"] = "Metadata"
        df["Type"] = "Numeric"

    else:
        # Generate CSV for other attributes
        filtered_data = data_model.loc[
            (~data_model["Valid Values"].isna()) | (~data_model["DependsOn"].isna())
        ]
        df = filtered_data.loc[
            (filtered_data["Attribute"] == term)
            & (data_model["Parent"] != "ValidValue")
        ][["Attribute", "Valid Values", "DependsOn", "columnType", "Parent"]]

        # Explode comma-separated values
        df = (
            df.drop(columns=["Attribute", "DependsOn"])
            .set_index(["columnType", "Parent"])
            .apply(lambda x: x.str.split(",").explode())
            .reset_index()
        )

        # Prepare output DataFrame
        df.rename(columns={"Valid Values": "Key"}, inplace=True)
        df["Key Description"] = None
        df["Source"] = None
        df = df[["Key", "Key Description", "columnType", "Source", "Parent"]]

    # Remove duplicates and format output
    # df = df.drop_duplicates()
    term_csv_name = re.sub(r"\s|/", "_", term)
    df.to_csv(Path(ROOT_DIR, "_data", term_csv_name + ".csv"), index=False)
    logging.info(f"Added {term_csv_name}.csv")
    print(f"Added {term_csv_name}.csv")

    return df


def manage_files(term: str = None) -> None:
    """
    Manages data model files, including generating CSVs for the full model, modules, and attributes.

    Args:
        term: An optional term (attribute) to potentially trigger a specific file generation (str, optional).
            Defaults to None.
    """

    # Load data models
    try:
        current_dm = pd.read_csv(Path(ROOT_DIR, "_data/DataModel.csv"))
    except FileNotFoundError:
        logging.error(
            "Current data model CSV not found: %s",
            Path(ROOT_DIR, "_data/DataModel.csv"),
        )
        return

    try:
        data_model = pd.read_csv(config["csv_model_link"])
    except FileNotFoundError:
        logging.error("CSV data model link in config not found!")
        return

    # Generate attribute CSVs with sanitization
    data_model["Attribute"] = data_model["Attribute"].str.replace(
        "\\s|/", "_", regex=True
    )

    # Generate module CSVs
    modules = data_model["module"].unique().tolist()

    for module in modules:
        try:
            create_module_csv(data_model, module)
        except Exception as e:
            logging.debug(f"Error creating module CSV for '{module}': {e}")
            print(f"Error creating module CSV for '{module}': {e}")

    relevant_data = data_model.loc[
        (~data_model["Valid Values"].isna())
        | (~data_model["DependsOn"].isna()) & (data_model["Parent"] != "ValidValue")
    ]

    def generate_csv_temp(attr):
        create_term_df(data_model, attr)

    list(map(generate_csv_temp, relevant_data["Attribute"].unique()))

    data_model.rename(
        columns={"Attribute": "Key", "Description": "Key Description"},
        errors="ignore",
        inplace=True,
    )

    data_model = data_model[
        ["Key", "Key Description", "columnType", "Source", "module"]
    ]

    # Update data model CSV
    data_model.to_csv(Path(ROOT_DIR, "_data/DataModel.csv"), index=False)

    logging.info("Successfully created term files for data model")

    logging.info("Deleting files corresponding to terms not found in the data model")

    rm_files = glob(str(Path(ROOT_DIR, "_data")) + "/*.csv")

    keep_terms = ["DataModel"] + modules + list(data_model["Key"].unique())

    for r in rm_files:
        attr_name = Path(r).stem
        if attr_name not in keep_terms:
            logging.warning(
                f"Deleting file: {attr_name}",
            )
            os.remove(Path(r))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "term",
        type=str,
        help="The term name(s) (Optional). Provide when you want to generate file(s) for specific term(s). Leave it blank if you want to edit files for all terms",
        nargs="*",
    )
    args = parser.parse_args()

    if args.term:
        manage_files(args.term)
    else:
        manage_files()
