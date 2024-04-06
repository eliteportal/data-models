#!/bin/bash

set -e

# MANIFEST='BiospecimenNonHuman'

# date "+%H:%M:%S   %d/%m/%y"
# schematic schema convert ./EL.data.model.csv \
#   --output_jsonld ./EL.data.model.jsonld
# date "+%H:%M:%S   %d/%m/%y"

for MANIFEST in 'Biospecimenhuman'; do
  echo -- $MANIFEST

  RESULTS=$(schematic manifest --config ./config.yml \
    get -dt $MANIFEST \
    --output_xlsx EL.Manifest.$MANIFEST.xlsx \
    --title EL.Manifest.$MANIFEST \
    --sheet_url)

  echo $RESULTS
  NOW=$(date -f "%d/%m/%y +%H:%M:%S")
  echo $NOW $MANIFEST ": " $RESULTS >>./_data/manifest_generation_results.txt
  echo -----------------------------
done
