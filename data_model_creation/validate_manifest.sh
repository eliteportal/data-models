#!/usr/bin/env bash

set -e

MANIFEST='Biospecimenhuman'
MAINFEST_PATH = "./test_manifests/Biospecimenhuman_test.csv"

schematic model --config ./config.yml validate \
    --manifest_path $MAINFEST_PATH \
    --data_type $MANIFEST
