#!/usr/bin/env python

""" 
Validate manifests

USAGE: python main.py -c config.yml -d EL.data.model.csv -m scripts/tests/test_manifests/ -t Proteomics -id syn58863921
"""

import argparse
import create_test_manifests
import validate_manifest


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Create test manifests",
        description="Generates test manifests filled in with the data model values",
        epilog="Text at the bottom of help",
        usage="%(prog)s [options]",
    )

    parser.add_argument("-c", "--config", help="path to the data model", type=str)

    parser.add_argument("-d", "--datamodel", help="path to the data model", type=str)

    # or create new manifest from model using schematic
    parser.add_argument(
        "-m", "--manifestPath", help="Directory to store the manifest", type=str
    )
    parser.add_argument(
        "-t", "--templateName", help="name of template in data model", type=str
    )

    parser.add_argument("-id", "--datasetid", help="Synapse ID", type=str)

    args = parser.parse_args()

    template_name = args.templateName
    manifest_dir = args.manifestPath
    data_model_path = args.datamodel
    config = args.config
    dataset_id = args.datasetid

    manifest_path = create_test_manifests.main(
        template_name, manifest_dir, data_model_path, dataset_id
    )

    validate_manifest.main(config, manifest_path, template_name, dataset_id)
