#! bin/bash python3
"""
Name: get_data_model.py
definition: Update data model in this directory with the data model from the data-model repo
Contributors: Nicholas Lee

Notes: 
- NA
"""

# update EL model in repo with data-models version
from utils import utils
from pathlib import Path
from dotenv import dotenv_values


def main():
    ROOT_DIR = Path(__file__).parents[1]
    config = dotenv_values(".env")
    url = config["csv_model_link"]
    try:
        df = utils.load_and_backup_dm(url, Path(ROOT_DIR, "backups").resolve())
        df.to_csv(Path(ROOT_DIR, "EL.data.model.csv").resolve(), index=False)
        print(Path(ROOT_DIR, "EL.data.model.csv").resolve())
        print("\033[92m Successfully updated data model \033[00m")
    except Exception as e:
        print("\033[31m Unable to update data model \033[00m")
        print(e)


if __name__ == "__main__":
    main()
