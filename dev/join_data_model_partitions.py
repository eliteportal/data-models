import glob
import pandas as pd


def write_out_data_model(data_model, file_path):
    data_model.drop_duplicates(subset=["Attribute"], inplace=True)
    data_model.reset_index(drop=True, inplace=True)
    data_model.to_csv(file_path, index=False)


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

    data_model.info()

    return data_model


def main():
    partition_path = "../models/partitions/*.csv"
    file_path = "../EL.data.model.csv"

    # backup data model?

    dm = join_data_model_partitions(partition_path)

    write_out_data_model(dm, file_path)


if __name__ == "main":
    main()
