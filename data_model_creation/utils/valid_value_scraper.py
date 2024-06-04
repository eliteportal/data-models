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


def iri_request(base_url, iri):
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


def purl_main(base_url, iri):
    response = iri_request(base_url, iri)
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
