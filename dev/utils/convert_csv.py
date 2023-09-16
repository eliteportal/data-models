import yaml
import pathlib

with open("./local_configs/notebook_config.yaml", "r") as f:
    config = yaml.safe_load(f)

csv_model = pathlib.Path(config["file_names"]["csv_model"]).resolve()
json_model = pathlib.Path(config["file_names"]["json_model"]).resolve()
