# ELITE Data Model and Metadata Dictionary

As of 2024-07-17 this repo contains both the production data model used by the ELITE portal to submit and validate metadata through the Data Curator App; _and_ the data dictionary website which is based on the data model and provides definitions for all metadata templates and terms used in the data model. 

There is a separate [data-dictionary](https://github.com/eliteportal/data-dictionary) repo which contains the same source code, and which can later be used to deploy the website when we are able to set up automation in that repository which successfully monitors this repository for changes. To simplify the process, for now we will use this data-models repo to manage both the data model and the dictionary.

<!-- toc -->

- [EL Metadata Dictionary Site](#el-metadata-dictionary-site)
  * [Updating Metadata Dictionary Site -- interim processes](#updating-metadata-dictionary-site----interim-processes)
    + [Building and previewing the site locally](#building-and-previewing-the-site-locally)
- [EL Data Model](#el-data-model)
  * [Editing data models - interim process](#editing-data-models---interim-process)
    + [Editing attributes by module](#editing-attributes-by-module)
      - [Adding a new valid value to an existing manifest column](#adding-a-new-valid-value-to-an-existing-manifest-column)
      - [Adding a new column to a manifest template](#adding-a-new-column-to-a-manifest-template)
    + [Notes on collaboratively editing csvs](#notes-on-collaboratively-editing-csvs)
    + [Scraping Valid Values from Ontology](#scraping-valid-values-from-ontology)
  * [Automations](#automations)
    + [Updates to data model](#updates-to-data-model)
    + [Updating the data dictionary](#updating-the-data-dictionary)
    + [Adding a new template](#adding-a-new-template)
  * [Developing in a codespace](#developing-in-a-codespace)
    + [Create Data Model Visualization Tree](#create-data-model-visualization-tree)
  * [Developers](#developers)
    + [Files](#files)
    + [To setup environment](#to-setup-environment)
  * [Changes](#changes)

<!-- tocstop -->

# EL Metadata Dictionary Site

EL Metadata Dictionary is a [Jekyll](https://jekyllrb.com/) site utilizing [Just the Docs](https://just-the-docs.github.io/just-the-docs/) theme and is published on [GitHub Pages](https://pages.github.com/).

- `index.md` is the home page
- `_config.yml` can be used to tweak Jekyll settings, such as theme, title
- `_layout/` contains html templates we use to generate the web pages for each data model term
- `_data/` folder stores data for Jekyll to use when generating the site
- files in `docs/` will be accessed by GitHub Actions workflow to build the site
- two scripts in `processes/` can be run to generate updated files in `_data/` and `docs/` to publish changes in the data model to the dictionary site
- `.env` contains the link to the data model that the dictionary site is based on
- `Gemfile` is package dependencies for buildling the website
- `pyproject.toml` and `poetry.lock` list the python and package dependencies for the scripts that update both the data model and the data dictionary site
- You can add additional descriptions to home page or specific page by directly editing `index.md` or markdown files in `docs/`.

## Updating Metadata Dictionary Site -- interim processes

Interim process to update the metadata dictionary site after changes have been made to the data model:

:note: Note: do this in a SEPARATE PR after changes to the data model are merged to main. The scripts to do this reference the data model at the url in `processess/.env`, which is the main branch of this repo. It's not the most elegant right now but keeping the data model updates and the dictionary site updates as separate steps will make rolling back errors easier while we shore up this process.

1. Make a new branch. Run `poetry install` and then `poetry shell` on the command line to install dependencies and open a virtual environment.

2. From the main data-models directory, run `python proccesses/data_manager.py`. This should update some files within `_data/`

3. Then run `python processes/page_manager.py`. This should update files within `docs/`. 

4. Optional: you can run `python processes/create_network_graph.py` to create the schema visualization network graph. This is out of date and relatively unused, but it will be good to update and make more robust later.

5. Optional: Preview the website locally by running `bundle exec jekyll serve`.

6. Commit changes to your branch and open a PR. After review is passed and the changes are merged to main, a Github action will run via the `pages.yml` workflow to build and deploy the site to https://eliteportal.github.io/data-models/


### Building and previewing the site locally

1. Install Jekyll `gem install bundler jekyll`
2. Install Bundler `bundle install`
3. Run `bundle exec jekyll serve` to build your site and preview it at `http://localhost:4000`. The built site is stored in the directory `_site`.


# EL Data Model

**EL.data.model.\* ([csv](https://raw.githubusercontent.com/eliteportal/data-models/main/EL.data.model.csv) | [jsonld](https://raw.githubusercontent.com/eliteportal/data-models/main/EL.data.model.jsonld))**: this is the current, "live" version of the EL Portal data model. It is being used by both the staging and production versions of the multitenant Data Curator App.

## Editing data models - interim process

🚧 The Github action that automatically compiles the module csvs and converts to a json-ld is not working as expected as of June 2024. For now, please use the following procedure to manually compile attribute modules and convert the updated data model to a json-ld:

The main branch of this repo is protected, so you cannot push changes to main. To make changes to the data model:

1. Create a new branch in this repo and give it an informative name. 
2. On that branch, make and commit any changes. You can do this by cloning the repo locally or by [using a Github codespace](#developing-in-a-codespace). Please write informative commit messages in case we need to track down data model inconsistencies or introduced bugs.
3. Make sure you have the `poetry` dependency manager [installed](https://python-poetry.org/docs/#installing-with-the-official-installer) in your workspace.
4. Within the `data-models` repository, open a terminal and run `poetry install`. This will install the package versions listed in the `poetry.lock` file.
5. Once everything has installed, run `poetry shell` from the terminal. This will start a virtual environment running the correct version of all needed packages.
6. Still in the main directory, run `python data_model_creation/join_data_model.py` from the terminal. This will run a python script that joins all the module csvs, does a few data frame quality checks, and uses `schematic schema convert` to create the updated json-ld data model.
7. If the script succeeds, double check the version control history of your json-ld data model and make sure the changes you expected have been made! Save and commit all changes, then push your local branch to the remote.
8. [Optional]: to generate a test manifest, run `schematic manifest -c path/to/config.yml get -dt RelevantDataType -s` from the terminal. This will generate a json schema, a manifest csv, and a link to a google sheet version of the manifest. DO NOT put any real data in the google sheet manifest! This is just an integration test to see if the manifest columns and drop downs look as expected. Don't commit the json schema and the manifest csv generated during this step to your branch -- these are ephemeral and should be deleted. 
9. Open a pull request and request review from someone else on the EL DCC team. The Github Action that runs when you open a PR will currently fail -- you can ignore this. EL DCC team will perform manual checks before merging changes.
10. After the PR is merged, delete your branch.

### Editing attributes by module

The full `EL.data.model.csv` file has over 200 attributes and is unwieldy to edit and hard to review changes for. For ease of editing, the full data model is divided into "module" subfolders, like so:

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
2. Next, find the row for the attribute "organ" (should be the first row), and w/in the valid values column, add "eyeball" to the comma-separated list of valid values.
3. Save your changes and write an informative commit. Please try to add valid values alphabetically!

#### Adding a new column to a manifest template

1. If you wanted to add the column "furColor" to the "model-ad_individual_animal_metadata" template, first decide which module the new column should belong to. In this case, "MODEL-AD" makes the most sense.
2. W/in the `MODEL-AD` subfolder, create a new csv called `furColor.csv` with the required schematic column headers. Describe the attribute "furColor" as necessary and make sure `Parent` = `ManifestColumn`. Add any valid values for "furColor" as new rows to this csv as described in the previous scenario.
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

❓status unknown

Use `scraping_valid_values.py` to pull in values from EBI OLS sources. 

## Automations 

🚧 currently broken! Also the documentation here is from the AD data model, I don't think it's accurate for the EL repo.
 
When you open a PR that includes any changes to files in the `modules/` directory, a Github Action will automatically run before merging is allowed. This action:

### Updates to data model

1. Runs the `assemble_csv_data_model.py` script to concatenate the modular attribute csvs into one data frame, sort alphabetically by `Parent` and then `Attribute`, and write the combined dataframe to `EL.data.model.csv`. The action then commits the changes to the master data model csv.
2. Installs `schematic` from the develop branch and runs `schema convert` on the newly-concatenated data model csv to generate a new version of the jsonld file `EL.data.model.jsonld`. The action also commits the changes to the jsonld.

If this automated workflow fails, then the data model may be invalid and further investigation is needed.

### Updating the data dictionary

🚧 currently broken!

1. Runs `update-data-dictionary.yaml` in order to reflect information found in the dictionary for contributors


### Adding a new template

❓ status unknown

Recreates DCA template config

❓ status unkown

- Run the github action `create-template-config.yml` when adding new templates

## Developing in a codespace

:warning: If you are working in a Github Codespace, do NOT commit any Synapse credentials to the repository and do NOT use any real human data when testing data model function. This is not a secure environment!

If you want to make changes to the data model and test them out by generating manifests with `schematic`, you can use the devcontainer in this repo with a Github Codespace. This will open a container in a remote instance of VSCode and install the latest version of schematic.

Codespace secrets:

- SYNAPSE_PAT: scoped to view and download permissions on the sysbio-dcc-tasks-01 Synapse service account
- SERVICE_ACCOUNT_CREDS: these are creds for using the Google sheets api with schematic


### Create Data Model Visualization Tree

[Schematic API](https://schematic.api.sagebionetworks.org/v1/ui/)
[Visualization Repository](https://github.com/Sage-Bionetworks/schema_visualization)

- Creates a network graph of the data model. Aim is to help see connections between components.

## Developers

Software packages installed

- Poetry - [See installation guide here](https://python-poetry.org/docs/)

### Files

1. `EL.data.model.csv`: The CSV representation of the example data model. This file is created by the collective effort of data curators and annotators from a *community* (e.g. *ELITE*), and will be used to create a JSON-LD representation of the data model.

2. `EL.data.model.jsonld`: The JSON-LD representation of the example data model, which is automatically created from the CSV data model using the schematic CLI. More details on how to convert the CSV data model to the JSON-LD data model can be found [here](https://sage-schematic.readthedocs.io/en/develop/cli_reference.html#schematic-schema-convert). This is the central schema (data model) which will be used to power the generation of metadata manifest templates for various data types (e.g., `scRNA-seq Level 1`) from the schema.

3. `config.yml`: The schematic-compatible configuration file, which allows users to specify values for application-specific keys (e.g., path to Synapse configuration file) and project-specific keys (e.g., Synapse fileview for community project). A description of what the various keys in this file represent can be found in the [Fill in Configuration File(s)](https://sage-schematic.readthedocs.io/en/develop/README.html#fill-in-configuration-file-s) section of the schematic [docs](https://sage-schematic.readthedocs.io/en/develop/index.html).


### To setup environment

After cloning the repository, run the following command:
```poetry install```

## Changes

`./change-log.md`
