# # Setup

# - Fix inconsistencies in parent column

import pandas as pd
import numpy as np
import os

from glob import glob
import yaml
import re
import copy
import json
from thefuzz import fuzz

# Custom package
from utils import utils, synapse_login

with open("./local_configs/notebook_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# paths to import files
schematic_config = config["paths"]["schematic"]
csv_model = config["file_names"]["csv_model"]
json_model = config["file_names"]["json_model"]

print(
    "Schematic config: ",
    schematic_config,
    "\n",
    "CSV model: ",
    csv_model,
    "\n",
    "JSON LD Model: ",
    json_model,
)

# ## Hard Coded stuff

validation_coder = {
    "number": "regex search ([0-9]+\.[0-9]*.?)|([0-9]+)",
    "integer": "regex search ([0-9]+)",
    "string": "",
}

base_cols = [
    "Attribute",
    "Description",
    "Valid Values",
    "DependsOn",
    "Properties",
    "Required",
    "Template",
    "Parent",
    "DependsOn Component",
    "Source",
    "Validation Rules",
]

keep_cols = [
    "Attribute",
    "Description",
    "Valid Values",
    "Required",
    "DependsOn",
    "DependsOn Component",
    "Properties",
    "Validation Rules",
    "Template",
    "Parent",
    "Source",
    "Type",
    "Ontology",
    "multivalue",
]

list_cols = [
    "UsedIn",
    "DependsOn",
    "Properties",
    "Validation Rules",
    "Template",
    "Parent",
    "Source",
    "Type",
    "Ontology",
    "Required",
    "multivalue",
]

template_hard_coded_attrs = {
    "Attribute": "",
    "Description": "",
    "Valid Values": "",
    "Required": "False",
    "Validation Rules": "",
    "Template": "",
    "Parent": "",
    "Source": "",
    "Type": "",
    "Ontology": "",
    "UsedIn": "",
}

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
        "^0x Visium Spatial Gene Expression"
    ): "10x Visium Spatial Gene Expression",
    re.compile("falseFalseFALSEtrueTrueTRUE	"): "True, False",
    re.compile("TRUE|TRUEDiagnosisStatus", re.IGNORECASE): "True",
    re.compile("FALSE|FASLSE", re.IGNORECASE): "False",
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
    re.escape(
        r"Possible values are listed under the instrument model term.OtherMsInstrumentModel"
    ): "OtherMsInstrumentModel",
    re.compile(
        r"Possible values are listed under the cleavage agent nameOtherCleavageAgents"
    ): "OtherCleavageAgents",
    re.compile(r"Possible values are listed under modification parameters"): "",
    re.compile("Uknown"): "Unknown",
    re.compile("OtherControlType", re.IGNORECASE): "OtherControlType",
    re.compile("OtherMsAnalyteType", re.IGNORECASE): "OtherMsAnalyteType",
}

# # Functions

# Clean list columns into single string
def join_strings(string):
    try:
        return ",".join(string)
    except:
        return ""


def clean_list(string):
    """Takes a list represented as a string and returns only unique values found

    Args:
        string (str): list represented as string

    Returns:
        string: list as string of unique values
    """

    new_list = string.split(",")
    new_list = [n.strip() for n in new_list if n != "nan"]
    new_list = ",".join(sorted(list(np.unique(new_list)))).strip(",")
    return new_list


def search_df(df, pattern):
    mask = np.column_stack(
        [df[col].str.contains(pattern, na=False, flags=re.IGNORECASE) for col in df]
    )

    df = df.loc[mask.any(axis=1)]

    with pd.option_context("display.max_colwidth", None):
        display(df)

    return df


def find_row(df, attribute):
    """Get indexes of the dataframe"""
    indexes = df.index[
        df["Attribute"].str.contains(
            "(^" + re.escape(attribute) + "$)", flags=re.IGNORECASE
        )
    ].tolist()
    if len(indexes) != 0:
        return indexes
    else:
        print(attribute)
        return None


def replace_valid_value(df, indexes, regex_dict, attribute):
    """Alter the dataframe valid values with the replacement value"""
    if indexes == None:
        return df

    elif len(indexes) > 0:
        regex_dict = regex_dict[attribute]

        for index in indexes:
            df.loc[index, "Valid Values"] = re.sub(
                **regex_dict, string=df.loc[index, "Valid Values"]
            )

            # print(df.loc[index, 'Valid Values'])
        return df
    else:
        return df


def code_equals_values(df, regex_dict, attribute):
    print("attribute: ", attribute)

    indexes = find_row(df, attribute)

    print("Index: ", indexes)

    if indexes == None:
        return df
    else:
        df = replace_valid_value(df, indexes, regex_dict, attribute)
        return df


def rewrite_df_value(df, col_name, search_term, col_value, new_value):
    try:
        df.loc[df[df[col_name] == search_term].index[0], col_value] = new_value
        return df
    except:
        return df

# Unzip compressed folder if downloaded from Google Drive
# %unzip 'RFC Tables-20230620T181152Z-001.zip'

# # Collect RFCs

# Get all the RFC file paths
file_paths = glob("../_data/RFC Tables/*")

# Create Data Model for Schematic

dm = pd.DataFrame()

# parse through files to create complete data model
for fp in file_paths:
    file_name = os.path.basename(fp)

    temp = pd.read_excel(fp)

    # Create file_name column to check
    temp.insert(loc=0, column="file_name", value=file_name)

    # Create new columnn for data model name
    temp.insert(
        loc=1,
        column="dm",
        value=re.sub(
            "\s\s+",
            " ",
            re.sub(
                "_",
                " ",
                re.sub(
                    "(EL)|(RFC)|(\.xlsx)|([Aa]ssay)|([Dd]ata [Mm]odel)", "", file_name
                ),
            ).strip(),
        ),
    )

    dm = pd.concat([dm, temp])

# initial cleaning
dm[["required", "multivalue"]] = (
    dm[["required", "multivalue"]]
    .fillna(False)
    .astype(str)
    .replace({"1.0": True, "0.0": False})
)

dm.fillna("")
dm.reset_index(drop=True, inplace=True)
dm.head()

# Data model clean up

# collapse presumed ontology columns and join with existing
dm.loc[:, "ontology"] = dm.iloc[:, 11:].bfill(axis=1).iloc[:, 0]

dm["ontology"] = (
    dm[["concept source ontology", "ontology"]]
    .fillna("")
    .apply(lambda x: ",".join([y.strip() for y in x.unique() if len(y) > 0]), axis=1)
)

# if unique values are provided by data contributor then add this note in the ontology

dm["ontology"] = (
    dm.loc[
        dm["valid values"].str.contains(
            "(n/a \(unique to each data contributor\))", na=False
        ),
        "ontology",
    ]
    + ","
    + "Data Contributor"
)

# new ontologies:
ontology_list = []
for i, v in dm[["concept source ontology", "ontology"]].fillna("").iterrows():
    ontology_list.append(",".join(v))

dm["ontology"] = ontology_list
dm["ontology"] = dm["ontology"].str.strip(",")

dm = dm.apply(
    lambda x: x.str.replace(
        pat="\n|(n/a \(unique to each data contributor\))", repl="", regex=True
    ).str.split(","),
    axis=1,
)

dm.head()

# revert lists back to strings
dm = dm.applymap(lambda x: join_strings(x))

# Rename columns with DCA standards
dm_schema_cols = {
    "dm": "Template",
    "key": "Attribute",
    "description": "Description",
    "valid values": "Valid Values",
    "required": "Required",
    "requires": "DependsOn Component",
    "concept source ontology": "Source",
    "ontology": "Ontology",
    "type": "Type",
}

dm = dm.rename(dm_schema_cols, axis=1)

# drop unimportant columns
r = re.compile("Unnamed*", re.IGNORECASE)

# Add additional required columns for DCA
dm["Properties"] = ""
dm["Validation Rules"] = dm["Type"].map(validation_coder)
dm["DependsOn"] = ""
dm["Parent"] = ""
# dm['DependsOn Component'] = ""

dm = dm[keep_cols]

dm.head()

# Add templates as attributes to generate templates in DCA
# Create Manifests in data model
unique_templates = np.unique(
    ",".join(dm["Template"].dropna().values.tolist()).split(",")
)
templates = pd.DataFrame({"Attribute": unique_templates})
templates["Required"] = "True"
templates["Properties"] = "dataType"
templates["Parent"] = "Template"
templates["Description"] = templates["Attribute"].apply(
    lambda x: f"Metadata template for {x}"
)

# Adjust bseq
templates.loc[
    templates["Attribute"] == "bsSeq (bisulfite-seq WGBS methylseq methylomics)",
    "Description",
] = "Metadata template for bisulfite-seq WGBS methylseq methylomics"
templates.loc[
    templates["Attribute"] == "bsSeq (bisulfite-seq WGBS methylseq methylomics)",
    "Attribute",
] = "bsSeq"

# update templates column for other attributes
dm["Template"] = dm["Template"].str.replace(
    "bsSeq (bisulfite-seq WGBS methylseq methylomics)", "bsSeq", regex=False
)

# create depends On column for templates
for i, m in enumerate(templates["Attribute"]):
    dm["Template"].str.contains(m)
    templates.loc[i, "DependsOn"] = ",".join(
        dm.loc[
            dm["Template"].str.contains(m, regex=False, na=False), "Attribute"
        ].tolist()
    )

# fixing "not listed" columns
dm["Valid Values"] = dm["Valid Values"].str.replace(
    "Genbank common names (not listed for purposes of this RFC)Unknown",
    "Genbank common names (not listed for purposes of this RFC),Unknown",
    regex=False,
)

dm.loc[dm["Valid Values"].str.contains("not listed"), "Valid Values"] = (
    dm.loc[dm["Valid Values"].str.contains("not listed"), "Valid Values"]
    .str.split(")")
    .apply(
        lambda x: ",".join(
            [y.strip(",") for y in x if not bool(re.search("not listed", y))]
        )
    )
)

# QC
dm.loc[dm["Valid Values"].str.contains("not listed", na=False), "Valid Values"]

# Dropping measurement technique
dm = dm.drop(
    index=dm.query('Attribute == "measurementTechnique"').index.values
).reset_index(drop=True)

# combine duplicated attributes
dm = dm.groupby("Attribute").agg(lambda x: ",".join(set(x.astype(str)))).reset_index()

# found extra commas in strings at beginning and end
dm = dm.applymap(lambda x: x.strip(","))

template_recoder = {
    re.compile("genotyping", re.IGNORECASE): "Genotyping",
    re.compile("proteomics", re.IGNORECASE): "Proteomics",
}

dm = dm.replace(template_recoder, regex=True)

display(dm.dtypes)
display(dm.head())
display(dm.Template.unique())

# Reorder Columns based on DCA Standards
dm = dm.loc[:, keep_cols]

# # Clean up
# ## DependsOn Component
# 

recoder = {
    "metabolmics": "metabolomics",
    "(mass spec proteomics)": "Proteomics",
    "(mass spec metabolomics)": "Metabolomics Human",
    "(assay_otheruseTreatment? = Yes)": "assay_other, useTreatment? = Yes",
    "OtherUnknown": "Other, Unknown",
    "falseFalseFALSEtrueTrueTRUE": "TRUE, FALSE",
    "Hispanic or latinoEthnicity": "Hispanic or Latino",
    re.compile("Forwardreverse", flags=re.IGNORECASE): "forward,reverse",
    re.compile("singleEndpairedEnd"): "singleEnd, pairedEnd",
    re.compile("(WGS)"): "Whole Genome Sequencing",
    re.compile("\?"): "",
    "Zeiss LSM 980Other": "Zeiss LSM 980,Other",
    "bsSeqsampleType = other": "bsSeq, sampleType = other",
    re.compile(
        "HPO, MONDO, MAXO codes or labels \(not listed for purposes of this RFC\)"
    ): "HPO and MONDO and MAXO codes or labels (not listed for purposes of this RFC)",
    "The Health, Aging, and Body Composition Study \(HealthABC\)": "The Health and Aging and Body Composition Study (HealthABC)",
}

# 'mass spec metabolomics,measurementTechnique = other'
# falseFalseFALSEtrueTrueTRUE

dm = dm.replace(recoder, regex=True)

with pd.option_context("display.max_colwidth", None):
    display(dm[dm["Valid Values"].str.contains("and Body Composition Study")])

with pd.option_context("display.max_colwidth", None):
    display(dm.query('Attribute == "ethnicity"'))

# QA check
dm[dm["DependsOn Component"].str.contains(
    "metabolomics", case=False, na=False)]

# ## Cleaning other values and equal values
# Removing illegal characters
# 

# Remove any special characters

dm["Attribute"] = dm["Attribute"].str.replace("\(|\)|\?", "", regex=True)

dm["Valid Values"] = (
    dm["Valid Values"]
    .apply(
        lambda x: re.sub(
            "^0x Visium Spatial Gene Expression",
            "10x Visium Spatial Gene Expression",
            x,
        )
    )
    .apply(clean_list)
)

# Clean up equals in depends on

def create_new_value(old_value):
    new_vals = old_value.split("=")
    new_vals = [nv.strip() for nv in new_vals]
    # convert to camel case
    nv = new_vals[1].capitalize() + new_vals[0][0].upper() + new_vals[0][1:]
    return nv

def recode_yes_no(v):
    if v.lower() == "yes":
        return "TRUE"
    elif v.lower() == "no":
        return "FALSE"
    else:
        return v


dm["Valid Values"] = (
    dm["Valid Values"]
    .apply(lambda x: x.split(","))
    .apply(lambda x: ",".join([recode_yes_no(y) for y in x]))
)

# Split list to process other values
# Find the other columns in the data model
others = dm[dm["DependsOn Component"].str.contains("=", na=False)].copy()

others["DependsOn Component Original"] = others["DependsOn Component"].str.split(",")

# Create series of equals values to use for new attributes/ valid values relationship
others["equals_series"] = others["DependsOn Component Original"].apply(
    lambda x: [y for y in x if bool(re.search("=", y))][0]
)

# others["equals_attribute"] = others["equals_series"].apply(create_new_value)

others[["baseAttribute", "equalsValue"]] = (
    others["equals_series"]
    .str.split("=", expand=True)
    .apply(lambda x: [y.strip() for y in x])
    .rename({0: "base_attribute", 1: "equalsValue"}, axis=1)
)

# Deciding to use true and false for all yes/no values
recoder = {
    re.compile("^[Yy]es", flags=re.IGNORECASE): "TRUE",
    re.compile("true", flags=re.IGNORECASE): "TRUE",
    re.compile("^[Nn]o", flags=re.IGNORECASE): "FALSE",
}

others["equalsValue"] = others["equalsValue"].replace(recoder, regex=True)

others["newDescription"] = others[["baseAttribute", "equalsValue"]].apply(
    lambda x: f"When {x[0].strip()} = {x[1].strip()}", axis=1
)

others["equalsAttribute"] = others[["baseAttribute", "equalsValue"]].apply(
    lambda x: f"{x[1].strip()}{x[0].strip()[0].upper()+x[0].strip()[1:]}", axis=1
)
others["DependsOn Component"] = ""
others["Properties"] = "dataProperty"
others.loc[others["equalsValue"] == "other", "Parent"] = "Specification"

equals_df = others.copy()
equals_df = equals_df.drop(columns=["DependsOn", "Description"])

equals_df = equals_df.rename(
    {
        "Attribute": "DependsOn",
        "newDescription": "Description",
        "equalsAttribute": "Attribute",
    },
    axis=1,
)[base_cols]

equals_df["DependsOn Component"] = ""

equals_df["Valid Values"] = ""

equals_df["Properties"] = "ValidValue"

# Update base attribute equals values

# Create mapping
temp = others["equals_series"].str.split("=", expand=True)
temp = temp.apply(lambda x: x.str.strip(), axis=1)
temp = temp.rename({0: "base_attribute", 1: "value_to_replace"}, axis=1)
temp["value_to_replace"] = temp["value_to_replace"].str.capitalize()

# new value
temp["new_value"] = others["equalsAttribute"]
temp.reset_index(drop=True, inplace=True)

temp = temp.drop_duplicates()

replacements = {}

for i, x in temp.iterrows():
    ba, vtr, nv = x
    replacements[ba] = {
        "pattern": re.compile("(" + vtr + ")", flags=re.IGNORECASE),
        "repl": nv,
    }

replacements

for attribute in replacements.keys():
    dm = code_equals_values(dm, replacements, attribute)
    print("-" * 20)

# ## Add derived attributes from "=" valid values

# dm["Properties"] = "dataProperty"
dm.update(others[base_cols])
dm = pd.concat([dm, equals_df], ignore_index=True)

# Do not need
dm["DependsOn Component"] = ""

# # Valid Values Work

# # Not sure what happened here in the RFCs
dm["Valid Values"] = dm["Valid Values"].replace(recoder_valid_values)

# valid values that contain other
pattern = "([Oo]ther)"

pure_others = dm[
    dm["Valid Values"].str.contains(pattern, flags=re.IGNORECASE, regex=True)
].copy()

pure_others.loc[:, "replacement_value"] = pure_others.loc[:, "Attribute"].apply(
    lambda x: "Other" + (x[0].upper() + x[1:])
)

regex_dict = {}

for i, r in pure_others.iterrows():
    regex_dict[r["Attribute"]] = {
        "pattern": re.compile(pattern, flags=re.IGNORECASE),
        "repl": r["replacement_value"],
    }

# json_formatted = json.dumps(regex_dict, indent=4)
# print(json_formatted)

for attribute in regex_dict.keys():
    dm = code_equals_values(dm, regex_dict, attribute)
    print("-" * 20)

# ## Cleanup valid values

# Fuzzy matching to find misspellings
# Fuzzy matching

valid_values = ",".join(dm["Valid Values"])
valid_values = valid_values.split(",")
valid_values = list(np.unique(valid_values))
valid_values = [v.strip() for v in valid_values if len(v) > 0]


scores = {}
for v in valid_values:
    scores[v] = {}
    for v2 in valid_values:
        if v == v2:
            next
        else:
            score = fuzz.ratio(v.lower(), v2.lower())
            if score == 100:
                scores[v][v2] = score
    if len(scores[v]) == 0:
        scores.pop(v)

# create recoding variables off fuzzy matching
new_values_recoded = []

for v in scores.values():
    new_values_recoded.append(list(v.keys())[0].title())

new_values_recoded = np.unique(new_values_recoded)

# recoder_valid_values = {}
for nv in new_values_recoded:
    recoder_valid_values[re.compile(nv, flags=re.IGNORECASE)] = nv
    # recoder_valid_values.append(value_add)

dm[["Valid Values", "multivalue"]] = (
    dm[["Valid Values", "multivalue"]]
    .replace(recoder_valid_values, regex=True)
    .fillna("")
    .applymap(lambda x: clean_list(x))
)

dm["Valid Values"] = (
    dm["Valid Values"].apply(lambda x: clean_list(x)
                             ).apply(lambda x: x.split(","))
)

# Expand each valid value into its own row
dm_vv = dm.explode("Valid Values")

# join valid values back together in data model as string
dm["Valid Values"] = dm["Valid Values"].apply(lambda x: ",".join(x).strip(","))

# Group valid values to create unique attribute and trace where value is used in another attribute and template
dm_vv = (
    dm_vv.dropna(subset="Valid Values")
    .groupby("Valid Values")
    .agg(lambda x: ",".join(set(x.astype(str))).strip(","))
    .reset_index()
)

dm_vv["Properties"] = "ValidValue"
dm_vv["Required"] = "False"

# rename for concatenating with data model
dm_vv = dm_vv.rename({"Valid Values": "Attribute",
                     "Attribute": "UsedIn"}, axis=1)

dm_vv[list_cols] = dm_vv[list_cols].applymap(clean_list)

dm_vv = dm_vv[dm_vv["Attribute"] != ""].reset_index(drop=True)

# clean up type
dm_vv["Type"] = "STRING"

# cleanup multivalue
dm_vv["multivalue"] = "False"

dm_vv.head()

dm_vv.shape

# dm["Valid Values"] = (
#     dm["Valid Values"]
#     .replace(recoder_valid_values, regex=True)
#     .apply(lambda x: clean_list(x))
# )

# valid_values = list(np.unique(",".join(dm["Valid Values"]).split(",")))

# valid_values = [v.strip() for v in valid_values if len(v) > 0]

# valid_values_df = pd.DataFrame({"Attribute": pd.Series(valid_values)})

# valid_values_df["Properties"] = "validValue"
# valid_values_df["Required"] = "False"

# valid_values_df = valid_values_df[
#     ~valid_values_df["Attribute"].isin(dm["Attribute"].tolist())
# ]

# valid_values_df

# adding valid values found in attribute columns
print(dm.shape)

dm2 = pd.concat([dm, dm_vv], axis=0, ignore_index=True)

display(dm2.shape)

print(sum(dm2.duplicated(subset="Attribute", keep=False)))

# dm2.loc[dm2.duplicated(subset="Attribute", keep=False),].sort_values(by="Attribute")

# Create measurement unit attributes
# Separate out measurement units
r = re.compile("(^Other)")

measurement_units = np.unique(
    ",".join(
        dm.loc[
            dm["Valid Values"].str.contains("units", regex=True), "Valid Values"
        ].values.tolist()
    ).split(",")
)

measurement_units = [
    x
    for x in measurement_units
    if x not in ["Not Specified", "Other", "Unknown", "Not Available"]
    and not bool(r.search(x))
]

dm2.loc[dm2["Attribute"].isin(measurement_units), "Parent"] = "MeasurementUnit"
dm2.loc[dm2["Attribute"].isin(measurement_units), "Description"] = "Measurement unit"
dm2.loc[dm2["Attribute"].isin(measurement_units), "Type"] = "STRING"
dm2.loc[dm2["Attribute"].isin(measurement_units), "multivalue"] = False

# Nonsense attributes
dm2 = dm2.drop(
    index=dm2.loc[dm2["Attribute"].str.contains(
        "Possible values"),].index.tolist()
)

# Fuzzy matching to find misspellings
# Fuzzy matching

valid_values = dm2["Attribute"].replace(
    recoder_valid_values, regex=True).tolist()

scores = {}
for v in valid_values:
    scores[v] = {}
    for v2 in valid_values:
        if v == v2:
            next
        else:
            score = fuzz.ratio(v.lower(), v2.lower())
            if score == 100:
                scores[v][v2] = score
    if len(scores[v]) == 0:
        scores.pop(v)

scores

dm2["Attribute"] = dm2["Attribute"].replace(recoder_valid_values, regex=True)

dm2[["Valid Values", "multivalue"]] = (
    dm2[["Valid Values", "multivalue"]]
    .fillna("")
    .astype(str)
    .replace(recoder_valid_values, regex=True)
    .applymap(lambda x: clean_list(x))
)

dm2 = (
    dm2.dropna(subset="Attribute")
    .groupby("Attribute")
    .agg(lambda x: ",".join(set(x.astype(str))).strip(","))
    .reset_index()
)

dm2 = dm2.drop(index=dm2[dm2["Attribute"] == "f"].index.tolist()).reset_index(drop=True)

dm2[list_cols] = dm2[list_cols].applymap(clean_list)

print(f"dm2 shape: {dm2.shape}")
print(f'Duplicates: {sum(dm2.duplicated(subset="Attribute", keep=False))}')

# # Check columns for Speical Characters

check_cols = ["Attribute"]

mask = np.column_stack(
    [dm2[col].str.contains("\(|\)", na=False) for col in dm2[check_cols]]
)

with pd.option_context("display.max_colwidth", None):
    display(dm2[check_cols].loc[mask.any(axis=1)])

dm2 = pd.concat([dm2, templates], axis=0, ignore_index=True)

print(dm2.shape)

dm2[["Valid Values", "Template", "Ontology", "Source"]] = (
    dm2[["Valid Values", "Template", "Ontology", "Source"]]
    .fillna("")
    .applymap(clean_list)
)

# Recode required columns and fix spelling mistakes
required_recoder = {"0.0": "False", "1.0": "True", "FASLSE": "False"}

dm2["Required"] = dm2["Required"].replace(required_recoder)

# Last bit of cleanup

# Remove measurement technique dependency from biospecimen human
dm2.loc[dm2["Attribute"] == "Biospecimen human", "DependsOn"] = (
    dm2.loc[dm2["Attribute"] == "Biospecimen human", "DependsOn"]
    .values[0]
    .replace("measurementTechnique,", "")
)
bio_measure_technique_index = dm2.query(
    'Attribute == "measurementTechnique" and Parent == "Biospecimen human"'
)

if len(bio_measure_technique_index.index) > 0:
    dm2 = dm2.drop(
        index=bio_measure_technique_index.index[0]).reset_index(drop=True)

# Remove measurement technique dependency from biospecimen human
dm2.loc[dm2["Attribute"] == "Biospecimen human", "DependsOn"] = (
    dm2.loc[dm2["Attribute"] == "Biospecimen human", "DependsOn"]
    .values[0]
    .replace("specifyMeasurementTechnique,", "")
)
bio_measure_technique_index = dm2.query(
    'Attribute == "specifyMeasurementTechnique" and Parent == "Biospecimen human"'
)


if len(bio_measure_technique_index.index) > 0:
    dm2 = dm2.drop(
        index=bio_measure_technique_index.index[0]).reset_index(drop=True)

# Remove measurement technique dependency from biospecimen human
dm2.loc[dm2["Attribute"] == "Biospecimen human", "DependsOn"] = (
    dm2.loc[dm2["Attribute"] == "Biospecimen human", "DependsOn"]
    .values[0]
    .replace("OtherMeasurementTechnique,", "")
)
bio_measure_technique_index = dm2.query(
    'Attribute == "OtherMeasurementTechnique"')


if len(bio_measure_technique_index.index) > 0:
    dm2 = dm2.drop(
        index=bio_measure_technique_index.index[0]).reset_index(drop=True)

dm2.loc[dm2[dm2["Attribute"] == "visitCode"].index.values[0], "Valid Values"] = ""

dm2.loc[dm2[dm2["Attribute"] == "visitCode"].index.values[0],
        "Validation Rules"] = ""

# Extra comma at beginning of valid values

# # Validation Rules

mixed_attrs = [
    {"attribute": "tissueWeight", "val_type": "mixed float", "regex": "regex search"},
    {"attribute": "tissueVolume", "val_type": "mixed float", "regex": "regex search"},
    {"attribute": "specimenAge", "val_type": "mixed integer", "regex": "regex search"},
    {"attribute": "samplingAge", "val_type": "mixed integer", "regex": "regex search"},
    {"attribute": "age", "val_type": "mixed integer", "regex": "regex search"},
]

for ma in mixed_attrs:
    attribute = ma["attribute"]
    val_type = ma["val_type"]

    # get indexes for new validation rules based on attribute
    indexes = dm2[dm2["Attribute"] == attribute].index.tolist()

    for i in indexes:
        if val_type == "integer":
            first_part = "[0-9]+"
        elif val_type == "float":
            first_part = "^\d*?\.?\d$"
        elif val_type == "mixed integer":
            regex = "regex search"
            num_match = "^\d*?"
        elif val_type == "mixed float":
            regex = "regex search"
            num_match = "^\d*?\.?\d$"
            # All valid values are applicable
            new_string = (
                regex
                + num_match
                + "|"
                + ""
                + "|".join(dm2.loc[i, "Valid Values"].split(","))
            )

        dm2.loc[i, "Validation Rules"] = new_string

dm2["Validation Rules"].unique().tolist()

# ## Building Dependencies

dependencies = {
    "specimenID": "matchAtLeastOne Biospecimenhuman.specimenID value",
    "individualID": "matchExactlyOne IndividualHuman.individualID set",
}

for k, v in dependencies.items():
    indexes = dm2[dm2["Attribute"] == k]["Validation Rules"].index.values
    dm2.loc[indexes, "Validation Rules"] = v

dm2.loc[3, "Valid Values"] = dm2.loc[3, "Valid Values"].replace(
    ",Whole Genome Sequencing", ""
)

# # More Adjustments

with pd.option_context("display.max_colwidth", None):
    display(dm2.query('Attribute == "visitCode"'))

hard_coded_valid_values = [
    {
        "attribute": "visitCode",
        "valid_value": "1,2,3,4,Other,Unknown,Not collected,Not applicable",
    },
    {"attribute": "tissueWeight", "valid_value": ""},
    {"attribute": "consentGroupID", "valid_value": "1,2,3"},
    {"attribute": "samplingAge", "valid_value": ""},
    {"attribute": "specimenAge", "valid_value": ""},
    {"attribute": "age", "valid_value": ""},
]

for h in hard_coded_valid_values:
    dm2.loc[
        dm2[dm2["Attribute"] == h["attribute"]].index.values[0], "Valid Values"
    ] = h["valid_value"]

# # Only needed for the first time since the Valid values were TBD
dm2 = rewrite_df_value(dm2, "Attribute", "assay", "Valid Values", np.nan)
dm2 = dm2.replace("", np.nan)
# Add valid values from the AD model
dm2["Valid Values"] = dm2["Valid Values"].fillna(
    dm2["Attribute"].map(df_new_attrs.set_index("Attribute")["Valid Values"])
)

checks = [c["attribute"] for c in hard_coded_valid_values]

with pd.option_context("display.max_colwidth", None):
    display(dm2.query(f"Attribute in @checks"))

print(dm2.shape)

dm2 = (
    dm2.fillna("").drop_duplicates(subset=["Attribute"]).reset_index(drop=True)
)  # 'DependsOn', 'Properties',

display(dm2.shape)

# # Add ADKP attrs to dm

df = pd.read_csv(
    "https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv"
)

# preprocess AD data model to remove duplicates
df = df.sort_values(by=["Attribute", "Valid Values"]).reset_index(drop=True)
df = df.drop_duplicates(keep="first", subset=["Attribute"])

df.loc[
    df.query('Attribute.str.contains("template")',
             engine="python").index.tolist(),
    "Properties",
] = "template"

attrs_interest = [
    "analysisType",
    "analysisType",
    "analytical covariates",
    "assay",
    "assay",
    "biospecimen",
    "consortium",
    "data dictionary",
    "dataSubtype",
    "dataType",
    "fileFormat",
    "grant",
    "ID mapping",
    "individual",
    "isConsortiumAnalysis",
    "isModelSystem",
    "isMultiSpecimen",
    "libraryPrep",
    "libraryType",
    "manifest",
    "manifest",
    "metadata",
    "metadataType",
    "modelSystemName",
    "modelSystemType",
    "platform",
    "project",
    "protocol",
    "protocol",
    "resourceType",
    "type",
]

metadataTypes = [
    "analytical covariates",
    "assay",
    "biospecimen",
    "data dictionary",
    "ID mapping",
    "individual",
    "manifest",
    "protocol",
]

df_new_attrs = df.query("Attribute in @attrs_interest").copy()

df_new_attrs["Properties"] = "BaseAnnotation"

# Cleanup data model attributes to fit ELITE data model
df_new_attrs = rewrite_df_value(
    df_new_attrs, "Attribute", "study", "Valid Values", "LLFS,ILO,LG,LC"
)

df_new_attrs = rewrite_df_value(
    df_new_attrs, "Attribute", "consortium", "Valid Values", "ELITE"
)

df_new_attrs = rewrite_df_value(
    df_new_attrs,
    "Attribute",
    "metadataType",
    "Valid Values",
    "analytical covariates, assay, biospecimen, data dictionary, ID mapping, individual, manifest, protocol",
)

# recode Parent
recoder = {
    "metadataType": "MetadataType",
    "dataProperty": "DataProperty",
    "dataType": "DataType",
    "dataSubtype": "DataSubtype",
}

df_new_attrs = df_new_attrs.replace(recoder)

# Rename Columns

df_new_attrs = df_new_attrs.rename(
    columns={"Parent": "Properties", "Properties": "Parent"}
)

# Merge new attributes with existiing data model
dm_new = pd.concat([dm2, df_new_attrs])

dm_new.drop(columns="columnType", inplace=True)

print(f"Duplicates: {sum(dm_new.duplicated(subset="Attribute"))}")
# dm_new[dm_new.duplicated(subset="Attribute", keep=False)]

dm_new.sample(5)
dm_new["Validation Rules"] = dm_new["Validation Rules"].replace(
    "regex search ([0-9]+),regex search ([0-9]+\\.[0-9]*.)|([0-9]+)",
    "regex search ([0-9]+\\.[0-9]*.)|([0-9]+)",
)
dm_new[
    dm_new["Validation Rules"]
    == "regex search ([0-9]+),regex search ([0-9]+\\.[0-9]*.)|([0-9]+)"
]

# recode Parent
recoder = {
    "metadataType": "MetadataType",
    "dataProperty": "DataProperty",
    "dataType": "DataType",
    "dataSubtype": "DataSubtype",
}

dm_new = dm_new.replace(recoder)

# drop duplicates
print(dm_new.shape)

dm_new = dm_new.drop_duplicates(subset=["Attribute"], keep="first")

print(dm_new.shape)

# Fill in blanks with unspecified to update later and categorize for site
dm_new[["Parent", "Properties", "Type"]] = dm_new[
    ["Parent", "Properties", "Type"]
].fillna("unspecified")

dm_new["Required"] = dm_new["Required"].fillna("False")

# clean up template depends on
dm_new["DependsOn"] = (
    dm_new["DependsOn"].fillna("").apply(clean_list).replace("", np.nan)
)

remove_values = ["False", "Not applicable", "Not collected", "Unknown", "Other"]

dm_new.loc[dm_new["Parent"] == "Template", "DependsOn"] = dm_new.loc[
    dm_new["Parent"] == "Template", "DependsOn"
].apply(lambda x: ",".join([y for y in x.split(",") if y not in remove_values]))

# # Pull Valid Values



# # Hard Coded Attributes Fixed

# add study name attribute
# Later get from synapse
new_attribute = {
    "Attribute": ["studyName"],
    "Description": [
        "Name of studies found in project. Values include: MRGWAS,ELPSCRNA,Aging-PheWAS,Organoid scRNAseq"
    ],
    "Valid Values": [np.nan],
    "DependsOn": [np.nan],
    "Properties": [np.nan],
    "Required": [np.nan],
    "Parent": ["validValues"],
    "DependsOn Component": [np.nan],
    "Source": [np.nan],
    "Validation Rules": ["str"],
    "Module": [np.nan],
    "Type": [np.nan],
    "Ontology": [np.nan],
}

dm = pd.concat([dm, pd.DataFrame.from_dict(new_attribute)])

atrs_to_fix = [
    "sequencingBatchID",  # needs to accept numerical values
    "libraryVersion",  # needs to accept numerical values
]
vv = ""
vr = "regex search ^[0-9]+|(Unknown)|(Not collected)|(Not applicable)|(Not Specified)"
for a in atrs_to_fix:
    fix_index = dm_elite.query("Attribute == @a").index[0]
    dm_elite.loc[fix_index, "Valid Values"] = vv
    dm_elite.loc[dm_elite.query("Attribute == @a").index[0], "Validation Rules"] = vr

# # Update Attributes with Synapse Data

syn = synapse_login.main()

# Pull grant information
grants = syn.tableQuery("SELECT * FROM syn51209786").asDataFrame()["grantNumber"]

grantIds = []
for i in grants:
    grantIds += i

grantIds = ",".join([i.strip() for i in grantIds])

dm.loc[
    dm["Attribute"].str.contains("grant", flags=re.IGNORECASE), "Valid Values"
] = grantIds

# # Write Out Data Model

dm_new["Type"] = dm_new["Type"].str.upper()

dm_new = dm_new.reset_index(drop=True)
dm_new.to_csv("../" + csv_model, index=False)

# # Convert Data Model

# Convert CSV to JSON LD
print(f'schematic schema convert {"../" + csv_model} --output_jsonld {json_model}')

!schematic schema convert {"../" + csv_model} --output_jsonld {"../" + json_model}


