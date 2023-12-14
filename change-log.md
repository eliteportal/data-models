# Change Log

## 2023-12-13

### Value Changes

| Previous Value | New Value | Rationale |
|---|---|---|
|studyCode | project | Reflects the ordering used in the Synapse Backend|
| project | dcc | Project creates ambiguity with values like LLFS, LC, etc. and DCC is what the value represents |

### Valid Values and Validation Rule Changes

- Dropped `visitCode` requirement to be string
- Dropped requirement that `race` be a list, just has to be a string and comma separated values if it is a list
- Changed `age` type to string to allow for missing values like "Not collected"

### New Manifest Type

1. `file_annotation_template`
   - Adding dataRepository as column type for file annotations
