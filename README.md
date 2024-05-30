# ELITE Data Model

- [ELITE Data Model](#elite-data-model)
  - [Production data model](#production-data-model)
  - [Editing data models](#editing-data-models)
    - [Github branch procedure](#github-branch-procedure)
    - [Editing attributes by module](#editing-attributes-by-module)
      - [Adding a new valid value to an existing manifest column](#adding-a-new-valid-value-to-an-existing-manifest-column)
      - [Adding a new column to a manifest template](#adding-a-new-column-to-a-manifest-template)
    - [Notes on collaboratively editing csvs](#notes-on-collaboratively-editing-csvs)
    - [Scraping Valid Values from Ontology](#scraping-valid-values-from-ontology)
  - [Automations](#automations)
    - [Updates to data model](#updates-to-data-model)
    - [Updating the data dictionary](#updating-the-data-dictionary)
    - [Adding a new template](#adding-a-new-template)
  - [Developing in a codespace](#developing-in-a-codespace)
  - [Legacy data models](#legacy-data-models)
    - [Create Data Model Visualization Tree](#create-data-model-visualization-tree)
  - [Developers](#developers)
    - [Files](#files)
    - [To setup environment](#to-setup-environment)
      - [Submodules](#submodules)
  - [Changes](#changes)

## Production data model

**EL.data.model.\* ([csv](https://raw.githubusercontent.com/eliteportal/data-models/main/EL.data.model.csv) | [jsonld](https://raw.githubusercontent.com/eliteportal/data-models/main/EL.data.model.jsonld))**: this is the current, "live" version of the EL Portal data model. It is being used by both the staging and production versions of the multitenant Data Curator App.

## Editing data models

:warning: Do **not** edit `EL.data.model.csv` or `EL.data.model.jsonld` by hand! :warning:

### Github branch procedure

The main branch of this repo is protected, so you cannot push changes to main. To make changes to the data model:

1. Create a new branch in this repo and give it an informative name. The schema-convert workflow will not work from a private fork.
2. On that branch, make and commit any changes. You can do this by cloning the repo locally or by [using a Github codespace](#developing-in-a-codespace). Please write informative commit messages in case we need to track down data model inconsistencies or introduced bugs.
3. Open a pull request and request review from someone else on the AD DCC team. The Github Action described in [Automation](#automation) will run as soon as you open the PR. If this action fails, something about the data model csv could not be converted to a json-ld and should be investigated. If this action passes, the PR can be merged with one approving review.
4. After the PR is merged, delete your branch.

### Editing attributes by module

The full `EL.data.model.csv` file has over 1400 attributes and is unwieldy to edit and hard to review changes for. For ease of editing, the full data model is divided into "module" subfolders, like so:

```
data-models/
├── EL.data.model.csv (do not edit!)
├── EL.data.model.jsonld (do not edit!)
└── modules/
    ├── biospecimen/
    │   ├── specimenID.csv
    │   ├── organ.csv
    │   └── tissue.csv
    └── sequencing/
        ├── readLength.csv
        └── platform.csv
```

Within each module, every attribute in the data model has its own csv, named after that attribute (example: `organ.csv`). 

Some common data model editing scenarios are:

#### Adding a new valid value to an existing manifest column

1. If you wanted to add a new valid value "eyeball" to our existing column attribute "organ", after making a new branch and opening the repo either locally or within a codespace, you would go to `modules/biospecimen/organ.csv`.
2. Then, create a new row for an attribute named "eyeball", with a description and source (preferably an ontology URI). In the `Parent` column, make sure the value is "organ".
3. Next, find the row for the attribute "organ" (should be the first row), and w/in the valid values column, add "eyeball" to the comma-separated list of valid values.
4. Save your changes and write an informative commit. Please try to add valid values alphabetically!

#### Adding a new column to a manifest template

1. If you wanted to add the column "furColor" to the "model-ad_individual_animal_metadata" template, first decide which module the new column should belong to. In this case, "MODEL-AD" makes the most sense.
2. W/in the `MODEL-AD` subfolder, create a new csv called `furColor.csv` with the required schematic column headers. Describe the attribute "furColor" as necessary and make sure `Parent` = `DataProperty`. Add any valid values for "furColor" as new rows to this csv as described in the previous scenario.
3. Find the manifest template attributes in `modules/template/templates.csv`. In the "model-ad_individual_animal_metadata" row, add your new column "furColor" to the comma-separated list of attributes in the `DependsOn` column.
4. Save your changes and write an informative commit.

For more advanced data modeling scenarios like adding conditional logic, creating validation rules, or creating new manifests, please consult the #ad-dcc-team slack channel.

### Notes on collaboratively editing csvs

A persistent issue is that manually editing csvs is challening. Some columns in our modules are very short, and others are veeeeery long (Description, Valid Values). Some options for working on csvs, and their pros and cons:

- Editing in the Github UI :octocat: : convenient, but challenging to keep track of columns in plain text format.
- Cloning the repo, making a branch, and opening csvs locally in Excel or another spreadsheet program 🖥️ : probably the best UI experience, but involves a few extra steps with git.
- Using a [Github codespace](#developing-in-a-codespace) to launch VSCode in the browser, and editing with the pre-installed RainbowCSV extension 🌈 : Still difficult to edit csvs as plain text, but the color formatting and ability to use a soft word wrap makes it much easier to distinguish columns. [RainbowCSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv) lets you designate "sticky" rows and columns for easier scrolling, and also has a nice "CSVLint" function that will check for formatting errors after you make changes.

We are exploring better solutions to this problem -- if you have ideas, tell us!

### Scraping Valid Values from Ontology

Use `scraping_valid_values.py` to pull in values from EBI OLS sources. 

## Automations

When you open a PR that includes any changes to files in the `modules/` directory, a Github Action will automatically run before merging is allowed. This action:

### Updates to data model

1. Runs the `assemble_csv_data_model.py` script to concatenate the modular attribute csvs into one data frame, sort alphabetically by `Parent` and then `Attribute`, and write the combined dataframe to `EL.data.model.csv`. The action then commits the changes to the master data model csv.
2. Installs `schematic` from the develop branch and runs `schema convert` on the newly-concatenated data model csv to generate a new version of the jsonld file `EL.data.model.jsonld`. The action also commits the changes to the jsonld.

If this automated workflow fails, then the data model may be invalid and further investigation is needed.

### Updating the data dictionary

1. Runs `update-data-dictionary.yaml` in order to reflect information found in the dictionary for contributors


### Adding a new template

Recreates DCA template config

- Run the github action `create-template-config.yml` when adding new templates

## Developing in a codespace

:warning: If you are working in a Github Codespace, do NOT commit any Synapse credentials to the repository and do NOT use any real human data when testing data model function. This is not a secure environment!

If you want to make changes to the data model and test them out by generating manifests with `schematic`, you can use the devcontainer in this repo with a Github Codespace. This will open a container in a remote instance of VSCode and install the latest version of schematic.

Codespace secrets:

- SYNAPSE_PAT: scoped to view and download permissions on the sysbio-dcc-tasks-01 Synapse service account
- SERVICE_ACCOUNT_CREDS: these are creds for using the Google sheets api with schematic

## Legacy data models

Previous versions of the data model live in the `legacy-data-models/` folder. This include the Diverse Cohorts pilot model and the intial "legacy" model representing the AD Portal Synapse project metadata dictionary and metadata templates from August 2023. These are not being used by DCA.

### Create Data Model Visualization Tree

[Schematic API](https://schematic.api.sagebionetworks.org/v1/ui/)
[Visualization Repository](https://github.com/Sage-Bionetworks/schema_visualization)

- Creates a network graph of the data model. Aim is to help see connections between components.

## Developers

Software packages installed

- Poetry - [See installation guide here](https://python-poetry.org/docs/)
- pyenv - [See guide here](https://github.com/pyenv/pyenv)

### Files

1. `EL.data.model.csv`: The CSV representation of the example data model. This file is created by the collective effort of data curators and annotators from a *community* (e.g. *ELITE*), and will be used to create a JSON-LD representation of the data model.

2. `EL.data.model.jsonld`: The JSON-LD representation of the example data model, which is automatically created from the CSV data model using the schematic CLI. More details on how to convert the CSV data model to the JSON-LD data model can be found [here](https://sage-schematic.readthedocs.io/en/develop/cli_reference.html#schematic-schema-convert). This is the central schema (data model) which will be used to power the generation of metadata manifest templates for various data types (e.g., `scRNA-seq Level 1`) from the schema.

3. `config.yml`: The schematic-compatible configuration file, which allows users to specify values for application-specific keys (e.g., path to Synapse configuration file) and project-specific keys (e.g., Synapse fileview for community project). A description of what the various keys in this file represent can be found in the [Fill in Configuration File(s)](https://sage-schematic.readthedocs.io/en/develop/README.html#fill-in-configuration-file-s) section of the schematic [docs](https://sage-schematic.readthedocs.io/en/develop/index.html).


### To setup environment

After cloning the repository, run the following command:
```poetry install```

#### Submodules

This repository includes three submodules

1. `data-dictionary`
   - For creating a site that displays the data model

## Changes

`./change-log.md`
