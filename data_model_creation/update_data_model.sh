#!/usr/bin/env bash

python data_model_creation/join_data_model.py

python data_model_creation/test_generate_manifests.py # will test all manifests are generated properly and then update the dca-template-config.json

sh data-dictionary/processes/main_workflow.sh   # update data dictionary with changes
