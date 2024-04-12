""" Join the data model modules """

from glob import glob
import pandas as pd
from pathlib import Path
from toolbox import utils


def join_data_model_partitions(partition_path):
    """Join the partitions back together to form the data model used in DCA

    Args:
        partition_path (str): directory containing the partitions as CSVs

    Returns:
        object: pandas dataframe
    """
    modules = glob(partition_path)

    print(modules)

    data_model = (
        pd.concat([pd.read_csv(m) for m in modules])
        .sort_values(by=["Module", "Attribute"])
        .reset_index(drop=True)
        .fillna("")
    )

    print("Data model shape BEFORE cleaning: ", data_model.shape)
    data_model.drop_duplicates(subset=["Attribute"], inplace=True)
    data_model.reset_index(drop=True, inplace=True)
    print("Data model shape AFTER cleaning: ", data_model.shape)

    return data_model


if __name__ == "__main__":

    root_dir_name = "ELITE-data-models"

    root_dir = utils.get_root_dir(root_dir_name)

    module_pattern = root_dir.resolve()._str + "/modules/*.csv"

    file_path = Path(root_dir, "EL.data.model.csv")

    dm = join_data_model_partitions(module_pattern)

    dm.to_csv(file_path, index=False)
