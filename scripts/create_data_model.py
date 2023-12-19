import os
from pathlib import Path
from dotenv import dotenv_values

# paths to import files
root_dir = Path(__file__).parent.parent

config = dotenv_values(Path(root_dir, ".env"))
schematic_config = Path(root_dir, config["schematic_config_path"])
csv_model = Path(root_dir, config["csv_path"])
json_model = Path(root_dir, csv_model.stem + ".jsonld")

# Initialize schematic
os.system(f"schematic init --config {config['paths']['schematic']}")

# Convert Schema
os.system(f"schematic schema convert {csv_model} --output_json {json_model}")

# Get an empty manifest as a CSV using model
os.system(f"schematic manifest --config {schematic_config} get")
