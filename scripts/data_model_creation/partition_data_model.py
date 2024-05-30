#!usr/bin/env python

"""Create partitions from the data model based on the Parent names

Args:
    data_model (object): dataframe that contains the data model
    partition_path (str): directory to store the partitioned data model as CSVs
"""

import globw
import pandas as pd
import re
import synapseclient as sc
from pathlib import Path
from tqdm import tqdm
import shutil
import os

dm_path = "EL.data.model.csv"
output_path = "backups"
partition_path = "modules"
root_dir_name = "ELITE-data-models"

syn = sc.login()

cwd = Path(__file__).resolve()

root_dir = None
for p in cwd.parents:
    if bool(re.search(root_dir_name + "$", str(p))):
        print(p)
        root_dir = p
        os.chdir(root_dir)

if root_dir is None:
    raise ValueError("No root directory found")

dm = pd.read_csv(dm_path)
dm["module"] = dm["module"].fillna("Unknown")

# Split by Parent
modules = dm["module"].dropna().unique()

# clean modules folders
existing_dir_mods = [s.strip("/") for s in glob.glob("**/", root_dir=partition_path)]

for e in list(set(existing_dir_mods) - set(modules)):
    print("Removing directory: ", e)
    shutil.rmtree(Path(partition_path, e))

# create module directories
for m in list(set(modules) - set(existing_dir_mods)):
    mod_path = Path(partition_path, m)
    print(mod_path)
    mod_path.mkdir(parents=True, exist_ok=True)

# check for existing csv files
existing_csvs = glob.glob("**/*.csv", recursive=True, root_dir=partition_path)
existing_attrs = [Path(e).stem for e in existing_csvs]
existing_df = pd.DataFrame(
    {"csv_paths": existing_csvs, "existing_attrs": existing_attrs}
)
existing_df["module"] = existing_df["csv_paths"].apply(lambda x: str(Path(x).parent))

# create template CSV
template_df = dm.loc[dm["module"] == "template"]
template_df.to_csv("modules/template/templates.csv")
dm = dm.loc[dm["module"] != "template"]

for i in tqdm(range(len(dm)), desc="Updating module CSVs"):
    try:
        attr = dm.loc[i, "Attribute"]
        module = dm.loc[i, "module"]
        csv_path = Path(module, attr + ".csv")
        full_csv_path = Path(partition_path, csv_path)
        # full_csv_path.parent.mkdir(parents=True, exist_ok=True)
        checker = existing_df[existing_df["existing_attrs"] == attr]

        if all(checker["module"] == module):
            # print('CSV already exists')
            pass  # need to do comparison later

        elif all(checker["module"] != module):  # if module is different
            # remove old csv
            # print("Removing old CSV file: ", attr)
            # os.remove(full_csv_path)

            # create new csv
            print("Creating new CSV: ", csv_path)
            dm.loc[i,].to_csv(full_csv_path, index="ignore")

        else:
            # create new csv
            dm.loc[i,].to_csv(full_csv_path, index="ignore")

    except Exception as e:
        print(attr, e)


print("Done partitioning data model into modules")
