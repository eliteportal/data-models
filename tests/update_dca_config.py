""" 
Check any differences exist between the data model and the dca-template-config.json file so that templates generate in DCA.

Assumes the newest data model is correct. 

Need to find way to update type
"""

import json
from pathlib import Path
import re
import pandas as pd
from test_suite.utils import get_template_labels, get_root_dir, compare_dfs, bcolors


def main(JSONLD_PATH):

    # Get manifest names to generate manifests
    ROOT_DIR = get_root_dir("ELITE-data-models")

    with open(Path(ROOT_DIR, "dca-template-config.json"), "r", encoding="UTF-8") as f:
        template_config = json.load(f)

    config_df = pd.DataFrame(template_config["manifest_schemas"])

    with open(Path(ROOT_DIR, JSONLD_PATH), "r", encoding="UTF-8") as jf:
        jsonld_dm = json.load(jf)

    # get all the template labels from the data model JSON-LD
    template_df = get_template_labels(jsonld_dm)

    # match the column names with the DCA template config
    col_map = {"label": "schema_name", "displayName": "display_name"}
    template_df = template_df.rename(columns=col_map)

    # for easier comparisons
    config_df["schema_name_lower"] = config_df["schema_name"].str.lower()
    template_df["schema_name_lower"] = template_df["schema_name"].str.lower()

    df = compare_dfs(
        config_df, template_df, ["schema_name_lower"], keys=["config", "dm"]
    )

    print("\n")
    print(" --- Differences --- ")
    print(df[df["config"] != df["dm"]])
    print("\n")

    update_config = str(input("Update DCA template config y/[n]: ") or "n")

    if update_config.lower() == "y":
        df["config"].update(df["dm"])

        df = df["config"].unstack().reset_index(drop=True)
        # update config
        template_config["manifest_schemas"] = df.to_dict("records")

        # update version
        increment = float(
            input("Increment data model schema version by (default 0.1): ") or 0.1
        )

        print("Current schema versiona: ", template_config["schema_version"])

        template_config["schema_version"] = "v" + str(
            float(re.sub("v", "", template_config["schema_version"])) + float(increment)
        )
        print("New schema version: ", template_config["schema_version"])

        with open(
            Path(ROOT_DIR, "dca-template-config.json"), "w", encoding="UTF-8"
        ) as outfile:
            json.dump(template_config, outfile, indent=4)

        print(bcolors.OKGREEN + "--- New configuration --- " + bcolors.ENDC)
        print(json.dumps(template_config, indent=4))


if __name__ == "__main__":
    # add argument parser later
    JSONLD_PATH = "EL.data.model.jsonld"
    main(JSONLD_PATH)
