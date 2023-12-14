#!/usr/bin/env python

"""
Module Docstring

__author__ = "Nicholas"
__version__ = "0.1.0"
__license__ = "MIT"
__description__ = "Script for turning the csv model into a jsonld model. WARNING: this can take a while to run."

*needs work: needs to generate manifests in `manifest-templates` folder, but it puts the filesl in the main folder.

"""

import pandas as pd
import json
import os
import synapseclient
from dotenv import dotenv_values
from glob import glob


# def main():


# if __name__ == "main":
"""Main entry point of the app"""
config = dotenv_values(".env")

# paths to run schematic
schematic_config = config["schematic_config_path"]
json_model_path = config["json_model_path"]
manifest_folder = config["manifest_folder_id"]
manifests = [""]

# with open(json_model_path, "r") as f:
#     json_model = json.loads(f)

# get manifest names from json
with open(json_model_path, "r", encoding="UTF-8") as f:
    json_model = json.load(f)

# Manifest names in data model
manifest_names_extracted = []

for i in json_model["@graph"]:
    try:
        if i["rdfs:subClassOf"][0]["@id"] == "bts:Template":
            manifest_names_extracted.append(i["@id"].replace("bts:", ""))
    except:
        pass

# display names extracted
manifest_display_names_extracted = []

for i in json_model["@graph"]:
    if i["@id"].replace("bts:", "") in (manifest_names_extracted):
        manifest_display_names_extracted.append(i["sms:displayName"])

# Create dictionary for lookup later
manifest_name_relationships = dict(
    zip(manifest_names_extracted, manifest_display_names_extracted)
)

CREATE_MANIFESTS = True  # whether to create the manifests again
if CREATE_MANIFESTS:
    # generate templates
    for k in manifest_name_relationships.keys():
        os.system(
            f"schematic manifest --config {config['schematic_config_path']} get -dt {k} --output_xlsx ./manifest-templates/EL.manifest.{k}.xlsx &> manifest-templates/manifest-generation.txt "
        )

# Upload templates
# ./manifest-templates/*.xlsx or .csv
syn = synapseclient.login()

manifest_files = glob("./manifest-templates/*manifest.csv")

ants = {"program": "ELITE", "resourceType": "manifest"}

for f in manifest_files:
    temp_file = synapseclient.File(path=f, parent=manifest_folder, annotations=ants)
    temp_file_stored = syn.store(temp_file)
