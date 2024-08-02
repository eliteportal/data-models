#!/bin/bash

# install dependencies from poetry lock file
poetry install

# open virtual environment with poetry shell
poetry shell

# write schematic gsheets creds to file for schematic to use
echo $SCHEMATIC_SERVICE_ACCOUNT_CREDS > ./schematic_service_account_creds.json