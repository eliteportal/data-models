import pathlib
import pandas as pd
import utils

if __name__ == "main":
    root_dir = pathlib.Path(__file__).parent.parent

    dm_name = pathlib.Path(root_dir, "EL.data.model.csv")
    output_path = pathlib.Path(root_dir, "backups")
    data_model = utils.load_and_backup_dm(dm_name, output_path)

    for m in data_model["Module"].unique():
        print(pathlib.Path(root_dir, f"modules/{m}.csv"))
        data_model.loc[data_model["Module"] == m].to_csv(
            pathlib.Path(root_dir, f"modules/{m}.csv"), index=False
        )
