#!/bin/bash
# generate GoogleSheets templates
# if using locally run with ./generate_all_manifests.sh from tests directory

set -e

TEST_CONFIG_PATH=../dca-template-config.json
TEST_CONFIG=dca-template-config.json
SCHEMATIC_CONFIG_PATH=../schematic_config.yml
SCHEMATIC_CONFIG=schematic_config.yml
CREDS_PATH=../schematic_service_account_creds.json
CREDS=./schematic_service_account_creds.json
DATA_MODEL_PATH=../EL.data.model.jsonld
DATA_MODEL=EL.data.model.jsonld
EXCEL_DIR=../elite-data/manifest-templates
JSON_DIR=../elite-data/current-manifest-schemas
LOG_DIR=../elite-data/logs
SLEEP_THROTTLE=45 # API rate-limiting, need to better figure out dynamically based on # of templates

# copy schematic-config.yml into tests/ 
cp $SCHEMATIC_CONFIG_PATH $SCHEMATIC_CONFIG
echo "✓ Using schematic configuration settings from $SCHEMATIC_CONFIG"

# Setup for creds
if [ -f "$CREDS_PATH" ]; then
  cp $CREDS_PATH $CREDS
fi

# If testing locally, it might already be in folder; 
# Else, especially if in Actions or Codespace, we need to create it from env var
# See https://github.com/nf-osi/nf-metadata-dictionary/settings/secrets/codespaces
if [ -f "$CREDS" ]; then
  echo "✓ $CREDS -- running tests locally"
elif [ -n "${SCHEMATIC_SERVICE_ACCOUNT_CREDS}" ]; then
  echo "${SCHEMATIC_SERVICE_ACCOUNT_CREDS}" > $CREDS
  echo "✓ Created temp $CREDS for test"
else
  echo "✗ Failed to access stored creds. Aborting test."
  exit 1
fi

# Set up templates config
cp $TEST_CONFIG_PATH $TEST_CONFIG
echo "✓ Using copy of $TEST_CONFIG_PATH for test"

TEMPLATES=($(jq '.manifest_schemas[] | .schema_name' $TEST_CONFIG | tr -d '"'))
echo "✓ Using config with ${#TEMPLATES[@]} templates..."

# Setup data model
cp $DATA_MODEL_PATH $DATA_MODEL
echo "✓ Set up $DATA_MODEL for test"

# Setup logs
mkdir -p $LOG_DIR

# Setup schema dir
mkdir -p $JSON_DIR

for i in ${!TEMPLATES[@]}
do
  echo ">>>>>>> Generating ${TEMPLATES[$i]}"
  schematic manifest --config "$SCHEMATIC_CONFIG" get -dt "${TEMPLATES[$i]}" -p "$DATA_MODEL" -oxlsx "$EXCEL_DIR/EL_template_${TEMPLATES[$i]}.xlsx" | tee $LOG_DIR/${TEMPLATES[$i]%.*}_log
  sleep $SLEEP_THROTTLE
done

echo "Moving manifest json schemas to $JSON_DIR"
mv *.schema.json $JSON_DIR

echo "Cleaning up test directory"
rm -f $CREDS $TEST_CONFIG $DATA_MODEL *.manifest.csv

echo "✓ Done!"