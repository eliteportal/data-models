#!/bin/bash

set -e

MANIFEST='Biospecimenhuman'

schematic schema convert C:/Users/nlee/Documents/Projects/ELITE-DCC/ELITE-data-models/models/EL_data_model_v3.csv \
  --output_jsonld C:/Users/nlee/Documents/Projects/ELITE-DCC/ELITE-data-models/models/EL_data_model_v3.jsonld;

# !echo $MANIFEST":" >> manifest_generation_results.txt
RESULTS=$(schematic manifest --config C:/Users/nlee/Documents/Projects/schematic/schematic/config.yml \
  get -dt $MANIFEST \
  --output_csv C:/Users/nlee/Documents/Projects/ELITE-DCC/ELITE-data-models/manifests/$MANIFEST.csv \
  --title EL_Manifest_$MANIFEST \
  --sheet_url)

echo $RESULTS

echo $MANIFEST ": " $RESULTS >> C:/Users/nlee/Documents/Projects/ELITE-DCC/notebooks/manifest_generation_results.txt