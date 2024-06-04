import subprocess
from glob import glob
from pathlib import Path
import re

cwd = Path(__file__)
ROOT_DIR_NAME = "ELITE-data-models"

for p in cwd.parents:
    if bool(re.search(ROOT_DIR_NAME + "$", str(p))):
        print(p)
        ROOT_DIR = p


# rfc files
rfc_tables = glob("data/rfc_tables_cleaned/*.csv")

for r in rfc_tables:
    command = f""" python scripts/add_new_term.py -d "EL.data.model.csv" -n "{r}" """

    proc = subprocess.Popen(
        command,
        cwd=ROOT_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = proc.communicate()

    print(r, proc.returncode)
