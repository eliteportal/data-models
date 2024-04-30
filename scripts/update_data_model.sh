#!/usr/bin/env bash

# python ./scripts/join_data_model.py
python ./scripts/split_model.py

python ./tests/test_generate_manifests.py

sh data-dictionary/processes/main_workflow.sh
