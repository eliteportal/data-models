#!usr/bin/env python
""" 
Split data model by "Module"

TODO: 
- [ ] add arg parse later 
"""

import os
from glob import glob
from pathlib import Path
import pandas as pd
from toolbox import utils


def create_modules(root_dir, data_model) -> None:

    base_path = Path(root_dir, "modules")
    # create parent directories if they do not exist

    Path(base_path).mkdir(parents=True, exist_ok=True)

    for m in data_model["Module"].unique():
        module_path = Path(root_dir, f"modules/{m}.csv")
        print(module_path)
        data_model.loc[data_model["Module"] == m].to_csv(module_path, index=False)


if __name__ == "__main__":

    ROOT_DIR_NAME = "ELITE-data-models"

    root_dir = utils.get_root_dir(ROOT_DIR_NAME)

    dm_name = Path(root_dir, "EL.data.model.csv")

    data_model = pd.read_csv(Path(root_dir, "EL.data.model.csv"))

    # check what files are not part of the modules in the data model and delete them
    check_files = [
        [p, Path(p).stem] for p in glob(str(Path(root_dir, "modules")) + "/*.csv")
    ]

    for file_path, module in check_files:
        if module not in data_model["Module"].unique():
            os.remove(file_path)

    # incase any are missing
    data_model.loc[data_model["Module"].isna(), "Module"] = data_model.loc[
        data_model["Module"].isna(), "Module"
    ].fillna("Unlabeled")

    create_modules(root_dir, data_model)
