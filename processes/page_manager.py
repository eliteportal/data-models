#!/usr/bin/env python

"""
**module Name:** page_manager.py

**Description:**

This Python script provides functions to generate documentation pages for a data model within a website. It includes functions to:

* Load the data model from a CSV file.
* Create a page for the entire data model.
* Create pages for individual modules within the data model.
* Create pages for templates defined in the data model.

**Contributors:**

* Dan Lu
* Nicholas Lee
"""

# load modules
import os
import re
import sys
from pathlib import Path
import frontmatter
import pandas as pd
from mdutils import fileutils
from dotenv import dotenv_values
from glob import glob
import json

from toolbox import utils

root_dir_name = "data-models"

ROOT_DIR = utils.get_root_dir(root_dir_name)

logger = utils.add_logger(ROOT_DIR, "page_manager.log")

config = dotenv_values(Path(str(Path(__file__).parent), ".env"))


def get_info(data_model: pd.DataFrame, term: str, column: str = "Attribute") -> dict:
    """
    Retrieves information about a specific term from a pandas DataFrame.

    Args:
        data_model: A pandas DataFrame representing the data model (pd.DataFrame).
        term: The name of the term to search for (str).
        column: The column name in the data model that contains the terms (str).
            Defaults to "Attribute".

    Returns:
        A dictionary containing information about the term, including:
            'Description' (str): The description of the term (if found).
            'Source' (str, optional): The source of the term information (if available in the data model).
            'module' (str, optional): The module the term belongs to (if available in the data model).

    Raises:
        ValueError: If the provided term is not found in the data model.
    """

    # Filter data by term in the specified column
    results = data_model.loc[
        data_model[column] == term, ["Description", "Source", "module"]
    ].to_dict("records")

    # Check if any results were found
    if not results:
        raise ValueError(f"Term '{term}' not found in the data model")

    # Assuming source information might not be available, handle potential missing key
    if not results[0].get("Source"):
        results[0]["Source"] = None

    # Return the first dictionary (assuming unique terms)
    return results[0]


def create_template_page(term: str, term_dict: dict, schema_names_frame: pd.DataFrame) -> frontmatter.Post:
    """
    Creates a new markdown page for a specific template within the website's documentation.

    Args:
        term: The name of the template to create a page for (str).
        term_dict: A dictionary containing information about the template, including:
            'Description' (str): The description of the template.
            'Source' (str): The source of the template information. (URL or reference)

    Returns:
        A `frontmatter.Post` object representing the created template page metadata.

    Raises:
        ValueError: If the provided term name is empty, or if the term_dict is missing
            required keys 'Description' or 'Source'.
    """

    if not term:
        raise ValueError("Term name cannot be empty")

    if not all(key in term_dict for key in ["Description", "Source"]):
        raise ValueError("term_dict must contain keys 'Description' and 'Source'")

    # Load markdown template
    post = frontmatter.load(Path(ROOT_DIR, "_layouts/template_page_template.md"))

    # Update metadata for the new page
    post.metadata["title"] = re.sub("_", r" ", term).strip()
    post.metadata["parent"] = term_dict["module"]

    template_url = get_template_download_link(term=term, schema_names_frame=schema_names_frame)

    # Inject term information into template content
    content_prefix = (
        "{% assign mydata=site.data."
        + re.sub("\s|/", "_", term)
        + " %} \n{: .note-title } \n"
        + f">{post.metadata['title']}\n"
        + ">\n"
        + f">{term_dict['Description']} [[Download]]({template_url})\n"
    )
    post.content = content_prefix + post.content

    # Create and populate the module page file
    logger.info("Creating Page for: %s", str(Path(ROOT_DIR, f"docs/template/{term}")))

    template_page = fileutils.MarkDownFile(str(Path(ROOT_DIR, f"docs/template/{term}")))
    template_page.append_end(frontmatter.dumps(post))

    # return post

def get_manifest_schemas_name_frame(template_config_path: str = "dca-template-config.json") -> pd.DataFrame:
    """
    Loads the manifest schemas from a JSON configuration file into a pandas DataFrame.

    Args:
        template_config_path: The path to the JSON configuration file (str).

    Returns:
        A pandas DataFrame containing the manifest schemas.
    """

    with open(template_config_path, "r") as f:
        json_template_configdata = json.load(f)

    return pd.DataFrame.from_dict(json_template_configdata["manifest_schemas"])

def get_template_download_link(term: str, schema_names_frame: pd.DataFrame) -> str:
    """
    Constructs the download URL for a specific template based on its schema name.
    Args:
        term: The name of the template (str).
        schema_names_frame: A pandas DataFrame containing the schema names and display names.
    Returns:
        The download URL for the template (str).
    """
    base_url = "https://github.com/eliteportal/data-models/raw/refs/heads/"
    templates_path = "main/elite-data/manifest-templates/"
    template_prefix = "EL_template_"

    # Get the schema name corresponding to the term display name
    schema_name = schema_names_frame.loc[schema_names_frame["display_name"]==term, "schema_name"].values[0]

    # Build the url to directly trigger a download of the template
    download_url = base_url + templates_path + template_prefix + schema_name + ".xlsx"

    return download_url

def create_table_page(term: str, term_dict: dict) -> fileutils.MarkDownFile:
    """
    Creates a new markdown page for a specific term within the website's documentation.

    Args:
        term: The name of the term to create a page for (str).
        term_dict: A dictionary containing information about the term, including
            'Description' (str): The description of the term.
            'Source' (str): The source of the term information. (URL or reference)

    Returns:
        A `fileutils.MarkDownFile` object representing the created term page.

    Raises:
        ValueError: If the provided term name is empty, or if the term_dict is missing
            required keys 'Description' or 'Source'.
    """

    if not term:
        raise ValueError("Term name cannot be empty")

    if not all(key in term_dict for key in ["Description", "Source"]):
        raise ValueError("term_dict must contain keys 'Description' and 'Source'")

    term = term.strip()

    # Load markdown template
    post = frontmatter.load(Path(ROOT_DIR, "_layouts/term_page_template.md"))

    # Update metadata for the new page
    post.metadata["title"] = term
    post.metadata["parent"] = term_dict["module"]

    # Inject term information into template content
    content_prefix = (
        "{% assign mydata=site.data."
        + term
        + " %} \n{: .note-title } \n"
        + f">{term}\n"
        + ">\n"
        + f">{term_dict['Description']} [[Source]]({term_dict['Source']})\n"
    )
    post.content = content_prefix + post.content

    # Create and populate the term page file
    term_page = fileutils.MarkDownFile(
        str(Path(ROOT_DIR, f"""docs/modules/{term_dict["module"]}/{term}"""))
    )
    term_page.append_end(frontmatter.dumps(post))

    return term_page


def create_module_page(module: str) -> fileutils.MarkDownFile:
    """
    Creates a new markdown page for a specific module within the website's documentation.

    Args:
        module: The name of the module to create a page for (str).

    Returns:
        A `fileutils.MarkDownFile` object representing the created module page.

    Raises:
        ValueError: If the provided module name is empty or invalid.
    """

    if not module:
        raise ValueError("module name cannot be empty")

    mod_page_path = Path(ROOT_DIR, f"docs/modules/{module}/{module}.md")

    if not mod_page_path.parent.exists():
        mod_page_path.parent.mkdir(parents=True, exist_ok=True)

    module_page = fileutils.MarkDownFile(str(mod_page_path).strip('.md'))

    # Load markdown template
    post = frontmatter.load(Path(ROOT_DIR, "_layouts/term_page_template.md"))

    # Update metadata for the new page
    post.metadata["title"] = module
    post.metadata["nav_order"] = 5
    # post.metadata["permalink"] = f"docs/{module}.html"
    post.metadata["has_children"] = True
    post.metadata["parent"] = 'modules'

    # Inject module name into template content
    content_prefix = (
        "{% assign mydata=site.data."
        + re.sub("\s|/", "_", module)
        + " %} \n{: .note-title } \n"
        + f">{module}\n"
        + ">\n"
        + ">module in the data model\n"
    )
    post.content = content_prefix + post.content

    # Create and populate the module page file
    print("Creating module page: ", str(mod_page_path))
    module_page.append_end(frontmatter.dumps(post))

    return module_page


def create_full_table(data_model: pd.DataFrame) -> None:
    """
    Generates a markdown page for the entire data model within the website's documentation.

    Args:
        data_model: A pandas DataFrame representing the data model (pd.DataFrame).
    """

    # module name for the full data model page
    module_name = "DataModel"

    # Create directory for the data model if it doesn't exist
    data_model_dir = Path(ROOT_DIR, f"docs/{module_name}")
    if not data_model_dir.exists():
        # Create parent directories if needed
        data_model_dir.mkdir(parents=True)

    # Create the module page file
    module_page = fileutils.MarkDownFile(str(data_model_dir / module_name))

    # Load markdown template and update metadata
    post = frontmatter.load(Path(ROOT_DIR, "_layouts/term_page_template.md"))
    del post.metadata["parent"]
    post.metadata["title"] = module_name
    post.metadata["nav_order"] = 2
    post.metadata["permalink"] = f"docs/{module_name}.html"

    # Inject content about the full data model
    content_prefix = (
        "{% assign mydata=site.data."
        + module_name
        + " %} \n{: .note-title } \n"
        + f">{module_name}\n"
        + ">\n"
        + f">Complete Table of Keys for ELITE that are found in the data model\n"
    )
    post.content = content_prefix + post.content

    # Add the populated post content to the module page
    module_page.append_end(frontmatter.dumps(post))

    # Note: This function doesn't return anything as it modifies files directly.


def delete_page(term: str) -> list[str]:
    """
    Simulates deleting a markdown page for a term within the website's documentation.

    **Important:** This function does not permanently delete files. It simulates deletion for demonstration purposes.

    Args:
        term: The name of the term to simulate deletion for (str).

    Returns:
        A list of filenames that would have been deleted (list[str]).
    """

    # Pattern to match filenames based on term name
    file_pattern = f"{ROOT_DIR}/docs/**/*.{term}.md"

    # Simulate finding matching files
    deleted_files = [f for f in glob(file_pattern, recursive=True)]

    # This function currently performs actual deletion (use with caution!)
    for file in deleted_files:
        logger.warning(f"Deleting: {file}")
        os.remove(file)

    return deleted_files


if __name__ == "__main__":
    # Load data model using pandas with informative error handling
    try:
        data_model = pd.read_csv(config["csv_model_link"])
    except FileNotFoundError:
        print("Error: CSV file not found! Please check the config file.")
        sys.exit(1)

    # Generate documentation pages
    create_full_table(data_model)

    modules = list(data_model["module"].dropna().unique())
    for module in modules:
        create_module_page(module)

    schema_names_frame = get_manifest_schemas_name_frame()

    # Creating template pages
    print('---- Creating Template pages ----')
    templates = list(
        data_model[data_model["Parent"] == "Component"]["Attribute"].unique()
    )
    for template in templates:
        # term_attr = re.sub("_", " ", template)
        term_info = get_info(data_model, template, column="Attribute")
        create_template_page(template, term_dict=term_info,schema_names_frame=schema_names_frame)

    # create attribute pages
    print("---- Creating attribute pages ----")
    for a in data_model.loc[~data_model['Parent'].str.contains('Component', na=False), "Attribute"]:
        term_info = get_info(data_model, a, column="Attribute")
        create_table_page(a, term_info)

    # Delete pages with no data
    md_files = glob(f"{ROOT_DIR}/docs/**/*.md", recursive=True)
    csv_files = glob(f"{ROOT_DIR}/_data/*.csv", recursive=True)
    file_exceptions = ["DataModel", "Network_Graph", "ChangeLog"]

    # keepers = templates + modules + file_exceptions
    # # keepers = [re.sub("_", " ", r) for r in keepers]

    # for m in md_files:
    #     attr = Path(m).stem
    #     if attr not in keepers:
    #         logger.warning(f"Deleting markdown file: {attr}")
    #         os.remove(Path(m))

    # create sub heading pages

    logger.info("Documentation generation completed!")
