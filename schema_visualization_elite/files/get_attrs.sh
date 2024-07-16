#!bin/bash

SCHEMA_URL=$(yq .schema_url ./config.yml)
PROJECT="ELITE"

# tangled_tree/layers isn't always working
curl -X 'GET' \
    "https://schematic.api.sagebionetworks.org/v1/visualize/tangled_tree/layers?schema_url=$SCHEMA_URL&figure_type=component" \
    -H 'accept: text/json' -o "./JSON/$PROJECT-tangled-tree.json"

# attributes table
curl -X 'GET' \
    "https://schematic.api.sagebionetworks.org/v1/visualize/attributes?schema_url=$SCHEMA_URL" \
    -H 'accept: text/csv' -o "./Merged/$PROJECT-attribute-table.csv"
