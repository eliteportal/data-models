#!/bin/bash

set -e

MANIFEST='Biospecimenhuman'

schematic schema convert ./EL.data.model.csv \
  --output_jsonld ./EL.data.model.jsonld

# !echo $MANIFEST":" >> manifest_generation_results.txt
RESULTS=$(schematic manifest --config ./config.yml \
  get -dt $MANIFEST \
  --output_csv ./manifests/$MANIFEST.csv \
  --title EL_Manifest_$MANIFEST \
  --sheet_url)

echo $RESULTS

echo $MANIFEST ": " $RESULTS >>./_data/manifest_generation_results.txt
