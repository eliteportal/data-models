"""
Tools for creating the data model

"""

import re
import json
from pathlib import Path
import pandas as pd


def get_templates(root_dir, jsonld_name):
    # Get manifest names to generate manifests
    json_model_path = Path(root_dir, jsonld_name)

    # ================ FIND TEMPLATES IN DATA MODEL ================ #
    with open(json_model_path, "r", encoding="UTF-8") as f:
        dm_json = json.load(f)

    # get template names
    for i in dm_json["@graph"]:
        try:
            if bool(re.search("template", i["@id"])):
                # print(i)
                templates = [
                    v for n in i["schema:domainIncludes"] for _, v in n.items()
                ]
        except KeyError:
            pass
    # Manifest template names in data model
    manifest_schemas = []

    for i in dm_json["@graph"]:
        try:
            if i["@id"] in templates:
                if bool(
                    re.search("individual|biospecimen", i["@id"], flags=re.IGNORECASE)
                ):
                    record_type = "record"
                else:
                    record_type = "file"

                temp_template = {
                    "display_name": i["sms:displayName"],
                    "schema_name": i["@id"].strip("bts:"),
                    "type": record_type,
                }

                manifest_schemas.append(temp_template)
        except KeyError:
            pass

    # see results
    manifest_schemas_df = (
        pd.DataFrame(manifest_schemas)
        .sort_values(["type", "display_name"], ascending=True)
        .reset_index(drop=True)
    )

    return manifest_schemas, manifest_schemas_df
