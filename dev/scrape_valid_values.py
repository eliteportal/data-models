import pandas as pd
import numpy as np

import urllib
import re
import requests
from tqdm import tqdm
from requests.exceptions import HTTPError

from utils import utils

# Functions


def join_strings(string):
    # Clean list columns into single string
    try:
        return ",".join(string)
    except Exception:
        return ""


def sort_lists(list):
    try:
        return ",".join(sorted(np.unique(list)))
    except Exception:
        return list


# parse url into api call
def url_to_api_call(url):
    url = url.replace("ols4", "ols4/api")

    test = urllib.parse.urlparse(url)

    url_parts = list(urllib.parse.urlparse(url))

    iri = urllib.parse.parse_qs(test.query)["iri"][0]

    new_iri = urllib.parse.quote_plus(urllib.parse.quote_plus(iri))

    url_parts[2] = url_parts[2].replace("classes", "terms")

    url_parts[2] = "/".join([url_parts[2], new_iri])

    url_parts[4] = ""

    new_url = urllib.parse.urlunparse(url_parts)

    return new_url


def get_response(u, params=None):
    """_summary_

    Args:
        u (_type_): _description_
        params (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    try:
        response = requests.get(u, params=params)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6
    else:
        print(response)
        return response


def simplify_response(response):
    """Get the terms from the response. Helps to simplify parsing the json"""

    j = response.json()["_embedded"]["terms"]

    if len(j) == 1:
        return j[0]
    else:
        print(f"Response has {len(j)} terms")
        return j


def iri_request(iri):
    """Get call to iri site"""
    response = get_response(base_url, params={"iri": iri})

    return response


def get_iri(url):
    """Extract iri from url"""
    test = urllib.parse.urlparse(url)

    params = urllib.parse.parse_qs(test.query)

    iri = params["iri"][0]

    return iri


def find_defining_ontology(terms):
    """look for defining ontology"""
    if len(terms) > 1:
        for t in terms:
            if t["is_defining_ontology"]:
                return t
            else:
                pass
    elif len(terms) == 1:
        return terms[0]
    else:
        return None


# term = find_defining_ontology(terms)
# term.


def get_all_terms(url, json_response):
    """get all terms from pages"""
    pages = json_response["page"]["totalPages"]
    size = json_response["page"]["size"]

    # get the original link
    # url = json_response['_links']['self']['href']

    terms_list = []

    for i in tqdm(range(pages)):
        response = requests.get(url, params={"page": i, "size": size})

        temp_d = response.json()

        for term in temp_d["_embedded"]["terms"]:
            terms_list.append(term)

    print("Length of terms: ", len(terms_list), sep="\t")

    return terms_list


# terms_list = get_all_terms(url, json_response)
def get_labels_from_terms_list(terms_list):
    vv = []

    for t in terms_list:
        # if t['has_children'] == False:
        vv.append(t)

    labels = []

    for i in vv:
        labels.append(i["label"])

    labels = sorted(np.unique(labels))

    return labels


def purl_main(iri):
    response = iri_request(iri)
    json_response = response.json()
    terms = json_response["_embedded"]["terms"]
    term = find_defining_ontology(terms)

    # get descendants
    url = term["_links"]["hierarchicalDescendants"]["href"]
    d = get_response(url)
    json_response = d.json()

    terms_list = get_all_terms(url, json_response)

    valid_values = get_labels_from_terms_list(terms_list)

    return valid_values


# to use for searching ols4 for terms
base_url = "http://www.ebi.ac.uk/ols4/api/terms"

validation_coder = {
    "number": "regex search ([0-9]+\.[0-9]*.?)|([0-9]+)",
    "integer": "regex search ([0-9]+)",
    "string": "",
}

other_vvs = ["Other", "Unknown", "Not Available", "Not Given"]

# # Pull in current data model
dm = utils.load_and_backup_dm("../EL.data.model.csv", output_dir="../backups")

# these ontologies are too large
indexes = dm[
    dm["Source"].str.contains(
        "https://www.ebi.ac.uk/ols4/ontologies/mondo|https://www.ebi.ac.uk/ols4/ontologies/maxo|https://www.ebi.ac.uk/ols4/ontologies/hp",
        regex=True,
        na=False,
    )
].index.tolist()

dm.loc[indexes, "Valid Values"] = np.nan
dm.loc[indexes, "Description"] = (
    dm.loc[indexes, "Description"] + " Please see the source ontology."
)
dm.loc[indexes, "Validation Rules"] = "str"

dm.loc[dm["Properties"] == "Valid Value", "Validation Rules"] = np.nan

dm["Required"] = dm["Required"].replace("False,True", "True")

dm["Source"] = dm["Source"].replace(
    "https://ontobee.org/ontology/NCITiri=http://purl.obolibrary.org/obo/NCIT_C62690https://www.ebi.ac.uk/ols4/ontologies/edam/terms?iri=http%3A%2F%2Fedamontology.org%2Fdata_1045",
    "https://ontobee.org/ontology/NCITiri=http://purl.obolibrary.org/obo/NCIT_C62690, https://www.ebi.ac.uk/ols4/ontologies/edam/terms?iri=http%3A%2F%2Fedamontology.org%2Fdata_1045",
)

dm = dm.replace("-The%20life%20stage", "", regex=True)

# Attributes with ontologies
dm_test = dm[
    (
        dm["Source"]
        .fillna("")
        .str.contains("http", regex=True, flags=re.IGNORECASE, na=False)
    )
    & (dm["Source"].str.contains("purl|ebi", regex=True, na=False))
    & (
        dm["Valid Values"].str.contains(
            "not", flags=re.IGNORECASE, regex=True, na=False
        )
    )
].reset_index(drop=True)

dm_test["Source"] = dm_test["Source"].str.replace("ols", "ols4", regex=True)
dm_test["Source"] = dm_test["Source"].str.replace("terms", "terms?", regex=True)

dm_test["Valid Values"] = dm_test["Valid Values"].str.split(",")

with pd.option_context("display.max_colwidth", None):
    display(dm_test)

# # OLS
#
# https://www.ebi.ac.uk/ols4/help
# replace ols with ols4
# Start extraction

# {
#     # could replace with this link to get higher level terms
#     "https://www.ebi.ac.uk/ols4/ontologies/maxo": "http://purl.obolibrary.org/obo/MONDO_0700096"
# }

dm_test["purl"] = (
    dm_test["Source"]
    .str.split(",")
    .apply(
        lambda x: sorted(np.unique([y for y in x if bool(re.search("ebi|purl", y))]))
    )
)


dm.query('Attribute.str.contains("diagnosis")', engine="python")

# ## Main extraction
#

dm_test["extraction_status"] = ""

errors = []

for i, v in dm_test.iterrows():
    storage = dm_test.loc[i, "Valid Values"]
    for url in v["purl"]:
        print(url)
        # for world countries
        if dm_test.at[i, "extraction_status"] == "done":
            next
        else:
            if (
                url
                == "https://wits.worldbank.org/countryprofile/metadata/en/country/all"
            ):
                x = pd.read_excel(
                    io="http://wits.worldbank.org/data/public/WITSCountryProfile-Country_Indicator_ProductMetada-en.xlsx",
                    sheet_name="Country-Metadata",
                )

                dm_test.at[i, "Valid Values"] = sorted(
                    storage + x["Country Code"].tolist()
                )

                dm_test.at[i, "extraction_status"] = "done"

            elif "terms" in url and "ebi.ac.uk" in url:
                url = url_to_api_call(url)

                result = get_response(url)

                try:
                    json_result = result.json()

                    url_descendents = json_result["_links"]["hierarchicalDescendants"][
                        "href"
                    ]

                    json_result = get_response(url_descendents).json()

                    terms_list = get_all_terms(url_descendents, json_result)

                    result = get_labels_from_terms_list(terms_list)

                    dm_test.at[i, "Valid Values"] = sorted(storage + result)

                    dm_test.at[i, "extraction_status"] = "done"

                except Exception as e:
                    dm_test.at[i, "extraction_status"] = "error"
                    print(e)
                    next

            elif "http://purl" in url:
                try:
                    result = purl_main(url)

                    dm_test.at[i, "Valid Values"] = sorted(storage + result)

                    dm_test.at[i, "extraction_status"] = "done"
                except Exception as e:
                    print(e)

            else:
                dm_test.at[i, "extraction_status"] = "error"
                print("Error")
                errors.append(url)

        print("-" * 20)

dm_test["Valid Values"] = (
    dm_test["Valid Values"].apply(lambda x: ",".join(x)).apply(utils.clean_list)
)

# Update attributes
no_vvs = ["diagnosis", "extractionMethod", "taxon", "commonName"]
dm_test.loc[dm_test["Attribute"].isin(no_vvs), "Valid Values"] = np.nan

# drop extra columns
dm_test = dm_test.drop(columns=["purl", "extraction_status"])

# join new valid values df with current dm
replacements = dm_test.set_index("Attribute").to_dict()

for k, v in replacements.items():
    for a, av in v.items():
        dm.loc[dm["Attribute"] == a, k] = av

dm.loc[dm["Attribute"].isin(dm_test["Attribute"])]

dm = dm.replace("-The%20life%20stage", "", regex=True)

dm[["Valid Values", "Source", "Ontology"]] = (
    dm[["Valid Values", "Source", "Ontology"]]
    .fillna("")
    .applymap(utils.clean_list)
    .replace("", np.nan)
)

# # Update data model

print("Duplicates: {}".format(sum(dm.duplicated(subset="Attribute"))))

# write out new data model
dm.to_csv("../EL.data.model.csv")
