#!/usr/bin/env bash

# Workflow to update dictionary website content after changes to data model
# eventually needs to be a workflow
# run from 'data-models' parent directory

poetry install

poetry shell

python proccesses/data_manager.py

python processes/page_manager.py

python processes/create_network_graph.py

# Test jekyll site
bundle exec jekyll serve

# push changes
