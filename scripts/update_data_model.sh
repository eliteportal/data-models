#!/usr/bin/env bash

python ./scripts/join_data_model.py

python ./tests/test_generate_manifests.py

sh update_data_dictionary.sh
