#!/bin/bash

set -e

MANIFEST='Biospecimenhuman'
MAINFEST_PATH = 

schematic model --config ./config.yml validate \
    --manifest_path ./test_manifests/Biospecimenhuman_test.csv \
    --data_type $MANIFEST
