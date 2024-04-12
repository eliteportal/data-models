# Tests to use when updating the data model

## File Descriptions

`/scripts/*`

- tests_generate_manifests.py

`tests/test_manifests/*`

- Manifests used for validating the different manfiests in the data model

- `tests/identify_changed_manifests_for_testing.py`
- `tests/test-suite-report.py`
- `tests/generate_test_manifests.sh`

## Tests

### For new templates

- Number of templates stays the same or goes up

### New Attributes

- All attributes are unique
- Attribute do not exist in data model, if they do, update them appropriately

### Data Model / Manifests

- Able to generate all manfiests using schematic
- Able to generate manifests in [DCA](https://dca.app.sagebionetworks.org/)
  - If not, check `dca-template-config.json`
- Able to validate manifests
