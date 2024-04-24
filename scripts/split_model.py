""" 
Split data model by "Module"

TODO: 
- [ ] add arg parse later 
"""

from pathlib import Path
from toolbox import utils
import pandas as pd


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

    # incase any are missing
    data_model.loc[data_model["Module"].isna(), "Module"] = data_model.loc[
        data_model["Module"].isna(), "Module"
    ].fillna("Unlabeled")

    create_modules(root_dir, data_model)
