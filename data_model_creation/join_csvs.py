"""Join the data model module CSVs into a single combined CSV."""

from glob import glob
from pathlib import Path
import re
import pandas as pd


def join_data_model_partitions(partition_path: str) -> pd.DataFrame:
    """Join module CSVs into a single data model dataframe.

    Args:
        partition_path: glob pattern for module CSV files

    Returns:
        pandas DataFrame of the combined, deduplicated data model
    """
    modules = glob(partition_path)

    print(modules)

    data_model = (
        pd.concat([pd.read_csv(m) for m in modules])
        .sort_values(by=["module", "Attribute"])
        .reset_index(drop=True)
        .fillna("")
    )

    print("Data model shape BEFORE cleaning: ", data_model.shape)
    data_model.drop_duplicates(subset=["Attribute"], inplace=True)

    drop_cols = [
        s
        for s in data_model.columns
        if bool(re.search("unnamed", s, flags=re.IGNORECASE))
    ]

    data_model = data_model.drop(columns=drop_cols)
    data_model["Required"] = data_model["Required"].fillna(False).astype(bool)
    data_model["multivalue"] = data_model["multivalue"].fillna(False).astype(bool)
    data_model.reset_index(drop=True, inplace=True)

    print("Data model shape AFTER cleaning: ", data_model.shape)

    return data_model


if __name__ == "__main__":
    from utils import utils

    ROOT_DIR_NAME = "data-models"
    ROOT_DIR = utils.get_root_dir(ROOT_DIR_NAME)

    module_pattern = str(ROOT_DIR.resolve()) + "/modules/**/*.csv"
    file_path = Path(ROOT_DIR, "EL.data.model.csv")

    dm = join_data_model_partitions(module_pattern)
    dm.to_csv(file_path, index=False)
    print(f"Wrote combined data model to {file_path}")
