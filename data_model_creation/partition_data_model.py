#!usr/bin/env python

"""Create partitions from the data model based on the Parent names

Args:
    data_model (object): dataframe that contains the data model
    partition_path (str): directory to store the partitioned data model as CSVs
"""

import glob
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

# create template CSV
template_df = dm.loc[dm["module"] == "template"]
template_df.to_csv("modules/template/templates.csv")
dm = dm.loc[dm["module"] != "template"]

for i, r in tqdm(
    dm.iterrows(),
    desc="Updating module CSVs",
):
    try:
        attr = r["Attribute"]
        module = r["module"]
        csv_path = Path(module, attr + ".csv")
        full_csv_path = Path(partition_path, csv_path)

        if not full_csv_path.exists():
            print("Creating new CSV: ", csv_path)
            pd.DataFrame(r).T.to_csv(full_csv_path, index=False)

        else:
            # print('CSV already exists')
            pass

    except Exception as e:
        print(attr, e)
        pass


print("Done partitioning data model into modules")
