# Scripts

- [Scripts](#scripts)
  - [Adding an RFC](#adding-an-rfc)
  - [Process](#process)
- [Updating the Data Model](#updating-the-data-model)
  - [Main](#main)

Used for the automated processes. Conducts tests to ensure that the data model templates are properly generated

## Adding an RFC

1. Download RFC and place in `/data/rfc_tables_raw`
2. `clean_raw_rfc.py` will output new cleaned CSV to `/data/rfc_tables_cleaned`
3. Run `python add_new_term.py -d <> -n <>` to add the new term to the data model
4. Run `python create_data_model.py` to regenerate the JSON-LD data model
5. Run the test under `tests/scripts/tests_generate_manifests.py` to determine if all the manifests can be generated
6. Test validating the new manifests using `python test_manifest_validation.py`
7. If all the tests pass, update the data model

## Process

- RFC to data model
- Hard code fixes
- scrape valid values
- split data model into modules
- Create Data Model from modules if modules are updated

# Updating the Data Model

## Main

- Use `update_data_model.sh` to:
    1. split the data model into modules
    2. test the generation of manifests
