"""
Name: create_docs.py
definition: A script to create the csvs that populate the metadata dictionary website. Creates the module markdown files. 
Contributors: Nicholas Lee
"""

# import packages
from jinja2 import Template
import os
import pandas as pd
import shutil
from dotenv import dotenv_values
from pathlib import Path

config = dotenv_values(".env")

os.chdir(Path(__file__).parent.parent)


def get_subdirectories(directory):
    # excludes hidden folders
    subdirectories = [f for f in os.listdir(directory) if not f.startswith(".")]

    return subdirectories


def create_module_folders(data_model):
    """Creates the subdirectories for the documents that are the pages within the website. If the page folder
        if the page does not exist in the "module" column in the data model, it is removed.

    Args:
        data_model (data.frame): the data model for the project
    """

    BASE_PATH = "docs"

    # get current subdirectories
    subdirectories = [f for f in os.listdir(BASE_PATH) if not f.startswith(".")]

    module_list = data_model["Module"].dropna().unique().tolist()

    # delete old directories
    for s in subdirectories:
        if s not in module_list:
            try: 
                shutil.rmtree(f"{BASE_PATH}/{s}")
            except: 
                pass

    # create new folders
    for m in module_list:
        new_path = os.path.join(BASE_PATH, m)
        if os.path.exists(new_path):
            print("Path already exists")
        else:
            print(f"Creating {m} directory")
            os.mkdir(new_path)

    print("Done")


def create_module_dict(module):
    """The template for a module dictionary that will be used to populate its markdown file

    Args:
        module (str): name of the module

    Returns:
        dict: module attributes
    """

    module_dict = {}
    module_dict["name"] = module
    module_dict["url"] = f"https://github.com/github/{module}"
    module_dict["description"] = ""

    return module_dict


def create_module_page(subdirectories):
    """Create the module pages

    Args:
        subdirectories (list): list of the subdirectories in docs to create markdown pages for
    """
    # render the template page
    with open("_layouts/template_page_template.md", "r") as file:
        template = Template(file.read(), trim_blocks=True)

    for m in subdirectories:
        dictionaries = [create_module_dict(m) for m in subdirectories]

    for n, module_dict in enumerate(dictionaries):
        rendered_file = template.render(module=module_dict, nav_order=n)

        with open(
            f"./docs/{module_dict['name']}/{module_dict['name']}.md",
            "w",
            encoding="utf-8",
        ) as output_file:
            output_file.write(rendered_file)


def main():
    data_model = pd.read_csv(config["csv_model_link"])

    data_model = data_model[["Attribute", "Description", "columnType", "Source", "Module"]]

    # rename columns
    data_model = data_model.rename(
        {"Attribute": "Key", "Description": "Key Description"}
    )

    # Clean up doc folders
    create_module_folders(data_model)

    # get subdirectories/module folders
    subdirectories = get_subdirectories("./docs")

    create_module_page(subdirectories)


if __name__ == "__main__":
    main()
