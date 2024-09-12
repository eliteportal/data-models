# ELITE Data Model and Metadata Dictionary

As of 2024-07-17 this repo contains both the production data model used by the ELITE portal to submit and validate metadata through the Data Curator App; _and_ the data dictionary website which is based on the data model and provides definitions for all metadata templates and terms used in the data model. 

There is a separate [data-dictionary](https://github.com/eliteportal/data-dictionary) repo which contains the same source code, and which can later be used to deploy the website when we are able to set up automation in that repository which successfully monitors this repository for changes. To simplify the process, for now we will use this data-models repo to manage both the data model and the dictionary.

<!-- toc -->

- [EL Data Model](#el-data-model)
  * [Editing the data model](#editing-the-data-model)
    + [Editing attributes by module](#editing-attributes-by-module)
      - [Adding a new valid value to an existing manifest column](#adding-a-new-valid-value-to-an-existing-manifest-column)
      - [Adding a new column to a manifest template](#adding-a-new-column-to-a-manifest-template)
    + [Notes on collaboratively editing csvs](#notes-on-collaboratively-editing-csvs)
    + [Adding a new template](#adding-a-new-template)
- [EL Metadata Dictionary Site](#el-metadata-dictionary-site)
  * [Updating Metadata Dictionary Site via Github Action](#updating-metadata-dictionary-site-via-github-action)
- [Other things you can do in this repository](#other-things-you-can-do-in-this-repository)
  * [Making changes WITHOUT Github Actions (locally or in a codespace):](#making-changes-without-github-actions-locally-or-in-a-codespace)
    + [editing data model in a github codespace](#editing-data-model-in-a-github-codespace)
    + [editing data model locally](#editing-data-model-locally)
    + [updating dictionary site in a github codespace](#updating-dictionary-site-in-a-github-codespace)
    + [updating dictionary site locally](#updating-dictionary-site-locally)
  * [Building and previewing the jekyll site locally](#building-and-previewing-the-jekyll-site-locally)
  * [Scraping Valid Values from Ontology](#scraping-valid-values-from-ontology)
  * [DCA config repo dispatch](#dca-config-repo-dispatch)
  * [Create Data Model Visualization Tree](#create-data-model-visualization-tree)
  * [Developers](#developers)
    + [Files](#files)
    + [To setup environment](#to-setup-environment)
  * [Changes](#changes)

<!-- tocstop -->

# EL Data Model

**EL.data.model.\* ([csv](https://raw.githubusercontent.com/eliteportal/data-models/main/EL.data.model.csv) | [jsonld](https://raw.githubusercontent.com/eliteportal/data-models/main/EL.data.model.jsonld))**: this is the current, "live" version of the EL Portal data model. It is being used by both the staging and production versions of the multitenant Data Curator App.

## Editing the data model

The main branch of this repo is protected, so you cannot push changes to main. To edit the data model, create a new branch of this repository and make changes to the attribute csv files in the `modules/` subdirectory. Once you have made your changes, open a pull request. This will trigger a Github Action that automatically joins the attributes from the module csv, converts the csv data model to the json-ld format, and commits the changes to your PR. Please **do not** make changes to `EL.data.model.csv` or `EL.data.model.jsonld` by hand! 

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

### Adding a new template

If you add a new template manifest (e.g. for a new assay type), remove an existing manifest, or rename a manifest, you need to update the `dca-template-config.yml` file that DCA uses to populate the menu contributors will use to select their template. To do this, you must **manually trigger** the Github Action `create-template-config.yml`. This will re-create the DCA template config file and open a new PR with the changes. Review and merge the PR to complete the template config update. You can use the default input values provided when you manually trigger this workflow.

# EL Metadata Dictionary Site

The Metadata Dictionary site is at: https://eliteportal.github.io/data-models/. 

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

## Updating Metadata Dictionary Site via Github Action

1. The dictionary site materials should be updated after you make changes to the data model ([see](#editing-the-data-model)). Once a PR with changes is reviewed and merged into main, the Github Action in `update_metadata_dictionary.yml` should automatically start. This action will update the files in `_data/` and `docs/` that are used to populate the dictionary website. 

2. Once any changes are detected in the `_data/` or `docs/` folders on the main branch, another Github action called `pages.yml` will run to update the deployment to the Github pages website. Verify that the dictionary site looks as expected at https://eliteportal.github.io/data-models/. 

# Other things you can do in this repository

## Making changes WITHOUT Github Actions (locally or in a codespace):

### editing data model in a github codespace

1. Start your codespace or build a new one. The codespace should build with a container image that includes the package manager `poetry`. You don't need to install poetry. It should also run the command `poetry install` after you launch it, which will tell poetry to install all the python libraries that are specified by this project (this will include schematic).
2. Make a new branch. On that branch, make and commit any changes. Please write informative commit messages in case we need to track down data model inconsistencies or introduced bugs.
3. Still in the top-level directory, run `poetry run python data_model_creation/join_data_model.py` from the terminal. This will run a python script that joins all the module csvs, does a few data frame quality checks, and uses `schematic schema convert` to create the updated json-ld data model.
4. If the script succeeds, double check the version control history of your json-ld data model and make sure the changes you expected have been made! Save and commit all changes, then push your local branch to the remote.
5. Open a pull request and request review from someone else on the EL DCC team. The Github Action that runs when you open a PR will currently fail -- you can ignore this. EL DCC team will perform manual checks before merging changes.
6. After the PR is merged, delete your branch.

### editing data model locally

1. Start your codespace or build a new one. The codespace should build with a container image that includes the package manager `poetry`. You don't need to install poetry. It should also run the command `poetry install` after you launch it, which will tell poetry to install all the python libraries that are specified by this project (this will include schematic).

Follow steps 2-4 [above](#editing-data-model-in-a-github-codespace)

5. [Optional]: to generate a test manifest, run `poetry run schematic manifest -c path/to/config.yml get -dt RelevantDataType -s` from the terminal. This will generate a json schema, a manifest csv, and a link to a google sheet version of the manifest. DO NOT put any real data in the google sheet manifest! This is just an integration test to see if the manifest columns and drop downs look as expected. Don't commit the json schema and the manifest csv generated during this step to your branch -- these are ephemeral and should be deleted. 
6. Open a pull request and request review from someone else on the EL DCC team. The Github Action that runs when you open a PR will currently fail -- you can ignore this. EL DCC team will perform manual checks before merging changes.
7. After the PR is merged, delete your branch.

### updating dictionary site in a github codespace

1. Start your codespace or build a new one. The codespace should build with a container image that includes the package manager `poetry`. You don't need to install poetry. It should also run the command `poetry install` after you launch it, which will tell poetry to install all the python libraries that are specified by this project (this will include schematic).

2. Make a new branch. 

3. From the top-level data-models directory, run `poetry run python processes/data_manager.py`. This should update some files within `_data/`

4. Then run `poetry run python processes/page_manager.py`. This should update files within `docs/`. 

5. Optional: you can run `poetry run python processes/create_network_graph.py` to create the schema visualization network graph. This is out of date and relatively unused, but it will be good to update and make more robust later.

6. Commit changes to your branch and open a PR. After review is passed and the changes are merged to main, a Github action will run via the `pages.yml` workflow to build and deploy the site to https://eliteportal.github.io/data-models/

### updating dictionary site locally

1. Make sure you have the `poetry` dependency manager [installed](https://python-poetry.org/docs/#installing-with-the-official-installer) in your workspace. 

Follow steps 2-5 from the section [above](#in-a-github-codespace)

6. Optional: Preview the website locally by running `bundle exec jekyll serve`.

7. Commit changes to your branch and open a PR. After review is passed and the changes are merged to main, a Github action will run via the `pages.yml` workflow to build and deploy the site to https://eliteportal.github.io/data-models/

## Building and previewing the jekyll site locally

1. Install Jekyll `gem install bundler jekyll`
2. Install Bundler `bundle install`
3. Run `bundle exec jekyll serve` to build your site and preview it at `http://localhost:4000`. The built site is stored in the directory `_site`.

## Scraping Valid Values from Ontology

❓status unknown

Use `scraping_valid_values.py` to pull in values from EBI OLS sources. 

## DCA config repo dispatch

❓status unknown

`dcc_config_repo_dispatch.yml` -- Not sure what this is for, still investigating its use. Authorization is failing.

## Create Data Model Visualization Tree

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
