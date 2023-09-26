import os
from thefuzz import fuzz
import re
import yaml
import pathlib

recoder = {
    "metabolmics": "metabolomics",
    "(mass spec proteomics)": "Proteomics",
    "(mass spec metabolomics)": "Metabolomics Human",
    "(assay_otheruseTreatment? = Yes)": "assay_other, useTreatment? = Yes",
    "OtherUnknown": "Other, Unknown",
    "falseFalseFALSEtrueTrueTRUE": "TRUE, FALSE",
    re.compile("Forwardreverse", flags=re.IGNORECASE): "forward,reverse",
    re.compile("singleEndpairedEnd"): "singleEnd, pairedEnd",
    re.compile("(WGS)"): "Whole Genome Sequencing",
    re.compile("\?"): "",
    "Zeiss LSM 980Other": "Zeiss LSM 980",
    "bsSeqsampleType = other": "bsSeq, sampleType = other",
    re.compile(
        "HPO, MONDO, MAXO codes or labels (not listed for purposes of this RFC)"
    ): "HPO and MONDO and MAXO codes or labels (not listed for purposes of this RFC)",
}

keep_cols = [
    "Attribute",
    "Description",
    "Valid Values",
    "DependsOn",
    "Properties",
    "Required",
    "Parent",
    "DependsOn Component",
    "Source",
    "Validation Rules",
    "Module",
    "Type",
    "Ontology",
]

with open("./local_configs/notebook_config.yaml", "r") as f:
    config = yaml.safe_load(f)

csv_model = pathlib.Path("../" + config["file_names"]["csv_model"]).resolve()
json_model = pathlib.Path("../" + config["file_names"]["json_model"]).resolve()

# fuzzy matching
# Fuzzy matching to find misspellings
# Fuzzy matching


def fuzzy_matching(value_list: list):
    scores = {}
    for v in value_list:
        scores[v] = {}
        for v2 in value_list:
            if v == v2:
                next
            else:
                score = fuzz.ratio(v.lower(), v2.lower())
                if score == 100:
                    scores[v][v2] = score
        if len(scores[v]) == 0:
            scores.pop(v)

    return scores


def convert_dm_to_json(csv_model, json_model):
    os.system(f"schematic schema convert {csv_model} --output_jsonld {json_model}")
