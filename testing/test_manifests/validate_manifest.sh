#!/bin/bash

set -e

MANIFEST='Biospecimenhuman'

schematic model --config C:/Users/nlee/Documents/Projects/schematic/schematic/config.yml validate \
    --manifest_path C:/Users/nlee/Documents/Projects/ELITE-DCC/ELITE-data-models/test_manifests/Biospecimenhuman_test.csv \
    --data_type $MANIFEST