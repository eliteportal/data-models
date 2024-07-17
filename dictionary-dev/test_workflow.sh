#! /bin/sh

# should be run in main directory

echo pwd

# Get new data model from repo
python ./dev/get_data_model.py

# update new csvs and and terms
python ./term_file_manager.py

# Test jekyll site
# bundle exec jekyll serve

# push changes
