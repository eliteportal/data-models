#!/usr/bin python

"""
Update dca-template-config.json so DCA pulls the right templates from the data model

TODO: 
- [ ] More robust errors
"""

import re
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
from utils.utils import get_root_dir, bcolors
from utils.data_model_tools import get_templates

# Get manifest names to generate manifests
ROOT_DIR = get_root_dir("ELITE-data-models")
JSON_PATH = Path(ROOT_DIR, "EL.data.model.jsonld")
TEMPLATE_PATH = Path(ROOT_DIR, "dca-template-config.json")


def main():
    """ UPDATE DATA MODEL TEMPLATE FOR DCA """ 
    with open(TEMPLATE_PATH, "r", encoding="UTF-8") as f:
        template_config = json.load(f)

    # ================ GET TEMPLATES ================ #
    manifest_schemas, manifest_schemas_df = get_templates(ROOT_DIR, JSON_PATH)

    print(manifest_schemas_df.to_markdown(index=False))
    print()
    print("Shape: ", manifest_schemas_df.shape)

    # difference
    m = manifest_schemas_df.merge(
        pd.DataFrame(template_config["manifest_schemas"]),
        on="display_name",
        how="outer",
        suffixes=["_new", "_previous"],
        indicator=True,
    )
    print(m[sorted(list(m.columns))].to_markdown(index=False))

    # ================ UPDATE DCA TEMPLATE CONFIG ================ #
    update_config = str(input("Update DCA template config y/[n]: ") or "n")

    if update_config.lower() == "y":
        # UPDATE MANIFESTS
        template_config["manifest_schemas"] = manifest_schemas
        template_config["schema_version"] = "v" + datetime.now().strftime(
            "%Y.%m.%d"
        )  # increment schema version

        print(bcolors.OKGREEN + "--- New configuration --- " + bcolors.ENDC)
        print(json.dumps(template_config, indent=4))

        with open(TEMPLATE_PATH, "w", encoding="UTF-8") as f:
            json.dump(template_config, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
