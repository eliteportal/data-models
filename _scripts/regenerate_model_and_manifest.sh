#!/bin/bash

set -e

MANIFEST='BiospecimenHuman'

# schematic schema convert ./EL.data.model.csv \
#   --output_jsonld ./EL.data.model.jsonld

RESULTS=$(schematic manifest --config ./config.yml \
  get -dt $MANIFEST \
  --output_csv ./manifest-templates/EL.Manifest.$MANIFEST.csv \
  --title EL.Manifest.$MANIFEST \
  --sheet_url)

echo $MANIFEST ": " $RESULTS >>./_data/manifest_generation_results.txt
