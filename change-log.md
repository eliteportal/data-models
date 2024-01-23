# Change Log

## 2024-01-19

Changes:

- Added `dataCoordinationCenter` to denote which center hosts the data in Synapse. This could be inferred by the portal that the data is surfaced in.
- Updated `consortium` to denote which contributing center (LLFS / ILO / LC / LG) the data is coming from. This way so that multiple studies can exist under one `consortium`

## 2024-01-17

Adding additional templates

1. proteomics
2. ComputationalTools

## 2023-12-15

- Removed cross validation

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

## Oct 20th, 2023

Attribute renaming to harmonize with current backend and ADKP

- consortium -> program
- studyCode -> project
- study -> studyKey

New Terms

- 'studyFocs'
  - valid values are 'Longevity' currently.

Attribute Changes:

- Remove valid values from speciesName

File Annotation Updates

- change "species" to "speciesGroup"
