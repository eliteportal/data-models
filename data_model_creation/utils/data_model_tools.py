"""
Tools for creating the data model

"""

import subprocess
from thefuzz import fuzz
import re
import json
from pathlib import Path
import pandas as pd


def get_templates(root_dir, jsonld_name):
    # Get manifest names to generate manifests
    json_model_path = Path(root_dir, jsonld_name)

    # ================ FIND TEMPLATES IN DATA MODEL ================ #
    with open(json_model_path, "r", encoding="UTF-8") as f:
        dm_json = json.load(f)

    # get template names
    for i in dm_json["@graph"]:
        try:
            if bool(re.search("template", i["@id"])):
                # print(i)
                templates = [
                    v for n in i["schema:domainIncludes"] for _, v in n.items()
                ]
        except KeyError:
            pass
    # Manifest template names in data model
    manifest_schemas = []

    for i in dm_json["@graph"]:
        try:
            if i["@id"] in templates:
                if bool(
                    re.search("individual|biospecimen",
                              i["@id"], flags=re.IGNORECASE)
                ):
                    record_type = "record"
                else:
                    record_type = "file"

                temp_template = {
                    "display_name": i["sms:displayName"],
                    "schema_name": i["@id"].strip("bts:"),
                    "type": record_type,
                }

                manifest_schemas.append(temp_template)
        except KeyError:
            pass

    # see results
    manifest_schemas_df = (
        pd.DataFrame(manifest_schemas)
        .sort_values(["type", "display_name"], ascending=True)
        .reset_index(drop=True)
    )

    return manifest_schemas, manifest_schemas_df


def fuzzy_matching(value_list: list):
    # Fuzzy matching to find misspellings
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


def convert_dm_to_json(csv_model_path, json_model_path, ROOT_DIR):
    proc = subprocess.Popen(
        f"schematic schema convert {csv_model_path} --output_jsonld {json_model_path}",
        shell=True,
        cwd=ROOT_DIR,
    )

    print(proc.communicate())


def clean_list(string):
    """Takes a list represented as a string and returns only unique values found

    Args:
        string (str): list represented as string

    Returns:
        list: list of unique values
    """

    new_list = string.split(",")
    new_list = [n.strip() for n in new_list]
    new_list = list(np.unique(new_list))
    return new_list


def check_special_chars(dm):
    pattern = "\(|\)|\?|/|-"
    results = dm[["Attribute", "Valid Values"]].apply(
        lambda x: sum(x.str.contains(pattern))
    )
    print(results)


# used to fix values in data model
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
# FASLSE
# hard coded dictionary
recoder_valid_values = {
    re.compile("Not Specified", flags=re.IGNORECASE): "Not Specified",
    re.compile("(Other$)", flags=re.IGNORECASE): "Other",
    re.compile("lipid", re.IGNORECASE): "Lipid",
    re.compile("plasma", re.IGNORECASE): "Plasma",
    re.compile("protein", re.IGNORECASE): "Protein",
    re.compile("saliva", re.IGNORECASE): "Saliva",
    re.compile("serum", re.IGNORECASE): "Serum",
    re.compile("sputum", re.IGNORECASE): "Sputum",
    re.compile("urine", re.IGNORECASE): "Urine",
    re.compile(
        "(^0x Visium Spatial Gene Expression)"
    ): "10x Visium Spatial Gene Expression",
    re.compile("falseFalseFALSEtrueTrueTRUE	"): "TRUE, FALSE",
    re.compile("TRUE|TRUEDiagnosisStatus", re.IGNORECASE): "TRUE",
    re.compile("TRUEDiagnosisStatus", re.IGNORECASE): "TRUE",
    re.compile("FALSE", re.IGNORECASE): "FALSE",
    re.compile("$f^", re.IGNORECASE): "F",
    re.compile("UnknownNot collected"): "Unknown, Not collected",
    re.compile(r"\u200b\u200b"): "",
    re.compile(
        "The Health,Aging,and Body Composition Study \(HealthABC\)"
    ): "The Health and Aging and Body Composition Study (HealthABC)",
    re.compile("Not Hispanic or latinoEthnicity"): "Not Hispanic or latino",
    re.compile("Hispanic or latinoEthnicity"): "Hispanic or latino",
    re.compile(
        "HPO, MONDO, MAXO codes or labels \(not listed for purposes of this RFC\)"
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
