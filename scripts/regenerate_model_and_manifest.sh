#!/usr/bin/env bash

set -e

# MANIFEST='BiospecimenNonHuman'

date "+%H:%M:%S   %d/%m/%y"
schematic schema convert ./EL.data.model.csv \
  --output_jsonld ./EL.data.model.jsonld
date "+%H:%M:%S   %d/%m/%y"

for MANIFEST in 'Proteomics'; do
  echo -- $MANIFEST

  RESULTS=$(
    schematic manifest --config ./config.yml \
      get -dt $MANIFEST \
      -s -oxlsx EL.Manifest.$MANIFEST.xlsx
  )

  echo $RESULTS
  NOW=$(date -f "%d/%m/%y +%H:%M:%S")
  echo $NOW $MANIFEST ": " $RESULTS >>./data/manifest_generation_results.txt
  echo -----------------------------
done
