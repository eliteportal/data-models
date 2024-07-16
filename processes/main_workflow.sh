#!/usr/bin/env bash

# Main workflow for this website. Also captured in github workflows.

cd "$(dirname "$0")"

source ../.venv/bin/activate

python data_manager.py

python page_manager.py

python create_network_graph.py

# Test jekyll site
# bundle exec jekyll serve

# push changes
