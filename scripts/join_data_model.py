""" Join the data model modules """

import glob
import pandas as pd
import pathlib


def join_data_model_partitions(partition_path):
    """Join the partitions back together to form the data model used in DCA

    Args:
        partition_path (str): directory containing the partitions as CSVs

    Returns:
        object: pandas dataframe
    """
    modules = glob.glob(partition_path)

    data_model = (
        pd.concat([pd.read_csv(m) for m in modules])
        .sort_values(by=["Module", "Attribute"])
        .reset_index(drop=True)
        .fillna("")
    )

    data_model.drop_duplicates(subset=["Attribute"], inplace=True)
    data_model.reset_index(drop=True, inplace=True)

    return data_model


if __name__ == "main":
    root_dir = pathlib.Path(__file__).parent.parent

    module_pattern = root_dir.resolve()._str + "/modules/*.csv"

    file_path = pathlib.Path(root_dir, "EL.data.model.csv")

    dm = join_data_model_partitions(module_pattern)

    dm.to_csv(file_path, index=False)
